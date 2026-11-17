from airflow.decorators import dag, task
from pendulum import datetime
import pandas as pd
import yaml
import os
import json

# Importy z naszej struktury
from src.io.ingest import ingest_tabular, ingest_images, ingest_big
from src.dq.ge_suite import run_ge_suite
from src.eda.profile import generate_profile_report
from src.prep.prep_tabular import prep_tabular
from src.prep.prep_images import prep_images
from src.prep.prep_big import prep_big

@dag(schedule=None, start_date=datetime(2025, 11, 1), catchup=False, tags=["ingest", "eda", "prep"])
def ingest_eda_prep():

    datasets = ["tabular", "images", "bigdata"]

    for ds in datasets:
        
        @task(task_id=f"ingest_{ds}")
        def ingest_task(ds_name: str = ds):
            with open(f"include/config/{ds_name}.yaml") as f:
                cfg = yaml.safe_load(f)
            
            if ds_name == "tabular":
                df = ingest_tabular(cfg)
                tmp_path = f"data/raw/{ds_name}_ingested.parquet"
                df.to_parquet(tmp_path, index=False)
                return tmp_path
            elif ds_name == "images":
                df = ingest_images(cfg)
                tmp_path = f"data/raw/{ds_name}_ingested.parquet"
                df.to_parquet(tmp_path, index=False)
                return tmp_path
            elif ds_name == "bigdata":
                return ingest_big(cfg)

        @task(task_id=f"dq_{ds}")
        def dq_task(file_path: str, ds_name: str = ds):
            with open(f"include/config/{ds_name}.yaml") as f:
                cfg = yaml.safe_load(f)
            
            if ds_name == "bigdata":
                df = pd.read_json(file_path, lines=True, nrows=50000)
            else:
                df = pd.read_parquet(file_path)
                
            run_ge_suite(df, cfg, dataset_name=ds_name)
            return file_path

        @task(task_id=f"eda_{ds}")
        def eda_task(file_path: str, ds_name: str = ds):
            if ds_name == "bigdata":
                #probka 20k do EDA
                df = pd.read_json(file_path, lines=True, nrows=20000)
            else:
                df = pd.read_parquet(file_path)
                
            report_path = f"reports/{ds_name}_profile.html"
            generate_profile_report(df, report_path)
            return file_path

        @task(task_id=f"prep_{ds}")
        def prep_task(file_path: str, ds_name: str = ds):
            with open(f"include/config/{ds_name}.yaml") as f:
                cfg = yaml.safe_load(f)
                
            output_path = f"data/clean/clean_{ds_name}.parquet"
            
            if ds_name == "tabular":
                df = pd.read_parquet(file_path)
                prep_tabular(df, output_path, target_col="diabetes")
            elif ds_name == "images":
                df = pd.read_parquet(file_path)
                prep_images(df, cfg)
            elif ds_name == "bigdata":
                prep_big(file_path, output_path)
                
            return output_path

        data = ingest_task()
        dq = dq_task(data)
        eda = eda_task(data)
        clean = prep_task(data)
        
        dq >> eda >> clean

ingest_eda_prep()