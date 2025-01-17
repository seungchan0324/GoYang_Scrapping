import json
import streamlit as st

with open("location_type.json", "r", encoding="UTF-8") as f:
    location_json = json.load(f)

with open("training_type.json", "r", encoding="UTF-8") as f:
    training_json = json.load(f)

if "selected" not in st.session_state:
    st.session_state["selected"] = []


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


if len(st.session_state["selected"]) == 5:
    st.write("5개 이상 선택이 안 됩니다.")


for location in location_json:
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

    st.checkbox(
        loc_name,
        checked,
        key=loc_code,
        on_change=toggle_checkbox,
        disabled=disabled,
        args=(loc_name, loc_code),
    )
