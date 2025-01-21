import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="상세 페이지", layout="wide")

if "selected_file" not in st.session_state:
    st.session_state.selected_file = None
if "select_menu" not in st.session_state:
    st.session_state["select_menu"] = False


def button_toggle(types):
    st.session_state[types] = not st.session_state[types]


def select_file(file):
    st.session_state.selected_file = file
    st.session_state["select_menu"] = False


df = None
filtered_df = None
search_value = None
directory = "files"
csv_files = [f for f in os.listdir(directory) if f.endswith(".csv")]

if st.session_state.selected_file:
    file_path = os.path.join(directory, st.session_state.selected_file)
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")

with st.sidebar:
    st.button("CSV 파일 선택", on_click=button_toggle, args=("select_menu",))
    if st.session_state["select_menu"]:
        search_query = st.sidebar.text_input("파일명 검색")
        filtered_files = [f for f in csv_files if search_query.lower() in f.lower()]

        for csv_file in filtered_files:
            st.button(csv_file, on_click=select_file, args=(csv_file,))

    if st.session_state.selected_file:
        search_column = st.selectbox("검색할 열 선택", df.columns)
        search_value = st.text_input("검색어 입력")

if st.session_state.selected_file:
    st.header(f"{st.session_state.selected_file}")
    if search_value:
        filtered_df = df[
            df[search_column].astype(str).str.contains(search_value, na=False)
        ]
        st.subheader(f"'{search_column}'에서 '{search_value}' 검색 결과")
        st.dataframe(filtered_df)
        st.download_button(
            label="필터링 된 CSV 다운로드",
            data=filtered_df.to_csv(index=False),
            file_name=st.session_state.selected_file,
            mime="text/csv",
        )
        st.bar_chart(filtered_df["종강 6개월 기준 취업률"])
    else:
        st.dataframe(df)

        st.download_button(
            label="CSV 다운로드",
            data=df.to_csv(index=False),
            file_name=st.session_state.selected_file,
            mime="text/csv",
        )
else:
    st.info("왼쪽에서 CSV 파일 선택을 누르신 후에 파일을 하나 지정해 주십시오.")
