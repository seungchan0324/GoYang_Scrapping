from extractor.GoYong24 import Extractor_Goyong24
import json


class Main:

    def __init__(self):
        pass

    def start_crawling(self):
        extractor = Extractor_Goyong24(self.location_json, self.training_json)
        extractor.start_crawling()
