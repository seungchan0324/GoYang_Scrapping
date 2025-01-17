import json
import streamlit as st
from datetime import date, timedelta

if "selected" not in st.session_state:
    st.session_state["selected"] = []

if "location" not in st.session_state:
    st.session_state["location"] = False


with open("location_type.json", "r", encoding="UTF-8") as f:
    location_json = json.load(f)

with open("training_type.json", "r", encoding="UTF-8") as f:
    training_json = json.load(f)


def toggle_checkbox(loc_name, loc_code):

    if loc_name == "서울 전체":
        if loc_code in st.session_state["selected"]:
            st.session_state["selected"] = []
        else:
            st.session_state["selected"] = [loc_code]
    else:
        if loc_code in st.session_state["selected"]:
            st.session_state["selected"].remove(loc_code)
        else:
            st.session_state["selected"].append(loc_code)


def location_button_toggle():
    st.session_state["location"] = not st.session_state["location"]


def location_reset():
    st.session_state["selected"] = []


st.button("지역정보", on_click=location_button_toggle)

if st.session_state["location"]:

    columns_per_row = 4
    columns = st.columns(columns_per_row)

    for idx, location in enumerate(location_json):
        loc_name = location["location"]
        loc_code = location["location_code"]

        checked = loc_code in st.session_state["selected"]

        is_max_selected = len(st.session_state["selected"]) == 5
        not_seoul = loc_name != "서울 전체"

        if "11%7C서울+전체" in st.session_state["selected"]:
            disabled = not_seoul
        else:
            disabled = len(st.session_state["selected"]) == 5 and (
                not checked and not_seoul
            )

        with columns[idx % columns_per_row]:
            st.checkbox(
                loc_name,
                checked,
                key=loc_code,
                on_change=toggle_checkbox,
                disabled=disabled,
                args=(loc_name, loc_code),
            )

    if len(st.session_state["selected"]) == 5:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.write("6개 이상 선택은 안 됩니다.")
        with col2:
            st.button("Reset", on_click=location_reset)
# ef3psqc11

st.write("\n")

one_years_ago = date.today() + timedelta(days=365)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작날짜")
with col2:
    end_date = st.date_input("끝 날짜", one_years_ago)
