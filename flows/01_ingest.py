import csv
import os

import pandas as pd
from prefect import flow, task
from sodapy import Socrata

client = Socrata("data.sfgov.org", None)
# id for the Police Dpt Incident Reports Data Set
# https://dev.socrata.com/foundry/data.sfgov.org/wg3w-h783
cwd = os.path.abspath(os.path.dirname(__file__))


@task
def extract() -> pd.DataFrame:
    # this feels super monkey but.. it works
    with open(os.path.join(cwd, "offset.csv"), "r", encoding="utf-8") as f:
        text = f.readline().strip()

    OFFSET = int(text)
    LIMIT = 100
    POLICE_INCIDENTS_DATA_SET_ID = "wg3w-h783"
    SORT_KEY = "incident_datetime"

    results = client.get(
        POLICE_INCIDENTS_DATA_SET_ID,
        limit=LIMIT,
        order=SORT_KEY,
        offset=OFFSET,
    )

    return pd.DataFrame.from_records(results)


@task
def add_minor_major_col(data: pd.DataFrame) -> pd.DataFrame:
    minor_incident_categories = (
        data[data["filed_online"] == True]
        .groupby(["incident_category", "incident_subcategory", "incident_description"])
        .size()
        .reset_index()
        .rename(columns={0: "count"})
    )

    # Probably a smell, should coerce type on df creation
    inc_cat = [str(x) for x in minor_incident_categories["incident_category"]]
    inc_subcat = [str(x) for x in minor_incident_categories["incident_subcategory"]]
    inc_desc = [str(x) for x in minor_incident_categories["incident_description"]]

    res = data.assign(
        is_minor=data["incident_category"].apply(lambda x: str(x) in inc_cat)
        & data["incident_subcategory"].apply(lambda x: str(x) in inc_subcat)
        & data["incident_description"].apply(lambda x: str(x) in inc_desc)
    )
    print(res.head())
    return res


@task
def remove_out_of_sf():
    pass


@task
def load():
    pass


@flow
def ingest():
    data = extract()
    add_minor_major_col(data)


ingest()
