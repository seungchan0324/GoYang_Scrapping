import time
import logging
import csv
import requests
import random
from bs4 import BeautifulSoup
from util.file_name import File_Name_Selector


class Extractor_Goyong24:

    file_name_selector = File_Name_Selector()

    def __init__(
        self,
        start_date="2025-01-17",
        end_date="2025-03-17",
        area="11%7C서울+전체",
        training_data="kdgtal_tgcr_yn%7CK-디지털트레이닝%2Cnlg_jsfc_yn%7C국가전략산업직종",
    ):
        self.start_date = (str(start_date)).replace("-", "")
        self.start_date_picker = start_date
        self.end_date = (str(end_date)).replace("-", "")
        self.end_date_picker = end_date
        self.area = area
        self.training_data = training_data
        self.soup = self.edit_goyong_url()

    def start_crawling(self, update_status):
        links = self.link_url_crawling(self.soup)
        try:
            data_set = self.training_people_crawling(links, update_status)
        except:
            self.save_to_file(f"{len(self.data_set)}개 된 고용24", self.data_set)

        # 파일명
        file_name = self.file_name_selector.select(
            self.area, self.training_data, self.start_date_picker, self.end_date_picker
        )
        self.save_to_file(file_name, data_set)

    # area 기본값 서울+전체
    def edit_goyong_url(
        self,
        pages="1",
    ):
        goyong_url = f"https://www.work24.go.kr/hr/a/a/1100/trnnCrsInf.do?dghtSe=A&traingMthCd=A&tracseTme=16&endDate={self.end_date}&keyword1=&keyword2=&pageSize=10&orderBy=ASC&startDate_datepicker={self.start_date_picker}&currentTab=1&topMenuYn=&pop=&tracseId=AIG20230000412579&pageRow=100&totamtSuptYn=A&keywordTrngNm=&crseTracseSeNum=&keywordType=1&gb=&keyword=&kDgtlYn=&ncs=200103%7C전체%2C200102%7C전체%2C200101%7C전체&area={self.area}&orderKey=2&mberSe=&kdgLinkYn=&srchType=all_type&totTraingTime=A&crseTracseSe={self.training_data}&tranRegister=&mberId=&i2=A&pageId=2&programMenuIdentification=EBG020000000310&endDate_datepicker={self.end_date_picker}&monthGubun=&pageOrder=2ASC&pageIndex={pages}&bgrlInstYn=&startDate={self.start_date}&crseTracseSeKDT=&gvrnInstt=&selectNCSKeyword=&action=trnnCrsInfPost.do"

        response = requests.get(
            goyong_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            },
        )
        soup = BeautifulSoup(response.content, "html.parser")

        return soup

    def link_url_crawling(self, soup):

        count = int(
            soup.find("ul", class_="tab_title")
            .find("span")
            .text.split("(")[1]
            .split(")")[0]
        )

        page_n = int(count / 100) + 1
        links = []

        for i in range(page_n):
            soup = self.edit_goyong_url(pages=i + 1)

            titles = soup.find_all("h3", class_="link_text")

            for title in titles:
                link = title.find("a")["onclick"]
                links.append(link)

        return links

    def wait(self, seconds=4):
        time.sleep(random.uniform(1, seconds))

    def make_param(self, link):
        param = link.split("'")
        return {
            "tracseId": param[1],
            "tracseTme": param[3],
            "crseTracseSe": param[5],
            "trainstCstmrId": param[7],
        }

    def info_url(self, link, alphabet):
        url = f"https://hrd.work24.go.kr/hrdp/co/pco{alphabet}o/PCO{alphabet.upper()}O0100P.do?"
        param = link.split("'")
        url += f"tracseId={param[1]}&tracseTme={param[3]}&crseTracseSe={param[5]}&trainstCstmrId={param[7]}&tracseReqstsCd=undefined&cstmConsTme=undefined#undefined"
        return url

    # selenium 오류 방지 코드
    # def goto_with_retry(
    #     self, page, url, max_retries=3, wait_until="networkidle", timeout=30_000
    # ):
    #     """page.goto()에 대해 최대 max_retries번 재시도."""
    #     for attempt in range(1, max_retries + 1):
    #         try:
    #             page.goto(url, wait_until=wait_until, timeout=timeout)
    #             print(f"[SUCCESS] URL 로드 성공")
    #             return  # 성공 시 함수를 빠져나감
    #         except TimeoutError as e:
    #             print(f"[ERROR] {url} 로드 타임아웃 (시도 {attempt}/{max_retries})")
    #             if attempt < max_retries:
    #                 print("잠시 대기 후 재시도합니다...")
    #                 self.wait(2)  # 2초 정도 대기 후 재시도
    #             else:
    #                 print("최대 재시도 횟수를 초과했습니다.")
    #                 # 여기서 raise 하거나 return 하거나, 원하는 처리를 수행
    #                 raise e  # 최종적으로 예외를 던져서 밖으로 전달

    def training_people_crawling(self, links, update_status):
        try:
            self.data_set = []
            count = 1
            for link in links:
                log_message = f"Step {count}/{len(links)}: 작업 진행 중..."
                update_status(log_message)
                url = self.info_url(link, "c")

                response = requests.get(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                    },
                )
                soup = BeautifulSoup(response.content, "html.parser")

                location = (
                    soup.find("ul", class_="infoList")
                    .find("span", class_="con")
                    .text.split("지도보기")[0]
                    .strip()
                )

                url = self.info_url(link, "b")

                response = requests.get(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                    },
                )
                soup = BeautifulSoup(response.content, "html.parser")

                company = (
                    soup.find("section", id="section1")
                    .find("div", class_="title")
                    .find("p")
                    .text.strip()
                )

                title = (
                    soup.find("section", id="section1")
                    .find("div", class_="title")
                    .find("h4")
                    .text
                )
                title = title.split("모집")[0].strip()

                job_sort = (
                    soup.find("section", id="section1")
                    .find("div", class_="box")
                    .find("ul", class_="list")
                    .find_all("span", class_="con")
                )

                occupation = job_sort[1].text.strip()

                training_type = job_sort[12].text.strip()

                training_time = job_sort[6].text.split("총")[1].split("시간")[0]

                ajax = "https://hrd.work24.go.kr/hrdp/co/pcobo/PCOBO0107TAjax.do"

                url = self.info_url(link, "b")

                headers = {
                    "Referer": url,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                }

                param = self.make_param(link)

                reponse = requests.get(ajax, param, headers=headers)

                soup = BeautifulSoup(reponse.text, "html.parser")

                trainings = soup.find_all("dl", class_="item")

                trainings = trainings[::-1]

                each_trainings_data = []

                sum = 0

                if not trainings:
                    self.data_set.append(
                        {
                            "기관명": company,
                            "주소": location,
                            "과정명": title,
                            "회차": "해당 정보 없음",
                            "직종": occupation,
                            "훈련유형": training_type,
                            "개강일": "해당 정보 없음",
                            "종강일": "해당 정보 없음",
                            "훈련시간": training_time,
                            "모집인원": "해당 정보 없음",
                            "수강신청인원": "해당 정보 없음",
                            "수강확정인원": "해당 정보 없음",
                            "평균 인원": "해당 정보 없음",
                            "전회차 인원": "해당 정보 없음",
                            "만족도_평균점수": "해당 정보 없음",
                            "만족도_응답자수": "해당 정보 없음",
                            "6개월후_취업률_퍼센트": "해당 정보 없음",
                            "6개월후_취업률_기준인원": "해당 정보 없음",
                        }
                    )
                    continue

                for training in trainings:

                    # 회차
                    recurrence = (
                        training.find("p", class_="tit").text.split("모집")[0].strip()
                    )

                    date = (
                        training.find("ul", class_="relList")
                        .find("span", class_="con")
                        .text.split("~")
                    )
                    # 훈련 시작날
                    start_date = date[0].strip()
                    # 훈련 종료날
                    end_date = date[1].strip()

                    training_data = training.find("table", class_="view").find_all("td")

                    def text_splitter(n):
                        return training_data[n].text.strip()

                    # 모집인원
                    recruit_student = text_splitter(0)

                    # 수강확정인원/수강신청인원
                    number_of_student = text_splitter(1).split(" ")
                    # 수강확정인원
                    confirmed_student = int(number_of_student[1].split("명")[0])
                    # 수강신청인원
                    not_confirmed_student = int(number_of_student[5].split("명")[0])

                    # 만족도
                    satisfaction = text_splitter(2)
                    if "( 명)" in satisfaction:
                        satisfaction = "해당 정보 없음"
                        satisfaction_people = "해당 정보 없음"
                    else:
                        score = satisfaction.split("점")[1].replace("기준", "").strip()
                        people = satisfaction.split("점")[2].strip()
                        satisfaction = score
                        satisfaction_people = people

                    if (
                        text_splitter(4) == "훈련진행중"
                        or text_splitter(4) == "해당없음"
                        or text_splitter(4).split("%")[0] == ""
                    ):
                        employment_rate_6mon = "6개월이 안 지났거나 해당 정보 없음"
                        employment_rate_6mon_people = (
                            "6개월이 안 지났거나 해당 정보 없음"
                        )
                    else:
                        # 취업률 3개월
                        # employment_rate_3mon = (
                        #     str(
                        #         float(text_splitter(3).split("%")[0])
                        #         + float(text_splitter(5).split("%")[0])
                        #     )
                        #     + "%"
                        # )
                        # 취업률 6개월
                        employment_rate_6mon = str(
                            round(
                                float(text_splitter(4).split("%")[0])
                                + float(text_splitter(6).split("%")[0]),
                                2,
                            )
                        )
                        employment_rate_6mon_people = (
                            text_splitter(4).split("/")[1].replace(")", "")
                        )

                    sum += confirmed_student

                    each_trainings_data.append(
                        {
                            "recurrence": recurrence,
                            "start_date": start_date,
                            "end_date": end_date,
                            "recruit_student": recruit_student,
                            "confirmed_student": confirmed_student,
                            "not_confirmed_student": not_confirmed_student,
                            "satisfaction": satisfaction,
                            "satisfaction_people": satisfaction_people,
                            "employment_rate_6mon": employment_rate_6mon,
                            "employment_rate_6mon_people": employment_rate_6mon_people,
                        }
                    )

                average_student = round(sum / len(each_trainings_data), 2)
                pre_confirmed_student = 0

                for data in each_trainings_data:

                    if pre_confirmed_student == 0:
                        pre_confirmed_student = "해당 정보 없음"

                    self.data_set.append(
                        {
                            "기관명": company,
                            "주소": location,
                            "과정명": title,
                            "회차": data["recurrence"],
                            "직종": occupation,
                            "훈련유형": training_type,
                            "개강일": data["start_date"],
                            "종강일": data["end_date"],
                            "훈련시간": training_time,
                            "모집인원": data["recruit_student"],
                            "수강신청인원": data["not_confirmed_student"],
                            "수강확정인원": data["confirmed_student"],
                            "평균 인원": average_student,
                            "전회차 인원": pre_confirmed_student,
                            "만족도_평균점수": data["satisfaction"],
                            "만족도_응답자수": data["satisfaction_people"],
                            "6개월후_취업률_퍼센트": data["employment_rate_6mon"],
                            "6개월후_취업률_기준인원": data[
                                "employment_rate_6mon_people"
                            ],
                        }
                    )

                    pre_confirmed_student = data["confirmed_student"]

                print("append 완료")
                count += 1
            logging.info("작업 완료!")
            print("작업 완료!")
            return self.data_set
        except Exception as e:
            print(f"Error during crawling: {e}")
            return []

    def save_to_file(self, file_name, data_set):
        file = open(f"./files/{file_name}.csv", "w", encoding="utf-8", newline="")
        writer = csv.writer(file)
        writer.writerow(
            [
                "기관명",
                "주소",
                "과정명",
                "회차",
                "직종",
                "훈련유형",
                "개강일",
                "종강일",
                "훈련시간",
                "모집인원",
                "수강신청인원",
                "수강확정인원",
                "평균 인원",
                "전회차 인원",
                "만족도_평균점수",
                "만족도_응답자수",
                "6개월후_취업률_퍼센트",
                "6개월후_취업률_기준인원",
            ]
        )

        for data in data_set:
            writer.writerow(data.values())

        file.close()

    def test_url(self, urls):
        self.training_people_crawling(urls)
