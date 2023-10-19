from typing import Tuple
from datetime import datetime

import duckdb
import pandas as pd
import streamlit as st
from streamlit.elements.widgets.time_widgets import DateWidgetReturn
from pygwalker.api.streamlit import init_streamlit_comm, StreamlitRenderer, PreFilter

st.set_page_config(
    page_title="Streamlit Twitter Demo",
    layout="wide"
)

st.title("Streamlit Twitter Demo")

# Initialize pygwalker communication
init_streamlit_comm()

@st.cache_data
def get_twitter_df() -> "pd.DataFrame":
    df = pd.read_json(st.secrets["DATA_URL"])
    return df[list(set(df.columns) - {"edit_controls", "public_metrics", "referenced_tweets", "context_annotations"})]

# When using `use_kernel_calc=True`, you should cache your pygwalker renderer, if you don't want your memory to explode
@st.cache_resource
def get_pyg_renderer() -> "StreamlitRenderer":
    df = get_twitter_df()
    # When you need to publish your application, you need set `debug=False`,prevent other users to write your config file.
    return StreamlitRenderer(df, spec="./twitter_gw_config.json", debug=False)


renderer = get_pyg_renderer()

# display explore ui
# renderer.render_explore()


def display_metrics_gather(start_date: "DateWidgetReturn", end_date: "DateWidgetReturn"):
    df = get_twitter_df()
    metrics = duckdb.query(f"""
        SELECT
            COUNT(1) twiiters_count,
            SUM(impression_count) impression_count,
            SUM(like_count) like_count,
            SUM(retweet_count) retweet_count,
            SUM(reply_count) reply_count,
            SUM(quote_count) quote_count,
            SUM(bookmark_count) bookmark_count
        FROM
            df
        WHERE
            created_at BETWEEN '{start_date.strftime("%Y-%m-%d")}' AND '{end_date.strftime("%Y-%m-%d")}'
    """).fetchone()
    metrics_cols = st.columns(7)
    metrics_names = [
        "twiiters_count", "impression_count", "like_count", "retweet_count",
        "reply_count", "quote_count", "bookmark_count"
    ]
    for metrics_col, metrics_name, metrics_value in zip(metrics_cols, metrics_names, metrics):
        metrics_col.metric(metrics_name, metrics_value)

    renderer.render_pure_chart(10)    


def display_date_picker() -> Tuple["DateWidgetReturn", "DateWidgetReturn"]:
    default_end_date = datetime(2023, 10, 19)
    default_start_date = datetime(2023, 8, 19)
    col1, col2, _ = st.columns([1, 1, 6])
    with col1:
        start_date = st.date_input("start time: ", default_start_date.date())
    with col2:
        end_date = st.date_input("end time: ", default_end_date.date())

    return start_date, end_date


def display_metrics_charts():
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "tweets", "impression", "retweet", "like",
        "reply", "quote", "bookmark"
    ])

    with tab1:
        renderer.render_pure_chart(0)

    with tab2:
        renderer.render_pure_chart(1)

    with tab3:
        renderer.render_pure_chart(2)

    with tab4:
        renderer.render_pure_chart(3)

    with tab5:
        renderer.render_pure_chart(4)

    with tab6:
        renderer.render_pure_chart(5)

    with tab7:
        renderer.render_pure_chart(6)


def display_most_engaging():
    option = st.selectbox(
        "select time type",
        ('dayily', 'weekly', 'monthly'),
    )
    option_chart_index = {
        "dayily": 7,
        "weekly": 8,
        "monthly": 9
    }
    renderer.render_pure_chart(option_chart_index.get(option, 7))


pre_filters = []
start_date, end_date = display_date_picker()
pre_filters.append(PreFilter(
    field="created_at",
    op="temporal range",
    value=[str(start_date), str(end_date)]
))

renderer.set_global_pre_filters(pre_filters)

st.subheader("metrics gather")
display_metrics_gather(start_date, end_date)

st.subheader("metrics by day")
display_metrics_charts()

st.subheader("most engaging time")
display_most_engaging()
