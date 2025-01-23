import streamlit as st
import pandas as pd
import plotly.express as px
from collections import defaultdict
import os

custom_css = """
<style>
/*sticky 적용*/
table td:nth-child(2){
  position: -webkit-sticky;
  position: sticky; 
  background-color: white;
  left: 0;
  z-index: 99;
}
</style>
"""

st.set_page_config(page_title="상세 페이지", page_icon="📑", layout="wide")

st.markdown(custom_css, unsafe_allow_html=True)

if "selected_file" not in st.session_state:
    st.session_state.selected_file = None
if "filters" not in st.session_state:
    st.session_state.filters = []


def select_file(file):
    st.session_state.selected_file = file
    st.session_state.filters = []  # 파일을 변경하면 기존 필터 초기화


def add_filter():
    st.session_state.filters.append({"column": None})


def remove_filter(index):
    if 0 <= index < len(st.session_state.filters):
        st.session_state.filters.pop(index)


def delete_file(path):
    st.session_state.selected_file = None
    st.session_state.filters = []
    os.remove(path)


# 차트 생성
def create_chart(df):
    # 색상 데이터 추가
    df["색상"] = df["기관명"].apply(
        lambda x: "솔데스크" if x == "(주)솔데스크" else "기타"
    )

    # customdata에 툴팁 데이터를 원하는 순서로 삽입
    df["custom_hover"] = (
        "기관명: "
        + df["기관명"].astype(str)
        + "<br>"
        + "과정명: "
        + df["과정명"].astype(str)
        + "<br>"
        + "취업률: "
        + df["6개월후_취업률"].astype(str)
        + "<br>"
    )

    # Plotly 차트 생성
    st.subheader("취업률 기준 차트")
    fig = px.scatter(
        df,
        y="6개월후_취업률",  # 세로축
        x="개강일",  # 가로축
        color="색상",  # 색상 조건 지정
        color_discrete_map={  # 색상 매핑
            "솔데스크": "red",
            "기타": "lightblue",
        },
        labels={
            "6개월후_취업률": "취업률(%)",
            "개강일": "개강일",
            "기관명": "기관명",
            "과정명": "과정명",
        },
    )

    # 툴팁 커스터마이징
    fig.update_traces(
        hovertemplate="%{customdata}<extra></extra>",  # customdata를 툴팁으로 사용
        customdata=df["custom_hover"],  # customdata로 지정
    )

    # 레이아웃 업데이트
    fig.update_layout(
        xaxis_title="개강일",
        yaxis_title="취업률(%)",
        title="6개월 후 취업률과 개강일 기준 차트",
        title_x=0.5,
        template="plotly_white",
    )

    st.plotly_chart(fig, use_container_width=True)


def create_average_dataframe(df):
    st.subheader("기업별 평균 취업률")
    average_employment_df = (
        df.groupby(["기관명", "직종"])
        .agg(
            평균취업률=("6개월후_취업률", "mean"),  # 평균 취업률
            과정_진행_횟수=("회차", "count"),  # 회차 수 계산
        )
        .reset_index()
    )
    average_employment_df["평균취업률"] = average_employment_df["평균취업률"].round(2)
    average_employment_df = average_employment_df.sort_values(
        by="평균취업률", ascending=False
    )
    average_employment_df.set_index("기관명", inplace=True)
    st.dataframe(average_employment_df, width=1000)


directory = "files"
csv_files = [f for f in os.listdir(directory) if f.endswith(".csv")]
columns_to_convert = [
    "모집인원",
    "수강신청인원",
    "수강확정인원",
    "수료인원",
    "평균 인원",
    "전회차 인원",
    "6개월후_취업률",
    "만족도_평균점수",
    "만족도_응답자수",
]
if st.session_state.selected_file:
    file_path = os.path.join(directory, st.session_state.selected_file)
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        df = None

    for column in columns_to_convert:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")


else:
    df = None

