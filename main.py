from extractor.GoYong24 import Extractor_Goyong24
import json


class Main:

    def __init__(self):
        pass

    def start_crawling(
        self,
        start_date,
        end_date,
        location_data,
        training_data,
    ):
        print(
            f"start_date: {start_date}, end_date: {end_date}, location_data: {location_data}, training_data: {training_data}"
        )
        extractor = Extractor_Goyong24(
            start_date,
            end_date,
            area=location_data,
            training_data=training_data,
        )
        extractor.start_crawling()


extractor = Extractor_Goyong24()
extractor.start_crawling()
