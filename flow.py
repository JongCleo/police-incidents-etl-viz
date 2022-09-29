import csv

from prefect import flow, task


@task
def extract(path):
    with open(path, "r") as f:
        text = f.readline().strip()
    data = [int(i) for i in text.split(",")]
    return data


@task
def transform(data):
    tdata = [i + 1 for i in data]
    return tdata


@task
def load(data, path):
    with open(path, "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(data)


@flow
def flow_try():
    # should note that Task results are caches in memory
    # and persisted to PREFECT_LOCAL_STORAGE_PATH

    data = extract("values.csv")
    # think of the return value as the prefect task, not as the return value itself
    # as proof, try doing
    # print(data)

    tranformed_data = transform(data)
    result = load(tranformed_data, "transformed_values.csv")
    # flow.visualize()


flow_try()
