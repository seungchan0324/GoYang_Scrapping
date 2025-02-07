from goyong24 import Extractor_Goyong24
import time


class Main:

    def __init__(self):
        pass

    def start_crawling(
        self, start_date, end_date, location_data, training_data, keyword, update_status
    ):
        extractor = Extractor_Goyong24(
            start_date,
            end_date,
            area=location_data,
            training_data=training_data,
            keyword=keyword,
        )
        start_time = time.time()
        extractor.start_crawling(update_status)
        update_status("작업 완료!")
        time.sleep(1)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print("코드 실행 시간: {:.6f} 초".format(elapsed_time))
