import great_expectations as gx
import pandas as pd
import json
import os

def run_ge_suite(df, cfg, dataset_name):
    context = gx.get_context(mode="ephemeral")
    
    data_asset = context.data_sources.add_pandas(f"ds_{dataset_name}").add_dataframe_asset(f"asset_{dataset_name}")
    batch_definition = data_asset.add_batch_definition_whole_dataframe(f"batch_{dataset_name}")
    batch = batch_definition.get_batch(batch_parameters={"dataframe": df})
    
    suite = context.suites.add(gx.ExpectationSuite(name=f"suite_{dataset_name}"))
    
    if len(df) > 0:
        suite.add_expectation(gx.expectations.ExpectTableRowCountToBeBetween(min_value=10))
    
    for col in cfg.get("required_columns", []):
        suite.add_expectation(gx.expectations.ExpectColumnToExist(column=col))

    rules = cfg.get("quality", {})
    
    pk = rules.get("primary_key")
    if pk and pk in df.columns:
        suite.add_expectation(gx.expectations.ExpectColumnValuesToBeUnique(column=pk))
        
    for col, col_rules in rules.get("column_rules", {}).items():
        if col in df.columns:
            if col_rules.get("max_null_percent") == 0:
                suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column=col))
                
            if "min_value" in col_rules or "max_value" in col_rules:
                suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(
                    column=col, 
                    min_value=col_rules.get("min_value"), 
                    max_value=col_rules.get("max_value")
                ))
            
            if "allowed_values" in col_rules:
                suite.add_expectation(gx.expectations.ExpectColumnValuesToBeInSet(
                    column=col, value_set=col_rules["allowed_values"]
                ))

    results = batch.validate(suite)
    
    os.makedirs("reports", exist_ok=True)
    log_path = f"reports/{dataset_name}_dq_log.json"
    
    log_data = {
        "dataset": dataset_name,
        "success": results.success,
        "statistics": results.statistics,
        "failed_assertions": []
    }
    
    for res in results.results:
        if not res.success:
            log_data["failed_assertions"].append({
                "expectation": getattr(res.expectation_config, 'type', 'Unknown'),
                "column": res.expectation_config.kwargs.get('column', 'N/A'),
                "details": res.result
            })
            
    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=4, default=str)
        
    if not results.success:
        errors = [getattr(res.expectation_config, 'type', 'Unknown') for res in results.results if not res.success]
        raise ValueError(f"DQ Failed! Sprawdź logi w {log_path}. Błędy: {errors}")
        
    print(f"DQ Passed! Logi zapisane w: {log_path}")
    return True