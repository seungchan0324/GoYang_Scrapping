url = "https://hrd.work24.go.kr/hrdp/co/pcobo/PCOBO0107TAjax.do"
from fake_useragent import UserAgent
import re

for info in infos:
    # print(info)

    tracseid = info.get("tracseId")
    tracseTme = info.get("tracseTme")
    trainstCstmrId = "500037933544"

    params = {
        "tracseId": tracseid,
        "tracseTme": tracseTme,
        "trainstCstmrId": trainstCstmrId,
    }

    headers = {
        "Referer": f"https://hrd.work24.go.kr/hrdp/co/pcobo/PCOBO0100P.do?tracseId=${tracseid}&tracseTme=${tracseTme}&crseTracseSe=C0061&trainstCstmrId=${trainstCstmrId}",
        "user-agent": UserAgent().chrome,
    }

    res = requests.get(url, params=params, headers=headers)
    # print(res.url)

    soup = BeautifulSoup(res.text, "html.parser")
    # print(soup.text)

    list1 = soup.find_all("dl", class_="item")
    for idx, item in enumerate(list1, 1):
        num = item.select_one(".tit").text.strip().split()[0]  # 회차
        date = item.select_one(".relList .con").text.strip()  # 훈련기간
        # 수강확정인원과 수강신청인원 같은 td 임
        enrollment_count = (
            item.select_one(".content .view tbody tr:nth-child(2) td")
            .text.strip()
            .split()
        )
        # print(f"수강신청 {enrollment_count}") ['수강확정인원:', '20명/', '수강신청인원(선발', '및', '검토대기인원포함):', '20명']
        confirmed_enrollment = enrollment_count[1].split("/")[0]  # 수강확정인원
        applied_enrollment = enrollment_count[5]  # 수강신청인원
        satisfaction_rate = (
            item.select_one(".content .view tbody tr:nth-child(3) td span")
            .text.strip()
            .split("준")[1]
        )  # 만족도
        employment_insurance_rate_3 = item.select_one(
            ".content .view tbody tr:nth-child(4) td"
        ).text.strip()  # 취업률 고용보험가입 3개월
        employment_insurance_rate_3 = re.sub(r"\s+", " ", employment_insurance_rate_3)
        employment_insurance_rate_6 = item.select_one(
            ".content .view tbody tr:nth-child(5) td"
        ).text.strip()  # 취업률 고용보험가입 6개월
        employment_insurance_rate_6 = re.sub(r"\s+", " ", employment_insurance_rate_6)
        employment_rate_3 = item.select_one(
            ".content .view tbody tr:nth-child(6) td"
        ).text.strip()  # 취업률 고용보험미가입 3개월
        employment_rate_3 = re.sub(r"\s+", " ", employment_rate_3)
        employment_rate_6 = (
            item.select_one(".content .view tbody tr:nth-child(7) td")
            .text.strip()
            .replace(r"\s+", " ")
        )  # 취업률 고용보험미가입 6개월
        employment_rate_6 = re.sub(r"\s+", " ", employment_rate_6)
        print(idx, "*" * 30)
        print(
            "\n".join(
                [
                    "기관명:{}",
                    "과정명:{}",
                    "회차:{}",
                    "훈련기간:{}",
                    "수강확정인원:{}",
                    "수강신청인원:{}",
                    "만족도:{}",
                    "취업률 고용보험가입 3개월:{}",
                    "취업률 고용보험가입 6개월:{}",
                    "취업률 고용보험미가입 3개월:{}",
                    "취업률 고용보험미가입 6개월:{}",
                ]
            ).format(
                info["company_title"],
                info["course_name"],
                num,
                date,
                confirmed_enrollment,
                applied_enrollment,
                satisfaction_rate,
                employment_insurance_rate_3,
                employment_insurance_rate_6,
                employment_rate_3,
                employment_rate_6,
            )
        )
