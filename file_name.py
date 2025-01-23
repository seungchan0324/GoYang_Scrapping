class File_Name_Selector:

    def __init__(self):
        pass

    def select(self, area, training_data, start_date_picker, end_date_picker, keyword):
        if " " in keyword:
            keyword = keyword.replace(" ", "-")
        if "%2C" in area:
            area_name = ",".join(area.split("서울+")[1] for area in area.split("%2C"))
        elif "전체" in area:
            area_name = "서울전체"
        else:
            area_name = area.split("서울+")[1]

        if "%2C" in training_data:
            training_name = ",".join(
                train.split("%7C")[1] for train in training_data.split("%2C")
            )
        elif "전체" in training_data:
            training_name = "훈련전체"
        else:
            training_name = training_data.split("%7C")[1]

        if "%28" in training_name:
            training_name = training_name.replace("%28", "")

        if "%29" in training_name:
            training_name = training_name.replace("%29", "")

        if "+" in training_name:
            training_name = training_name.replace("+", "_")

        if keyword != "":
            keyword += "_"

        if "-01-01" in str(start_date_picker) and "-12-31" in str(end_date_picker):
            year = str(start_date_picker).replace("-01-01", "")
            return f"{keyword}{area_name}_{training_name}_{year}년도"
        return f"{keyword}{area_name}_{training_name}_{start_date_picker}_to_{end_date_picker}"
