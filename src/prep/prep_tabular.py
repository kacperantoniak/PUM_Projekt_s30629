import pandas as pd
import os
from sklearn.preprocessing import StandardScaler

def prep_tabular(df, output_path, target_col="diabetes"):
    if target_col in df.columns:
        df = df.dropna(subset=[target_col])
        
    for col in df.select_dtypes(include=["number"]).columns:
        if col != target_col:
            df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include=["object", "category"]).columns:
        if col != target_col:
            if not df[col].mode().empty:
                df[col] = df[col].fillna(df[col].mode()[0])
                
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    cat_cols = [c for c in cat_cols if c != target_col]
    if len(cat_cols) > 0:
        df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
        
    num_cols = df.select_dtypes(include=["number"]).columns
    num_cols = [c for c in num_cols if c != target_col]
    if len(num_cols) > 0:
        scaler = StandardScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"Zapisano clean tabular do: {output_path}")