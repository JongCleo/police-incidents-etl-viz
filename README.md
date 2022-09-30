## Police Incidents Data Pipeline

This is a toy pipeline that ingests the most recent [SFPD incident report data](https://datasf.gitbook.io/datasf-dataset-explainers/sfpd-incident-report-2018-to-present) to enable exploration of the broad question **"How well is the SFPD performing its function?"**

There are **three work artifacts** in this project:

- this repo
- this [notion document](https://jongcleo.notion.site/Roote-System-Assignment-Police-Incidents-Data-79869f7c62534766a98aa46d3d0783e1) that details problem selection, approach etc.
- this colab notebook where I performed the [initial data exploration](https://colab.research.google.com/drive/1mcM9YOn6fSrAkoG8EbMgpCoBdlmufQDj?usp=sharing)

## Setup

Create a `dev.env` file from `sample.env`

1. Set up Virtual Environment and install dependencies

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
