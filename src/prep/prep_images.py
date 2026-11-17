import pandas as pd
import os
from sklearn.model_selection import train_test_split

def prep_images(df, cfg, output_dir="data/clean"):
    os.makedirs(output_dir, exist_ok=True)

    df['filepath'] = df['image_id'].apply(lambda x: f"data/raw/images/HAM10000_images_part_1/{x}.jpg")
    
    # podzial train/validate 80/20 ze stratyfikacja
    stratify_col = cfg["quality"]["target_col"] if cfg["quality"].get("target_col") in df.columns else None
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42, stratify=stratify_col)
    
    train_path = os.path.join(output_dir, "images_train_manifest.csv")
    val_path = os.path.join(output_dir, "images_val_manifest.csv")
    
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    print(f"Zapisano manifesty: {train_path}, {val_path}")