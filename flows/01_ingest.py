import csv
import imp
import os
import sys

import pandas as pd
from prefect import flow, task
from sodapy import Socrata
from sqlalchemy import create_engine

cwd = os.path.abspath(os.path.dirname(__file__))
# ip = imp.load_source("models", os.path.join(cwd, "../models/incident_parts.py"))

client = Socrata("data.sfgov.org", None)


@task
def extract() -> pd.DataFrame:
    # this feels super monkey but.. it works
    with open(os.path.join(cwd, "offset.csv"), "r", encoding="utf-8") as f:
        text = f.readline().strip()

    OFFSET = int(text)
    LIMIT = 100
    # id for the Police Dpt Incident Reports Data Set
    # https://dev.socrata.com/foundry/data.sfgov.org/wg3w-h783
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
def remove_out_of_sf(data: pd.DataFrame) -> pd.DataFrame:
    return data[data["police_district"].apply(lambda x: str(x) != "Out of SF")]


@task
def make_compatible_with_sqlite(data: pd.DataFrame) -> pd.DataFrame:
    data["filed_online"] = data["filed_online"].astype("str")
    data["is_minor"] = data["is_minor"].astype("str")
    data = data.drop("point", axis=1)
    return data


@task
def load(data: pd.DataFrame) -> None:
    dbengine = create_engine("sqlite:///demo.db")
    # ip.IncidentParts.__table__.create(bind=engine, checkfirst=True)
    data.to_sql("incident_parts", dbengine, if_exists="append", index=False)


@task
def update_offset() -> None:
    pass


@flow
def ingest():
    data = extract()
    minor_major_col_added = add_minor_major_col(data)
    invalids_removed = remove_out_of_sf(minor_major_col_added)
    compatible_data = make_compatible_with_sqlite(invalids_removed)
    load(compatible_data)


ingest()
