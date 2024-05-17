FROM apache/airflow:latest
FROM python:3.8.5

# Install DBT
RUN pip install -U pip
RUN pip install dbt==0.17.2


COPY requirements/ /tmp/requirements
RUN pip install --upgrade pip && \
    pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /tmp/requirements/requirements.txt
