import pandas as pd
import streamlit as st
import io

# 초기화
if "key" not in st.session_state:
    st.session_state.key = False
if "input_key" not in st.session_state:
    st.session_state.input_key = None
st.session_state.selected_file = None
st.set_page_config(page_title="SolTrack:Analyze", page_icon="📊", layout="wide")
solkey = st.secrets["KEY"]

st.title("분석 페이지")


def key_change(key):
    if key == solkey:
        st.session_state.key = True
        st.rerun()


def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="분석결과")
    processed_data = output.getvalue()
    return processed_data


if st.session_state.key == True:

    st.info(
        """
        아래 예측 취업률 데이터는 ChatGPT를 기반으로 한 예측값으로, 절대적인 지표로 활용하기에는 한계가 있을 수 있습니다. \n
        또한, HRD에서 제공하는 데이터는 최근 3년치(2022~2024년)만 포함되어 있으며, 특히 2024년 데이터는 아직 완전히 수집되지 않았으므로 참고하여 해석해 주시기 바랍니다.
        """
    )

    predicted_data, teachers = st.tabs(
        ["25년 예측 취업률", "각 선생님의 평균 취업률 및 만족도"]
    )

    with predicted_data:
        file_path = "./analyze/업체_직종별_예측취업률.csv"
        df = pd.read_csv(file_path)
        df["기관명"] = df["기관명"].str.replace(r"^\(주\)|^\(사\)", "", regex=True)

        df_sorted = df.sort_values(by=["직종", "예측_취업률"], ascending=[True, False])

        # 솔데스크 포함된 행 확인 (강조 표시용)
        df_sorted["강조"] = df_sorted["기관명"].eq("솔데스크")

        직종_목록 = df_sorted["직종"].unique()
        col1, col2, col3 = st.columns([0.9, 0.77, 1])

        for i, 직종 in enumerate(직종_목록):
            subset = df_sorted[df_sorted["직종"] == 직종].drop(columns=["직종"])

            # 컬럼 선택
            col = [col1, col2, col3][i % 3]

            with col:
                st.subheader(직종)

                # 솔데스크 강조 표시
                def highlight_solrow(row):
                    return (
                        ["color: #8C8CFF"] * len(row)
                        if row["강조"]
                        else [""] * len(row)
                    )

                styled_df = subset.style.apply(highlight_solrow, axis=1)
                st.dataframe(styled_df, hide_index=True, column_config={"강조": None})

                st.download_button(
                    label="📥 엑셀 다운로드",
                    data=to_excel(subset.drop(columns=["강조"])),
                    file_name=f"{직종}_25년_예측_취업률.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

    with teachers:
        file_path = "./analyze/강사_직종별_취업률과만족도.csv"
        df_teachers = pd.read_csv(file_path)

        df_teachers_sorted = df_teachers.sort_values(by="평균_취업률", ascending=False)

        st.subheader("강사별 평균 취업률 분석")

        def to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="강사별 취업률")
            processed_data = output.getvalue()
            return processed_data

        st.download_button(
            label="📥 엑셀 다운로드",
            data=to_excel(df_teachers_sorted),
            file_name="강사별_취업률.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.dataframe(df_teachers_sorted.reset_index(drop=True))
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
