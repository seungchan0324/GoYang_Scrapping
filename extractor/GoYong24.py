import time
import csv
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


class Extractor_Goyong24:

    def __init__(self):
        self.soup = self.edit_goyong_url()

    def start_crawling(self):
        links = self.link_url_crawling(self.soup)
        print(f"links 개수: {len(links)}")
        data_set = self.training_people_crawling(links)
        self.save_to_file("고용24", data_set)

    # area 기본값 서울+전체
    def edit_goyong_url(
        self, area="11%7C%EC%84%9C%EC%9A%B8+%EC%A0%84%EC%B2%B4", pages="1"
    ):
        goyong_url = f"https://www.work24.go.kr/hr/a/a/1100/trnnCrsInf.do?dghtSe=A&traingMthCd=A&tracseTme=16&endDate=20260101&keyword1=&keyword2=&pageSize=10&orderBy=ASC&startDate_datepicker=2024-01-01&currentTab=1&topMenuYn=&pop=&tracseId=AIG20230000412579&pageRow=100&totamtSuptYn=A&keywordTrngNm=&crseTracseSeNum=&keywordType=1&gb=&keyword=&kDgtlYn=&ncs=200103%7C%EC%A0%84%EC%B2%B4%2C200102%7C%EC%A0%84%EC%B2%B4%2C200101%7C%EC%A0%84%EC%B2%B4&area={area}&orderKey=2&mberSe=&kdgLinkYn=&srchType=all_type&totTraingTime=A&crseTracseSe=nlg_jsfc_yn%7C%EA%B5%AD%EA%B0%80%EA%B8%B0%EA%B0%84%EC%A0%84%EB%9E%B5%EC%82%B0%EC%97%85%EC%A7%81%EC%A2%85%2Ckdgtal_tgcr_yn%7CK-%EB%94%94%EC%A7%80%ED%84%B8%ED%8A%B8%EB%A0%88%EC%9D%B4%EB%8B%9D&tranRegister=&mberId=&i2=A&pageId=2&programMenuIdentification=EBG020000000310&endDate_datepicker=2026-01-01&monthGubun=&pageOrder=2ASC&pageIndex={pages}&bgrlInstYn=&startDate=20240101&crseTracseSeKDT=&gvrnInstt=&selectNCSKeyword=&action=trnnCrsInfPost.do"

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
        time.sleep(seconds)

    def training_people_crawling(self, links):
        data_set = []
        count = 1
        for link in links:
            print(f"{count}회차 {link}")
            url = "https://hrd.work24.go.kr/hrdp/co/pcobo/PCOBO0100P.do?"
            param = link.split("'")
            url += f"tracseId={param[1]}&tracseTme={param[3]}&crseTracseSe={param[5]}&trainstCstmrId={param[7]}&tracseReqstsCd=undefined&cstmConsTme=undefined#undefined"

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()

                page.goto(url, timeout=60000)
                print("url 가기")

                content = page.content()
                soup = BeautifulSoup(content, "html.parser")
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

                page.click("ul.tabList li:not(li.on)")
                page.wait_for_load_state("networkidle")
                print("훈련기관 정보 클릭")

                content = page.content()
                soup = BeautifulSoup(content, "html.parser")

                location = (
                    soup.find("ul", class_="infoList")
                    .find("span", class_="con")
                    .text.split("지도보기")[0]
                    .strip()
                )

                page.click("ul.tabList li:not(li.on)")
                page.wait_for_load_state("networkidle")
                print("훈련과정 정보 클릭")

                page.click("#infoTab7 button")
                page.wait_for_load_state("networkidle")
                print("다른회차 정보보기 클릭")

                content = page.content()
                soup = BeautifulSoup(content, "html.parser")

                trainings = soup.find("div", class_="accordionList").find_all("dl")

                trainings = trainings[::-1]

                each_trainings_data = []

                sum = 0

                for training in trainings:

                    recurrence = (
                        training.find("p", class_="tit").text.split("모집")[0].strip()
                    )

                    date = (
                        training.find("ul", class_="relList")
                        .find("span", class_="con")
                        .text.split("~")
                    )
                    start_date = date[0].strip()
                    end_date = date[1].strip()

                    number_of_student = (
                        training.find("table", class_="view")
                        .find_all("td")[1]
                        .text.split()
                    )

                    confirmed_student = int(number_of_student[1].split("명")[0])
                    not_confirmed_student = int(number_of_student[5].split("명")[0])

                    sum += confirmed_student

                    each_trainings_data.append(
                        {
                            "recurrence": recurrence,
                            "start_date": start_date,
                            "end_date": end_date,
                            "confirmed_student": confirmed_student,
                            "not_confirmed_student": not_confirmed_student,
                        }
                    )

                average_student = round(sum / len(each_trainings_data), 2)
                pre_confirmed_student = 0

                for data in each_trainings_data:

                    if pre_confirmed_student == 0:
                        pre_confirmed_student = "해당 정보 없음"

                    data_set.append(
                        {
                            "기관명": company,
                            "지역구": location,
                            "과정명": title,
                            "회차": data["recurrence"],
                            "직종": occupation,
                            "훈련유형": training_type,
                            "개강일": data["start_date"],
                            "종강일": data["end_date"],
                            "훈련시간": training_time,
                            "수강신청인원": data["not_confirmed_student"],
                            "수강확정인원": data["confirmed_student"],
                            "평균 인원": average_student,
                            "전회차 인원": pre_confirmed_student,
                        }
                    )

                    pre_confirmed_student = data["confirmed_student"]

                browser.close()
            self.wait(5)
            count += 1
        return data_set

    def save_to_file(self, file_name, data_set):
        file = open(f"{file_name}.csv", "w", encoding="utf-8", newline="")
        writer = csv.writer(file)
        writer.writerow(
            [
                "기관명",
                "지역구",
                "과정명",
                "회차",
                "직종",
                "훈련유형",
                "개강일",
                "종강일",
                "훈련시간",
                "수강신청인원",
                "수강확정인원",
                "평균 인원",
                "전회차 인원",
            ]
        )

        for data in data_set:
            writer.writerow(data.values())

        file.close()
