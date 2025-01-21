class File_Name_Selector:

    def __init__(self):
        pass

    def select(self, area, training_data, start_date_picker, end_date_picker):
        if "%C2" in area:
            area_name = ",".join(area.split("서울+")[1] for area in area.split("%C2"))
        elif "전체" in area:
            area_name = "서울전체"
        else:
            area_name = area.split("서울+")[1]

        if "%C2" in training_data:
            training_name = ",".join(
                train.split("%7C")[1] for train in training_data.split("%C2")
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

        return f"{area_name}_{training_name}_{start_date_picker}_to_{end_date_picker}"
