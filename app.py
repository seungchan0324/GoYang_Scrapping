import json
import streamlit as st
from datetime import date, timedelta
from main import Main
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.set_page_config(
    page_title="HRD 훈련과정 검색",
    page_icon="🔍",
)

st.markdown(
    """
### HRD 훈련과정 검색
"""
)

if "location_checked" not in st.session_state:
    st.session_state["location_checked"] = []

if "train_checked" not in st.session_state:
    st.session_state["train_checked"] = []

if "location" not in st.session_state:
    st.session_state["location"] = False

if "training" not in st.session_state:
    st.session_state["training"] = False


with open("location_type.json", "r", encoding="UTF-8") as f:
    location_json = json.load(f)

with open("training_type.json", "r", encoding="UTF-8") as f:
    training_json = json.load(f)


def start_crawling():
    main = Main()
    location_data = "%C2".join(st.session_state["location_checked"])
    training_data = "%C2".join(st.session_state["train_checked"])
    main.start_crawling(start_date, end_date, location_data, training_data)


def location_toggle_checkbox(loc_name, loc_code):

    if loc_name == "서울 전체":
        if loc_code in st.session_state["location_checked"]:
            st.session_state["location_checked"] = []
        else:
            st.session_state["location_checked"] = [loc_code]
    else:
        if "11%7C서울+전체" in st.session_state["location_checked"]:
            st.session_state["location_checked"].remove("11%7C서울+전체")
        if loc_code in st.session_state["location_checked"]:
            st.session_state["location_checked"].remove(loc_code)
        else:
            st.session_state["location_checked"].append(loc_code)


def train_toggle_checkbox(train_type, train_code):

    if train_type == "전체":
        if train_code in st.session_state["train_checked"]:
            st.session_state["train_checked"] = []
        else:
            st.session_state["train_checked"] = [train_code]
    else:
        if "A%7C전체" in st.session_state["train_checked"]:
            st.session_state["train_checked"].remove("A%7C전체")
        if train_code in st.session_state["train_checked"]:
            st.session_state["train_checked"].remove(train_code)
        else:
            st.session_state["train_checked"].append(train_code)


def button_toggle(types):
    st.session_state[types] = not st.session_state[types]


def location_reset(types):
    st.session_state[types] = []


st.button("지역선택", on_click=button_toggle, args=("location",))

if st.session_state["location"]:

    columns_per_row = 4
    columns = st.columns(columns_per_row)

    for idx, location in enumerate(location_json):
        loc_name = location["location"]
        loc_code = location["location_code"]

        checked = loc_code in st.session_state["location_checked"]

        is_max_location_checked = len(st.session_state["location_checked"]) == 5
        not_seoul = loc_name != "서울 전체"

        if "11%7C서울+전체" not in st.session_state["location_checked"]:
            disabled = len(st.session_state["location_checked"]) == 5 and (
                not checked and not_seoul
            )
        else:
            disabled = False

        with columns[idx % columns_per_row]:
            st.checkbox(
                loc_name,
                checked,
                key=loc_code,
                on_change=location_toggle_checkbox,
                disabled=disabled,
                args=(loc_name, loc_code),
            )

    if len(st.session_state["location_checked"]) == 5:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.write("6개 이상 선택은 안 됩니다.")
        with col2:
            st.button("Reset", on_click=location_reset, args=("location_checked",))
# ef3psqc11

st.write("\n")

one_years_ago = date.today() + timedelta(days=365)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작날짜")
with col2:
    end_date = st.date_input("끝 날짜", one_years_ago)

st.write("\n")

st.button("훈련유형 선택", on_click=button_toggle, args=("training",))

if st.session_state["training"]:

    columns_per_row = 3
    columns = st.columns(columns_per_row)

    for idx, train in enumerate(training_json):
        train_type = train["training_type"]
        train_code = train["training_code"]

        checked = train_code in st.session_state["train_checked"]

        with columns[idx % columns_per_row]:
            st.checkbox(
                train_type,
                checked,
                key=train_code,
                on_change=train_toggle_checkbox,
                args=(train_type, train_code),
            )

    if len(st.session_state["train_checked"]) > 1:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.write("많은 선택은 과부하를 부릅니다.")
        with col2:
            st.button("Reset", on_click=location_reset, args=("train_checked",))

st.write("\n")

search = True
search = (
    len(st.session_state["train_checked"]) == 0
    or len(st.session_state["location_checked"]) == 0
)
col1, col2 = st.columns([5, 1])
with col1:
    st.write("")
with col2:
    st.button("검색 시작", disabled=search, on_click=start_crawling)
