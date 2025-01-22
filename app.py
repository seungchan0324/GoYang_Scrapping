import json
from datetime import date, timedelta
import asyncio
import sys
import os
import streamlit as st
from main import Main
from file_name import File_Name_Selector

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 프로젝트 루트 경로를 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="HRD 훈련과정 검색",
    page_icon="🔍",
)

st.markdown(
    """
### HRD 훈련과정 검색
"""
)

# 세션 상태 초기화
if "location_checked" not in st.session_state:
    st.session_state["location_checked"] = []
if "train_checked" not in st.session_state:
    st.session_state["train_checked"] = []
if "location" not in st.session_state:
    st.session_state["location"] = False
if "training" not in st.session_state:
    st.session_state["training"] = False
if "search_started" not in st.session_state:
    st.session_state.search_started = False
if "log" not in st.session_state:
    st.session_state.log = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None
if "start_date" not in st.session_state:
    st.session_state.start_date = date.today()
if "end_date" not in st.session_state:
    st.session_state.end_date = date.today() + timedelta(days=365)
if "param" not in st.session_state:
    st.session_state.param = {}
if "keyword" not in st.session_state:
    st.session_state.keyword = None

# 클래스 초기화
main = Main()
file_name_selector = File_Name_Selector()

with open("./json/location_type.json", "r", encoding="UTF-8") as f:
    location_json = json.load(f)

with open("./json/training_type.json", "r", encoding="UTF-8") as f:
    training_json = json.load(f)


def update_status(message):
    st.session_state.log = message
    log_display.info(message)


def search_state():
    st.session_state.search_started = not st.session_state.search_started


def start_crawling(start_date, end_date, location_data, training_data, keyword):
    start_date_picker = (str(start_date)).replace("-", "")
    end_date_picker = (str(end_date)).replace("-", "")
    file_name = file_name_selector.select(
        location_data, training_data, start_date_picker, end_date_picker, keyword
    )
    st.session_state.file_name = file_name
    file_name_display.info(f"{file_name}.csv")
    main.start_crawling(
        start_date, end_date, location_data, training_data, keyword, update_status
    )
    search_state()
    st.experimental_rerun()


def toggle_checkbox(state_key, key_name, key_code):
    if "전체" in key_name:
        if key_code in st.session_state[state_key]:
            st.session_state[state_key] = []
        else:
            st.session_state[state_key] = [key_code]
    else:
        if "A%7C전체" in st.session_state[state_key]:
            st.session_state[state_key].remove("A%7C전체")
        elif "11%7C서울+전체" in st.session_state["location_checked"]:
            st.session_state[state_key].remove("11%7C서울+전체")
        if key_code in st.session_state[state_key]:
            st.session_state[state_key].remove(key_code)
        else:
            st.session_state[state_key].append(key_code)


def location_reset(types):
    st.session_state[types] = []


def button_toggle(str):
    st.session_state[str] = not st.session_state[str]


file_name_display = st.empty()
log_display = st.empty()
keyword_container = st.container()
location_container = st.container()
location_checkbox_container = st.container()
date_container = st.container()
training_container = st.container()
training_checkbox_container = st.container()
search_container = st.container()

if not st.session_state.search_started:

    with keyword_container:
        st.session_state.keyword = st.text_input("검색어를 입력하시오.")

    with location_container:

        st.button("지역선택", on_click=button_toggle, args=("location",))

    if st.session_state["location"]:

        with location_checkbox_container:

            columns_per_row = 5
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
                        on_change=toggle_checkbox,
                        disabled=disabled,
                        args=("location_checked", loc_name, loc_code),
                    )

            if len(st.session_state["location_checked"]) == 5:
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.write("6개 이상 선택은 안 됩니다.")
                with col2:
                    st.button(
                        "Reset", on_click=location_reset, args=("location_checked",)
                    )

            st.write("\n")

    with date_container:
        start_input, end_input = st.columns(2)
        with start_input:
            st.session_state.start_date = st.date_input(
                "시작날짜", value=st.session_state.start_date
            )
        with end_input:
            st.session_state.end_date = st.date_input(
                "끝 날짜", value=st.session_state.end_date
            )

        st.session_state.param["start_date"] = st.session_state.start_date
        st.session_state.param["end_date"] = st.session_state.end_date

        st.write("\n")

    with training_container:

        st.button("훈련유형 선택", on_click=button_toggle, args=("training",))

    with training_checkbox_container:

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
                        on_change=toggle_checkbox,
                        args=("train_checked", train_type, train_code),
                    )

            if len(st.session_state["train_checked"]) > 1:
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.write("많은 선택은 과부화를 부릅니다.")
                with col2:
                    st.button("Reset", on_click=location_reset, args=("train_checked",))

            st.write("\n")

    with search_container:

        search = True
        search = (
            len(st.session_state["train_checked"]) == 0
            or len(st.session_state["location_checked"]) == 0
        )
        st.session_state.param["location_data"] = "%C2".join(
            st.session_state["location_checked"]
        )
        st.session_state.param["training_data"] = "%C2".join(
            st.session_state["train_checked"]
        )
        col1, col2 = st.columns([5, 1])
        with col1:
            log_display = st.empty()
        with col2:
            st.button("검색 시작", disabled=search, on_click=search_state)

else:
    keyword_container.empty()
    date_container.empty()
    search_container.empty()
    location_container.empty()
    location_checkbox_container.empty()
    training_container.empty()
    training_checkbox_container.empty()

    keyword = st.session_state.keyword
    start_date = st.session_state.param["start_date"]
    end_date = st.session_state.param["end_date"]
    location_data = st.session_state.param["location_data"]
    training_data = st.session_state.param["training_data"]
    start_crawling(start_date, end_date, location_data, training_data, keyword)


with st.sidebar:
    files_path = "./files"
    file_list = os.listdir(files_path)
    st.header("현재 CSV 파일 리스트")
    if not file_list:
        st.warning("CSV 파일이 없습니다.")
    else:
        for file in file_list:
            st.write(file)
