import csv
import datetime

from prefect import flow, task
from prefect.deployments import Deployment
from prefect.task_runners import SequentialTaskRunner


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


@flow(name="first flow", description="basic shit", task_runner=SequentialTaskRunner())
# the task_runner can be concurrent or sequential
def flow_try(filename):
    # should note that Task results are caches in memory
    # and persisted to PREFECT_LOCAL_STORAGE_PATH

    data = extract(filename)
    # think of the return value as the prefect task, not as the return value itself
    # as proof, try doing
    # print(data)

    tranformed_data = transform(data)
    result = load(tranformed_data, filename)
    # flow.visualize()


# when creating flows from the Prefect Orion API, must use named parameters
# cannot be positional
flow_try(filename="values.csv")
