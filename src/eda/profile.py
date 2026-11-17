from ydata_profiling import ProfileReport

def generate_profile_report(df, output_path, minimal=True):
    if len(df) > 20000:
        df_sample = df.sample(n=20000, random_state=42)
    else:
        df_sample = df

    profile = ProfileReport(df_sample, title="Profiling Report", minimal=minimal)
    profile.to_file(output_path)
    print(f"Zapisano raport EDA do: {output_path}")