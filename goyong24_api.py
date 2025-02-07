import requests
import json
import collections
import csv
import xml.etree.ElementTree as ET


class Use_API:

    with open("./json/location_api.json", "r", encoding="utf-8") as f:
        location_data = json.load(f)

    # key와 value 위치 바뀐 dict
    # reverse_data = {value: key for key, value in location_data.items()}

    authKey = "9aa1c3c5-e44f-4ccc-a119-e0af76286b28"
    returnType = "JSON"
    # 1은 리스트 2는 상세(고정) 솔직히 뭐가 다른건지 모르겠음.
    outType = "2"
    # 페이지당 출력건수(고정)
    pageSize = "100"

    # 정렬방법, 정렬컬럼(고정)
    sort = "DESC"
    sortCol = "TOT_FXNUM"

    def __init__(
        self,
        srchTraAreals,
        # srchNcsls,
        # crseTracseSels,
        # srchTraStDt,
        # srchTraEndDt,
    ):
        # 11만 쓰면 서울
        self.srchTraAreals = ["11"]
        # NCS 직종 대분류, 중분류, 소분류
        self.srchNcsls = ["200101", "200102", "200103"]
        # self.srchNcsls = srchNcsls
        # 훈련유형 K-digital 여긴 ,로 여러개 가능
        self.crseTracseSels = ["C0054,C0104"]
        # self.crseTracseSels = crseTracseSels

        # 훈련시작일 From, 훈련시작일 To
        self.srchTraStDt = "20240101"
        # self.srchTraStDt = srchTraStDt
        self.srchTraEndDt = "20240131"
        # self.srchTraEndDt = srchTraEndDt

    # 1. 훈련과정 수집
    def start_data_collection(self):
        srchList = []
        for srchTraArea in self.srchTraAreals:
            for srchNcs in self.srchNcsls:
                for crseTracseSe in self.crseTracseSels:
                    srchList = self.search_procedure_list(
                        srchList, srchTraArea, srchNcs, crseTracseSe
                    )
        procedure_lists = list(
            map(
                dict,
                collections.OrderedDict.fromkeys(
                    tuple(sorted(src.items())) for src in srchList
                ),
            )
        )

        self.detail_prodedure_data_collection(procedure_lists)

    # 2. url로 직접 이동해서 필요한 데이터들 수집 훈련과정 ID 및
    def search_procedure_list(self, srchList, srchTraArea, srchNcs, crseTracseSe):
        # 초기화
        pageNum = 1

        while True:
            url = f"https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do?authKey={self.authKey}&returnType={self.returnType}&outType={self.outType}&pageNum={pageNum}&pageSize={self.pageSize}&srchTraStDt={self.srchTraStDt}&srchTraEndDt={self.srchTraEndDt}&srchTraArea1={srchTraArea}&srchNcs1={srchNcs}&crseTracseSe={crseTracseSe}&sort={self.sort}&sortCol={self.sortCol}"

            response = requests.get(url).json()

            # 훈련과정ID = TRPR_ID, 기관명 = SUB_TITLE, 과정명 = TITLE, 주소 = ADDRESS
            for srch in response["srchList"]:
                srchList.append(
                    {
                        "주소": srch["address"],
                        "과정명": srch["title"],
                        "기관명": srch["subTitle"],
                        "훈련과정ID": srch["trprId"],
                        "훈련구분": srch["trainTargetCd"],
                        "만족도점수": round(
                            (
                                float(srch["stdgScor"]) / 200
                                if len(srch["stdgScor"]) > 2
                                else float(srch["stdgScor"]) / 20
                            ),
                            2,
                        ),
                    }
                )

            if response["scn_cnt"] > 100 and response["scn_cnt"] / pageNum > 100:
                pageNum += 1
            else:
                break

        return srchList

    # 3. 훈련과정 ID 가져와서 넣기
    def detail_prodedure_data_collection(self, procedure_lists):
        data_set = []
        print(len(procedure_lists))
        for procedure_list in procedure_lists:
            url = f"https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L03.do?authKey={self.authKey}&returnType=XML&outType=2&srchTrprId={procedure_list['훈련과정ID']}"
            response_str = requests.get(url).content.decode("utf-8")
            root = ET.fromstring(response_str)

            scn_lists = root.findall("scn_list")

            for scn_list in scn_lists:
                try:
                    employment_rate_6mon = scn_list.find("eiEmplRate6").text
                    employment_rate_6mon_people = scn_list.find("eiEmplCnt6").text
                    number_of_graduates = round(
                        float(employment_rate_6mon_people)
                        / float(employment_rate_6mon)
                        * 100
                    )

                    data_set.append(
                        {
                            "기관명": procedure_list["기관명"],
                            "과정명": procedure_list["과정명"],
                            "회차": scn_list.find("trprDegr").text,
                            "모집인원": scn_list.find("totFxnum").text,
                            "수강신청인원": scn_list.find("totTrpCnt").text,
                            "수강확정인원": scn_list.find("totParMks").text,
                            "수료인원": number_of_graduates,
                            "6개월후_취업률": round(
                                float(employment_rate_6mon)
                                + float(scn_list.find("hrdEmplRate6").text),
                                2,
                            ),
                            "개강일": scn_list.find("trStaDt").text,
                            "종강일": scn_list.find("trEndDt").text,
                            "주소": procedure_list["주소"],
                            "훈련구분": procedure_list["훈련구분"],
                            "만족도점수": procedure_list["만족도점수"],
                        }
                    )
                except AttributeError:
                    data_set.append(
                        {
                            "기관명": procedure_list["기관명"],
                            "과정명": procedure_list["과정명"],
                            "회차": scn_list.find("trprDegr").text,
                            "모집인원": scn_list.find("totFxnum").text,
                            "수강신청인원": scn_list.find("totTrpCnt").text,
                            "수강확정인원": (
                                scn_list.find("totParMks").text
                                if scn_list.find("totParMks") is not None
                                else "해당 정보 없음"
                            ),
                            "수료인원": "해당 정보 없음",
                            "6개월후_취업률": "해당 정보 없음",
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
                            "훈련구분": procedure_list["훈련구분"],
                            "만족도점수": procedure_list["만족도점수"],
                        }
                    )
        self.save_to_file("임시", data_set)

    # 4. dict 형태의 데이터를 csv로 저장
    def save_to_file(self, file_name, data_set):
        with open(f"./files/{file_name}.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "기관명",
                    "과정명",
                    "회차",
                    "모집인원",
                    "수강신청인원",
                    "수강확정인원",
                    "수료인원",
                    "6개월후_취업률",
                    "개강일",
                    "종강일",
                    "주소",
                    "훈련구분",
                    "만족도점수",
                ]
            )

            for data in data_set:
                writer.writerow(data.values())


if __name__ == "__main__":
    api = Use_API(["전체"])
    api.start_data_collection()