with st.sidebar:
    st.header("파일 및 필터 관리")
    st.subheader("CSV 파일 선택")
    for csv_file in csv_files:
        st.button(csv_file, on_click=select_file, args=(csv_file,))

    if st.session_state.selected_file and df is not None:
        st.subheader("필터 추가 및 설정")
        if st.button("필터 추가"):
            add_filter()

        for i, filter_item in enumerate(st.session_state.filters):
            cols = st.columns([3, 3, 1])  # 열: 선택박스, 값 입력, 삭제 버튼
            with cols[0]:
                st.session_state.filters[i]["column"] = st.selectbox(
                    "열 선택",
                    df.columns,
                    key=f"filter-column-{i}",
                    index=(
                        0
                        if not st.session_state.filters[i].get("column")
                        else list(df.columns).index(
                            st.session_state.filters[i]["column"]
                        )
                    ),
                )

            selected_column = st.session_state.filters[i]["column"]
            with cols[1]:
                if selected_column in ["개강일", "종강일"]:
                    # 날짜 범위 필터
                    st.session_state.filters[i]["start_date"] = st.date_input(
                        "시작일",
                        value=pd.to_datetime(
                            st.session_state.filters[i].get(
                                "start_date", df[selected_column].min()
                            )
                        ),
                        key=f"filter-start-date-{i}",
                    )
                    st.session_state.filters[i]["end_date"] = st.date_input(
                        "종료일",
                        value=pd.to_datetime(
                            st.session_state.filters[i].get(
                                "end_date", df[selected_column].max()
                            )
                        ),
                        key=f"filter-end-date-{i}",
                    )
                elif selected_column in [
                    "모집인원",
                    "수강신청인원",
                    "수강확정인원",
                    "수료인원",
                    "평균 인원",
                    "전회차 인원",
                    "6개월후_취업률",
                    "만족도_평균점수",
                    "훈련시간",
                ]:
                    # 숫자 범위 필터
                    st.session_state.filters[i]["min"] = st.number_input(
                        "최소값",
                        value=st.session_state.filters[i].get("min", 0),
                        key=f"filter-min-{i}",
                    )
                    st.session_state.filters[i]["max"] = st.number_input(
                        "최대값",
                        value=st.session_state.filters[i].get("max", 100),
                        key=f"filter-max-{i}",
                    )
                else:
                    # 텍스트 필터
                    st.session_state.filters[i]["value"] = st.text_input(
                        "값 입력",
                        st.session_state.filters[i].get("value", ""),
                        key=f"filter-value-{i}",
                    )

            with cols[2]:
                st.button(
                    "삭제", key=f"remove-filter-{i}", on_click=remove_filter, args=(i,)
                )


if st.session_state.selected_file and df is not None:
    st.header(f"선택된 파일: {st.session_state.selected_file}")
    download, delete = st.columns([1, 1])
    if st.session_state.filters:
        filtered_df = df.copy()
        with download:
            st.download_button(
                label="필터링 된 CSV 다운로드",
                data=filtered_df.to_csv(index=False),
                file_name=f"filtered_{st.session_state.selected_file}",
                mime="text/csv",
            )
        for filter_item in st.session_state.filters:
            column = filter_item["column"]
            if column in ["개강일", "종강일"]:
                # 날짜 필터 적용
                start_date = pd.to_datetime(filter_item["start_date"])
                end_date = pd.to_datetime(filter_item["end_date"])
                filtered_df = filtered_df[
                    (pd.to_datetime(filtered_df[column]) >= start_date)
                    & (pd.to_datetime(filtered_df[column]) <= end_date)
                ]
            elif column in [
                "모집인원",
                "수강신청인원",
                "수강확정인원",
                "수료인원",
                "평균 인원",
                "전회차 인원",
                "6개월후_취업률",
                "만족도_평균점수",
                "훈련시간",
            ]:
                # 숫자 필터 적용
                filtered_df = filtered_df[
                    (filtered_df[column] >= filter_item["min"])
                    & (filtered_df[column] <= filter_item["max"])
                ]
            elif "value" in filter_item:
                # 텍스트 필터 적용
                filtered_df = filtered_df[
                    filtered_df[column]
                    .astype(str)
                    .str.contains(filter_item["value"], na=False)
                ]
        st.subheader("필터링 결과")
        display_filtered_df = filtered_df.copy()
        display_filtered_df.set_index("기관명", inplace=True)
        st.dataframe(display_filtered_df)
        create_chart(filtered_df)
        _, av_df, _ = st.columns([1, 2, 1])
        with av_df:
            create_average_dataframe(filtered_df)
    else:
        with download:
            st.download_button(
                label="CSV 다운로드",
                data=df.to_csv(index=False),
                file_name=st.session_state.selected_file,
                mime="text/csv",
            )
        display_df = df.copy()
        display_df.set_index("기관명", inplace=True)
        st.dataframe(display_df)
        create_chart(df)
        _, av_df, _ = st.columns([1, 3, 1])
        with av_df:
            create_average_dataframe(df)

    with delete:
        st.button("삭제", on_click=delete_file, args=(file_path,))

else:
    st.info("왼쪽에서 CSV 파일을 선택해 주세요.")
