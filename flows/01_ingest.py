import csv
import imp
import os

import pandas as pd
from prefect import flow, task
from sodapy import Socrata
from sqlalchemy import create_engine, inspect

cwd = os.path.abspath(os.path.dirname(__file__))
# ip = imp.load_source("models", os.path.join(cwd, "../models/incident_parts.py"))

client = Socrata("data.sfgov.org", None)


def get_current_offset() -> int:
    # this feels super monkey but.. it works
    with open(os.path.join(cwd, "offset.csv"), "r", encoding="utf-8") as f:
        offset = f.readline().strip()
    return int(offset)


@task
def extract(offset: int) -> pd.DataFrame:

    OFFSET = offset
    LIMIT = 50000
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
def insert_or_update(new_data: pd.DataFrame) -> None:
    dbengine = create_engine("sqlite:///demo.db")

    if not (inspect(dbengine).has_table("incident_parts")):
        new_data.to_sql("incident_parts", dbengine)
        return

    new_data.to_sql("potential_updates_table", dbengine, if_exists="replace")
    update_query = """
        UPDATE incident_parts as ip
        SET resolution = ip.resolution
        FROM potential_updates_table as put
        WHERE ip.row_id = put.row_id
    """
    insert_query = """
    INSERT INTO incident_parts (
	row_id ,
    incident_datetime,
    incident_date,
    incident_time,
    incident_year,
    incident_day_of_week ,
    report_datetime,
    incident_id ,
    incident_number,
    cad_number,
    report_type_code,
    report_type_description,
    filed_online,
    incident_code,
    incident_category,
    incident_subcategory,
    incident_description,
    is_minor,
    resolution,
    intersection,
    cnn,
    police_district,
    analysis_neighborhood,
    supervisor_district,
    latitude,
    longitude )
SELECT 
	row_id ,
    incident_datetime,
    incident_date,
    incident_time,
    incident_year,
    incident_day_of_week ,
    report_datetime,
    incident_id ,
    incident_number,
    cad_number,
    report_type_code,
    report_type_description,
    filed_online,
    incident_code,
    incident_category,
    incident_subcategory,
    incident_description,
    is_minor,
    resolution,
    intersection,
    cnn,
    police_district,
    analysis_neighborhood,
    supervisor_district,
    latitude,
    longitude 
FROM 	potential_updates_table
WHERE row_id not in (select row_id from incident_parts)"""
    with dbengine.begin() as conn:
        conn.execute(update_query)
        conn.execute(insert_query)

    # ip.IncidentParts.__table__.create(bind=engine, checkfirst=True)


@task
def update_offset(offset_increment: int) -> None:
    with open(os.path.join(cwd, "offset.csv"), "w", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([str(offset_increment)])


@flow
def ingest():
    offset = get_current_offset()
    data = extract(offset)
    minor_major_col_added = add_minor_major_col(data)
    invalids_removed = remove_out_of_sf(minor_major_col_added)
    compatible_data = make_compatible_with_sqlite(invalids_removed)
    insert_or_update(compatible_data)
    update_offset(offset + len(data))


ingest()
