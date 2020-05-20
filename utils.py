def string_date_to_attributes(date):
    hour, minute, second = date[:date.rfind(".")].split("T")[1].split(":")
    year, month, day = date.split("T")[0].split("-")  

    return [int(x) for x in [second, minute, hour, day, month, year]]