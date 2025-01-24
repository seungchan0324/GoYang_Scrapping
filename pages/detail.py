import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
import json

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

st.set_page_config(page_title="SolTrack:Detail", page_icon="📑", layout="wide")

st.markdown(custom_css, unsafe_allow_html=True)

if "selected_file" not in st.session_state:
    st.session_state.selected_file = None
if "filters" not in st.session_state:
    st.session_state.filters = []
if "key" not in st.session_state:
    st.session_state.key = False
if "input_key" not in st.session_state:
    st.session_state.input_key = None


with open("./json/과정_강사.json", "r", encoding="UTF-8") as f:
    teacher_json = json.load(f)


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
    # 차트 생성
    if "6개월후_취업률" in df.columns and "개강일" in df.columns:

        # 색상 데이터 추가
        df["색상"] = df["기관명"].apply(
            lambda x: "솔데스크" if x == "솔데스크" else "기타"
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
            # 툴팁 순서를 명시적으로 지정
            hover_data={
                "기관명": True,  # 3. 기관명
                "과정명": True,  # 4. 과정명
                "개강일": True,  # 1. 개강일
                "6개월후_취업률": True,  # 2. 취업률
                "강사명": True,
                "만족도_평균점수": True,
                "색상": False,  # 색상 데이터 숨기기
            },
            labels={
                "6개월후_취업률": "취업률(%)",
                "개강일": "개강일",
                "기관명": "기관명",
                "과정명": "과정명",
                "강사명": "강사명",
                "만족도_평균점수": "만족도 점수",
            },
        )
        fig.update_layout(
            xaxis_title="개강일",
            yaxis_title="취업률(%)",
            title="6개월 후 취업률과 개강일 기준 차트",
            title_x=0.5,
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False})


# 평균 취업률 표 생성
def create_average_dataframe(df):
    st.subheader("기업별 평균 취업률")
    average_employment_df = (
        df.groupby(["기관명", "직종"])
        .agg(
            평균취업률=("6개월후_취업률", "mean"),  # 평균 취업률
            평균수료인원=("수료인원", "mean"),
            과정_진행_횟수=("회차", "count"),  # 회차 수 계산
        )
        .reset_index()
    )
    average_employment_df["평균취업률"] = average_employment_df["평균취업률"].round(2)
    average_employment_df["평균수료인원"] = average_employment_df["평균수료인원"].round(
        2
    )
    average_employment_df = average_employment_df.sort_values(
        by="평균취업률", ascending=False
    )
    average_df = average_employment_df.copy()
    average_employment_df.set_index("기관명", inplace=True)
    st.dataframe(average_employment_df, width=1000)
    return average_df


def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output


def find_teacher(row):
    if row["기관명"] == "솔데스크":
        for title in teacher_json:
            if (
                title["과정명"] == row["과정명"]
                and title["훈련시작일"] == row["개강일"]
                and title["훈련종료일"] == row["종강일"]
            ):
                return title["메인강사"]
        return "일치하는 과정이 없습니다."
    else:
        return "해당 정보 없음"


def employment_average_chart(df, chart_key):
    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    # 색상 컬럼 추가
    df["색상"] = df["기관명"].apply(lambda x: "red" if x == "솔데스크" else "lightblue")

    # 평균취업률 기준 내림차순 정렬
    df = df.sort_values(by="평균취업률", ascending=False)

    # 막대 색상을 데이터 순서대로 적용
    fig = px.bar(
        df,
        x="기관명",
        y="평균취업률",
        hover_data={
            "평균취업률": True,
            "기관명": True,
        },
        labels={"평균취업률": "평균 취업률(%)", "기관명": "기관 이름"},
    )

    # Plotly의 update_traces를 사용해 색상 적용
    fig.update_traces(marker_color=df["색상"])

    # 차트 출력
    st.plotly_chart(fig, key=chart_key)


def occupation_chart(df):
    st.subheader("직종별 평균 취업률")
    it_system_tab, ui_ux_tab, big_data_tab, application_software_tab = st.tabs(
        [
            "IT 시스템 관리",
            "UI/UX 엔지니어링",
            "빅데이터 분석",
            "응용 SW 엔지니어링",
        ]
    )

    # IT 시스템 관리
    with it_system_tab:
        it_system_management_df = df[df["직종"] == "IT시스템관리(20010301)"]
        employment_average_chart(
            it_system_management_df, chart_key="it_system_management"
        )

    # UI/UX 엔지니어링
    with ui_ux_tab:
        ui_ux_engineering_df = df[df["직종"] == "UI/UX엔지니어링(20010207)"]
        employment_average_chart(ui_ux_engineering_df, chart_key="ui_ux_engineering")

    # 빅데이터 분석
    with big_data_tab:
        big_data_analysis_df = df[df["직종"] == "빅데이터분석(20010105)"]
        employment_average_chart(big_data_analysis_df, chart_key="big_data_analysis")

    # 응용 SW 엔지니어링
    with application_software_tab:
        application_software_engineering_df = df[
            df["직종"] == "응용SW엔지니어링(20010202)"
        ]
        employment_average_chart(
            application_software_engineering_df,
            chart_key="application_software_engineering",
        )


def key_change(key):
    if key == "$sol25":
        st.session_state.key = True
        st.rerun()


directory = "files"
csv_files = sorted([f for f in os.listdir(directory) if f.endswith(".csv")])
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

if st.session_state.key == True:

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

        df["기관명"] = df["기관명"].str.replace(r"^\(.\)", "", regex=True)
        df["강사명"] = df.apply(find_teacher, axis=1)
        df["만족도_평균점수"] = round(df["만족도_평균점수"] / 20, 1)
        df.insert(3, "강사명", df.pop("강사명"))

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
                        "삭제",
                        key=f"remove-filter-{i}",
                        on_click=remove_filter,
                        args=(i,),
                    )

    if st.session_state.selected_file and df is not None:
        st.header(f"선택된 파일: {st.session_state.selected_file}")
        download, delete = st.columns([1, 1])
        if st.session_state.filters:
            filtered_df = df.copy()
            with download:
                excel_data = convert_df_to_excel(df)
                st.download_button(
                    label="필터링된 Excel 다운로드",
                    data=excel_data,
                    file_name=f"{st.session_state.selected_file.rsplit('.', 1)[0]}.xlsx",  # 원하는 파일 이름 설정
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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
                average_df = create_average_dataframe(filtered_df)
        else:
            with download:
                excel_data = convert_df_to_excel(df)
                st.download_button(
                    label="Excel 다운로드",
                    data=excel_data,
                    file_name=f"{st.session_state.selected_file.rsplit('.', 1)[0]}.xlsx",  # 원하는 파일 이름 설정
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            display_df = df.copy()
            display_df.set_index("기관명", inplace=True)
            st.dataframe(display_df)
            create_chart(df)
            _, av_df, _ = st.columns([1, 3, 1])
            with av_df:
                average_df = create_average_dataframe(df)
            occupation_chart(average_df)

        with delete:
            st.button("삭제", on_click=delete_file, args=(file_path,))

    else:
        st.info("왼쪽에서 CSV 파일을 선택해 주세요.")
else:
    with st.sidebar:
        key = st.text_input(
            "키를 입력하여 주십시오.",
            value=st.session_state.input_key,
            type="password",
        )
        if key:
            key_change(key)
    st.warning("왼쪽에서 키를 입력하여 주십시오.")
