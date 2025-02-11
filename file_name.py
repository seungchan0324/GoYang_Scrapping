import json


class File_Name_Selector:

    with open("./json/location_api.json", "r", encoding="utf-8") as f:
        location_datas = json.load(f)
    location_data = {
        location_data["location_code"]: location_data["location"]
        for location_data in location_datas
    }

    with open("./json/training_api.json", "r", encoding="utf-8") as f:
        training_datas = json.load(f)
    training_data = {
        training_data["training_code"]: training_data["training_type"]
        for training_data in training_datas
    }

    def __init__(self):
        pass

    def select(self, areas, trainings, start_date_picker, end_date_picker, keyword):
        if keyword:
            keyword = keyword.replace(" ", "-")
            keyword += "_"

        area_name = ",".join(self.location_data[area] for area in areas)

        training_name = ",".join(self.training_data[training] for training in trainings)
        if training_name == "":
            training_name = "훈련전체"

        st_date_str = str(start_date_picker)
        ed_date_str = str(end_date_picker)
        if "-01-01" in st_date_str and "-12-31" in ed_date_str:
            st_year = st_date_str.replace("-01-01", "")
            ed_year = ed_date_str.replace("-12-31", "")
            if st_year == ed_year:
                return f"{keyword}{area_name}_{training_name}_{st_year}년도"
            else:
                return f"{keyword}{area_name}_{training_name}_{st_year}~{ed_year}년도"

        return f"{keyword}{area_name}_{training_name}_{start_date_picker}_to_{end_date_picker}"
