FROM apache/airflow:2.10.0
USER airflow
RUN pip install --no-cache-dir \
    great-expectations \
    ydata-profiling \
    scikit-learn \
    pyarrow \
    pandas \
    pyyaml