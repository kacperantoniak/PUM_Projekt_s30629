import pandas as pd
import os
import json
import pyarrow as pa
import pyarrow.parquet as pq

def prep_big(file_path, output_path, chunk_size=100000):
    """Przetwarza Big Data strumieniowo, filtruje i zapisuje do Parquet."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    writer = None
    rows_kept = 0
    chunk_data = []

    def process_chunk(data_list):
        nonlocal writer, rows_kept
        if not data_list:
            return
        
        chunk = pd.DataFrame(data_list)
        
        if 'sentence' in chunk.columns:
            chunk = chunk[chunk['sentence'].astype(str).str.len() > 10]
            
        if not chunk.empty:
            table = pa.Table.from_pandas(chunk)
            
            if writer is None:
                writer = pq.ParquetWriter(output_path, table.schema)
                
            writer.write_table(table)
            rows_kept += len(chunk)

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if not line:
                continue
            
            try:
                record = json.loads(line)
                chunk_data.append(record)
            except json.JSONDecodeError:
                continue
                
            if len(chunk_data) >= chunk_size:
                process_chunk(chunk_data)
                chunk_data = []
                
    if chunk_data:
        process_chunk(chunk_data)
        
    if writer:
        writer.close()
        
    print(f"Big Data przygotowane. Zapisano {rows_kept} wierszy do {output_path}")