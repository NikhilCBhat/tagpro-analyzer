def string_date_to_attributes(date):
    hour, minute, second = date[:date.rfind(".")].split("T")[1].split(":")
    year, month, day = date.split("T")[0].split("-")  

    return [int(x) for x in [second, minute, hour, day, month, year]]

def show_batch(dataset):
    for batch, label in dataset.take(1):
        print("Label: {}".format(label))
        for key, value in batch.items():
            print("{:20s}: {}".format(key,value.numpy()))