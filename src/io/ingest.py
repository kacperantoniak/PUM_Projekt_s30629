import pandas as pd
import os
import json

def ingest_tabular(cfg):
    df = pd.read_csv(cfg["source"])
    missing = set(cfg["required_columns"]) - set(df.columns)
    if missing:
        raise ValueError(f"Brakujące kolumny w tabular: {missing}")
    return df

def ingest_images(cfg):
    if not os.path.exists(cfg["source"]):
        raise FileNotFoundError(f"Brak pliku metadanych: {cfg['source']}")
    
    df = pd.read_csv(cfg["source"])
    missing = set(cfg["required_columns"]) - set(df.columns)
    if missing:
        raise ValueError(f"Brakujące kolumny w metadanych obrazów: {missing}")
        
    for img_dir in cfg.get("image_dirs", []):
        if not os.path.exists(img_dir):
            raise FileNotFoundError(f"Brak folderu z obrazami: {img_dir}")
            
    return df

def ingest_big(cfg):
    file_path = cfg["source"]
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Brak pliku Big Data: {file_path}")
    return file_path