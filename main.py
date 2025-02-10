from goyong24_api import Use_API
import time


class Main:

    def __init__(self):
        pass

    async def start_crawling(
        self,
        start_date,
        end_date,
        location_data,
        training_data,
        keyword,
        update_status,
    ):
        api = Use_API(
            start_date,
            end_date,
            location_data,
            ["200101", "200102", "200103"],
            training_data,
            keyword,
        )
        start_time = time.time()
        await api.start_data_collection_async(update_status)
        update_status("작업 완료!")
        time.sleep(1)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print("코드 실행 시간: {:.6f} 초".format(elapsed_time))
