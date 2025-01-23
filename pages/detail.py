import streamlit as st
import pandas as pd
import plotly.express as px
import os


st.set_page_config(page_title="상세 페이지", page_icon="📑", layout="wide")

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


def create_chart(df):
    # 차트 생성
    if "6개월후_취업률" in df.columns and "개강일" in df.columns:
        # Plotly 차트 생성
        st.subheader("취업률 기준 차트")
        fig = px.scatter(
            df,
            x="개강일",  # 가로축: 취업률
            y="6개월후_취업률",  # 세로축: 개강일
            hover_data={
                "기관명": True,  # 마우스오버 시 기관명 표시
                "과정명": True,  # 마우스오버 시 과정명 표시
                "6개월후_취업률": True,  # 마우스오버 시 취업률 표시
                "개강일": True,  # 마우스오버 시 개강일 표시
            },
            labels={
                "6개월후_취업률": "취업률(%)",
                "개강일": "개강일",
                "기관명": "기관명",
                "과정명": "과정명",
            },
        )
        fig.update_layout(
            xaxis_title="개강일",
            yaxis_title="취업률(%)",
            title="6개월 후 취업률과 개강일 기준 차트",
            title_x=0.5,
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)


# CSS 및 HTML 테이블 렌더링
def render_fixed_column_table(df):
    st.markdown(
        """
        <style>
        .table-container {
            overflow-x: auto; /* 가로 스크롤 허용 */
            overflow-y: auto; /* 세로 스크롤 허용 */
            height: 500px; /* 테이블 높이 고정 */
        }
        table {
            border-collapse: collapse;
            width: 100%;
            table-layout: fixed;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f4f4f4;
            position: sticky;
            top: 0; /* 헤더 고정 */
            z-index: 2;
        }
        td:nth-child(2), th:nth-child(2) {
            position: sticky;
            left: 0; /* 두 번째 컬럼 고정 (과정명) */
            background-color: #fff;
            z-index: 1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # HTML 테이블 생성
    table_html = df.to_html(index=False, escape=False)
    st.markdown(
        f"""
    <div class="table-container">
        {table_html}
    </div>
    """,
        unsafe_allow_html=True,
    )


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
        st.dataframe(filtered_df)
        create_chart(filtered_df)

        with download:
            st.download_button(
                label="필터링 된 CSV 다운로드",
                data=filtered_df.to_csv(index=False),
                file_name=f"filtered_{st.session_state.selected_file}",
                mime="text/csv",
            )
    else:
        st.dataframe(df)
        create_chart(df)
        with download:
            st.download_button(
                label="CSV 다운로드",
                data=df.to_csv(index=False),
                file_name=st.session_state.selected_file,
                mime="text/csv",
            )
    with delete:
        st.button("삭제", on_click=delete_file, args=(file_path,))
else:
    st.info("왼쪽에서 CSV 파일을 선택해 주세요.")
