from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import *

Base = declarative_base()


class IncidentParts(Base):
    __tablename__ = "incident_parts"
    row_id = Column(Integer, primary_key=True)
    incident_datetime = Column(DateTime)
    incident_date = Column(DateTime)
    incident_time = Column(String)
    incident_year = Column(String)
    incident_day_of_week = Column(String)
    report_datetime = Column(String)
    incident_id = Column(String)
    incident_number = Column(String)
    cad_number = Column(String)
    report_type_code = Column(String)
    report_type_description = Column(String)
    filed_online = Column(Boolean)
    incident_code = Column(String)
    incident_category = Column(String)
    incident_subcategory = Column(String)
    incident_description = Column(String)
    is_minor = Column(Boolean)
    resolution = Column(String)
    intersection = Column(String)
    cnn = Column(String)
    police_district = Column(String)
    analysis_neighborhood = Column(String)
    supervisor_district = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    point = Column(String)


import sys

print("In module products sys.path[0], __package__ ==", sys.path[0], __package__)
