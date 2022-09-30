## Police Incidents Data Pipeline

This is a toy pipeline that ingests the most recent [SFPD incident report data](https://datasf.gitbook.io/datasf-dataset-explainers/sfpd-incident-report-2018-to-present) to enable exploration of the broad question **"How well is the SFPD performing its function?"**

There are **three work artifacts** in this project:

- the prefect/pipeline code [demo](https://www.loom.com/share/d0aa46606c51407bbe73a2b8b87dbdf9)
- this [notion document](https://jongcleo.notion.site/Roote-System-Assignment-Police-Incidents-Data-79869f7c62534766a98aa46d3d0783e1) that details problem selection, approach etc.
- this colab notebook where I performed the [initial data exploration](https://colab.research.google.com/drive/1mcM9YOn6fSrAkoG8EbMgpCoBdlmufQDj?usp=sharing)
- this notebook where the viz is done (WIP) see [here](notebooks/visualization.ipynb)

## Setup

1. Set up Virtual Environment and install dependencies

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run to try the ingest pipeline locally and generate the demo.db sqlite database in your root folder
   `python3 ./flows/01_ingest.py`

3. Explore viz

```
jupyter lab
```
