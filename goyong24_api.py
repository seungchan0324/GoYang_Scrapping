import requests
import json
import collections
import csv
import re
import time
import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import datetime as dt
from file_name import File_Name_Selector


class Use_API:

    # with open("./json/location_api.json", "r", encoding="utf-8") as f:
    #     location_data = json.load(f)

    file_name_selector = File_Name_Selector()

    # apikey
    authKey = "9aa1c3c5-e44f-4ccc-a119-e0af76286b28"
    # returnType 절대절대 고정
    returnType = "JSON"
    # 1은 리스트 2는 상세(고정) 솔직히 뭐가 다른건지 모르겠음.
    outType = "2"
    # 페이지당 출력건수(고정)
    pageSize = "100"

    # 정렬방법, 정렬컬럼(고정)
    sort = "DESC"
    sortCol = "TOT_FXNUM"

    # 6개월 기준 취업률에 적혀 있는 문자별 상태값
    status_dict = {
        "A": "개설예정",
        "B": "진행중",
        "C": "미실시",
        "D": "수료자 없음",
    }

    # 지역, 직종, 훈련유형, 개강일, 종강일, 훈련과정명, 훈련기관명
    def __init__(
        self,
        srchTraStDt,
        srchTraEndDt,
        srchTraAreals,
        srchNcsls,
        crseTracseSels,
        keyword,
    ):
        # 훈련시작일 From, 훈련시작일 To
        self.srchTraStDt = str(srchTraStDt).replace("-", "")
        self.startDate = srchTraStDt
        self.srchTraEndDt = str(srchTraEndDt).replace("-", "")
        self.endDate = srchTraEndDt

        # 11만 쓰면 서울
        self.srchTraAreals = srchTraAreals
        # NCS 직종 대분류, 중분류, 소분류
        self.srchNcsls = srchNcsls
        # 훈련유형 K-digital 여긴 ,로 여러개 가능
        self.crseTracseSels = crseTracseSels
        if "None" in crseTracseSels:
            self.crseTracseSelstr = ""
        else:
            self.crseTracseSelstr = ",".join(crseTracseSels)

        # 검색 keyword
        if keyword:
            self.keyword = keyword.replace("&", "")
        else:
            self.keyword = ""

    # 도구1 날짜 문자열을 date 객체로 변환
    def dt_formatter(self, str_date):
        return dt.datetime.strptime(str_date, "%Y-%m-%d").date()

    # 도구2 개강일이 지정 날짜 범위 내에 있는지 확인
    def start_date_cutting(self, start_date):
        start_date = self.dt_formatter(start_date)
        if not (self.startDate <= start_date <= self.endDate):
            return True
        return False

    # 1. 추가 정보 API 호출 (140시간 이상 체크)
    async def more_than_140_hours_async(
        self,
        session,
        srchTrprId,
        trainstCstId,
    ):
        url = (
            f"https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L02.do"
            f"?authKey={self.authKey}&returnType=JSON&outType=2"
            f"&srchTrprId={srchTrprId}&srchTrprDegr=1&srchTorgId={trainstCstId}"
        )
        async with session.get(url) as response:
            data = await response.json()
        try:
            if int(data["inst_base_info"]["trtm"]) >= 140:
                return True, data["inst_base_info"]
        except Exception as e:
            print("more_than_140_hours_async 에러:", e, srchTrprId)
        return False, ""

    # 2. 목록 API 호출 (페이지 단위) 및 배치화
    async def search_procedure_list_async(
        self,
        session,
        srchTraArea,
        srchNcs,
        crseTracseSe,
    ):
        # 초기화
        pageNum = 1
        all_tasks = []
        all_srches = []
        i = 0
        while True:
            normal_url = (
                f"https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do"
                f"?authKey={self.authKey}&returnType={self.returnType}&outType={self.outType}"
                f"&pageNum={pageNum}&pageSize={self.pageSize}"
                f"&srchTraStDt={self.srchTraStDt}&srchTraEndDt={self.srchTraEndDt}"
                f"&srchTraArea1={srchTraArea}&srchNcs1={srchNcs}&crseTracseSe={crseTracseSe}"
                f"&sort={self.sort}&sortCol={self.sortCol}"
            )

            page_has_results = False

            # keyword에 대해 과정명과 기관명을 한번씩 검색 후 그걸 task에 넣은 후 한번에 동작하기 위함
            param_types = [
                ("srchTraProcessNm", self.keyword),  # 과정명 검색
                ("srchTraOrganNm", self.keyword),  # 기관명 검색
            ]

            for param_key, param_val in param_types:
                url = normal_url + f"&{param_key}={param_val}"
                async with session.get(url) as response:
                    data = await response.json()

                unique_srches = list(
                    {d["title"]: d for d in data.get("srchList", [])}.values()
                )

                if unique_srches:
                    page_has_results = True

                for srch in unique_srches:
                    task = self.more_than_140_hours_async(
                        session, srch["trprId"], srch["trainstCstId"]
                    )
                    all_srches.append(srch)
                    all_tasks.append(task)

            if not page_has_results or len(unique_srches) < int(self.pageSize):
                break
            else:
                pageNum += 1

        results = await asyncio.gather(*all_tasks)

        # 배치화: 각 검색 결과에 대해 동시에 140시간 이상 여부를 체크
        srchList = []
        for srch, (flag, info) in zip(all_srches, results):
            if not flag:
                continue

            try:
                satisfaction_score = round(
                    (
                        (float(srch["stdgScor"]) / 200)
                        if len(srch["stdgScor"]) > 2
                        else float(srch["stdgScor"]) / 20
                    ),
                    2,
                )
            except Exception:
                satisfaction_score = 0

            # 훈련과정ID = TRPR_ID, 기관명 = SUB_TITLE, 과정명 = TITLE, 주소 = ADDRESS
            srchList.append(
                {
                    "주소": srch["address"],
                    "과정명": srch["title"],
                    "기관명": srch["subTitle"],
                    "훈련과정ID": srch["trprId"],
                    "훈련구분": info["trprTargetNm"],
                    "직종": info["ncsNm"],
                    "만족도점수": satisfaction_score,
                }
            )

        return srchList

    # 3. 상세 정보 API 호출 (개별 교육과정)
    async def fetch_detail_async(self, session, procedure_list):
        url = (
            f"https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L03.do"
            f"?authKey={self.authKey}&returnType=XML&outType=2"
            f"&srchTrprId={procedure_list['훈련과정ID']}"
        )
        async with session.get(url) as response:
            response_str = await response.text()
        root = ET.fromstring(response_str)

        details = []
        for scn_list in root.findall("scn_list"):
            # 왜인지 모르겠지만 0회차가 존재 or 개강날짜 기준에 맞추기
            if scn_list.find("trprDegr").text == "0" or self.start_date_cutting(
                scn_list.find("trStaDt").text
            ):
                continue

            # 6개월 기준 취업률에 문자가 있으면 해당 과정은 개설예정, 진행중, 미실시, 수료자 없음 중 하나라 제외
            if not re.fullmatch(r"[^\d]", scn_list.find("eiEmplRate6").text):
                employment_rate_6mon = scn_list.find("eiEmplRate6").text
                employment_rate_6mon_people = scn_list.find("eiEmplCnt6").text
                # 수료인원과 취업률에 반영되는 인원이 달라 일단 취업률에 반영되는 인원으로 수료인원 지정함
                if float(employment_rate_6mon) != 0:
                    number_of_graduates = round(
                        float(employment_rate_6mon_people)
                        / float(employment_rate_6mon)
                        * 100
                    )
                else:
                    number_of_graduates = 0
                print(
                    f"program_title:{procedure_list['과정명']}, program_id:{procedure_list['훈련과정ID']}, program_round:{scn_list.find('trprDegr').text}, 훈련시작일: {scn_list.find('trStaDt').text}, 훈련종료일: {scn_list.find('trEndDt').text}"
                )
                details.append(
                    {
                        "기관명": procedure_list["기관명"],
                        "과정명": procedure_list["과정명"],
                        "회차": scn_list.find("trprDegr").text,
                        "수강확정인원": scn_list.find("totParMks").text,
                        "수료인원": number_of_graduates,
                        "6개월후_취업률": round(
                            float(employment_rate_6mon)
                            + float(scn_list.find("hrdEmplRate6").text),
                            2,
                        ),
                        "직종": procedure_list["직종"],
                        "과정상황": "과정 종료",
                        "수강신청인원": scn_list.find("totTrpCnt").text,
                        "모집인원": scn_list.find("totFxnum").text,
                        "훈련유형": procedure_list["훈련구분"],
                        "개강일": scn_list.find("trStaDt").text,
                        "종강일": scn_list.find("trEndDt").text,
                        "주소": procedure_list["주소"],
                        "만족도_평균점수": procedure_list["만족도점수"],
                    }
                )
            else:
                details.append(
                    {
                        "기관명": procedure_list["기관명"],
                        "과정명": procedure_list["과정명"],
                        "회차": scn_list.find("trprDegr").text,
                        "수강확정인원": (
                            scn_list.find("totParMks").text
                            if scn_list.find("totParMks") is not None
                            else "해당 정보 없음"
                        ),
                        "수료인원": scn_list.find("finiCnt").text,
                        "6개월후_취업률": self.status_dict[
                            scn_list.find("eiEmplRate6").text
                        ],
                        "직종": procedure_list["직종"],
                        "과정상황": self.status_dict[scn_list.find("eiEmplRate6").text],
                        "수강신청인원": scn_list.find("totTrpCnt").text,
                        "모집인원": scn_list.find("totFxnum").text,
                        "훈련유형": procedure_list["훈련구분"],
                        "개강일": (
                            scn_list.find("trStaDt").text
                            if scn_list.find("trStaDt") is not None
                            else "해당 정보 없음"
                        ),
                        "종강일": (
                            scn_list.find("trEndDt").text
                            if scn_list.find("trEndDt") is not None
                            else "해당 정보 없음"
                        ),
                        "주소": procedure_list["주소"],
                        "만족도_평균점수": procedure_list["만족도점수"],
                    }
                )
        return details

    # 4. 모든 상세 정보를 비동기 배치 처리 후 CSV 저장
    async def detail_procedure_data_collection_async(self, session, procedure_lists):
        tasks = []
        for procedure_list in procedure_lists:
            tasks.append(self.fetch_detail_async(session, procedure_list))
        results = await asyncio.gather(*tasks)

        data_set = []
        for details in results:
            data_set.extend(details)

        data_set = sorted(
            data_set, key=lambda x: (x["기관명"], x["과정명"], int(x["회차"]))
        )

        # 파일명
        file_name = self.file_name_selector.select(
            self.srchTraAreals,
            self.crseTracseSels,
            self.startDate,
            self.endDate,
            self.keyword,
        )
        self.save_to_file(file_name, data_set)

    # 5. CSV 파일 저장 (동기)
    def save_to_file(self, file_name, data_set):
        with open(f"./files/{file_name}.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "기관명",
                    "과정명",
                    "회차",
                    "수강확정인원",
                    "수료인원",
                    "6개월후_취업률",
                    "직종",
                    "과정상황",
                    "수강신청인원",
                    "모집인원",
                    "훈련유형",
                    "개강일",
                    "종강일",
                    "주소",
                    "만족도_평균점수",
                ]
            )

            for data in data_set:
                writer.writerow(data.values())

    # 6. 전체 데이터 수집 비동기 프로세스
    async def start_data_collection_async(self, update_status):
        update_status("api 통신 시작...")
        # requests여러번 생성되는거 방지하는 역할
        async with aiohttp.ClientSession() as session:
            tasks = []
            for srchTraArea in self.srchTraAreals:
                for srchNcs in self.srchNcsls:
                    tasks.append(
                        self.search_procedure_list_async(
                            session,
                            srchTraArea,
                            srchNcs,
                            self.crseTracseSelstr,
                        )
                    )
            results = await asyncio.gather(*tasks)
            srchList = []
            for lst in results:
                srchList.extend(lst)

            # 과정 중복제거
            procedure_lists = list(
                map(
                    dict,
                    collections.OrderedDict.fromkeys(
                        tuple(sorted(src.items())) for src in srchList
                    ),
                )
            )
            update_status(f"총 과정 수 {len(procedure_lists)}개를 저장하고 있습니다...")
            await self.detail_procedure_data_collection_async(session, procedure_lists)


async def main():
    start_time = time.time()
    api = Use_API(
        dt.datetime.strptime("2022-01-01", "%Y-%m-%d").date(),
        dt.datetime.strptime("2025-02-18", "%Y-%m-%d").date(),
        ["11"],
        ["200101", "200102", "200103"],
        ["None"],
        "자바파이썬빅데이터",
    )
    await api.start_data_collection_async(print)
    end_time = time.time()
    print("코드 실행 시간: {:.6f}초".format(end_time - start_time))


if __name__ == "__main__":
    asyncio.run(main())


# 서울 전체 k-digital 240101 ~ 240131 28.970319초 27.577818초
# 서울 전체 k-digital 240101 ~ 241231 439.235440초

# 동기식 및 배치화까지 적용 시킨 후
# 서울 전체 k-digital 240101 ~ 240131 2.311578초
# 서울 전체 k-digital 240101 ~ 241231 18.442422초
