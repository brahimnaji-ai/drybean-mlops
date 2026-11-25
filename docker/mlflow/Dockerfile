FROM python:3.15.1-slim

ENV HOME=/home/mlflow \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN python -m pip install --no-cache-dir --disable-pip-version-check \
        mlflow==3.18.0 \
        boto3==1.44.4 \
    && useradd --create-home --uid 10001 mlflow \
    && mkdir -p /mlflow \
    && chown -R mlflow:mlflow /mlflow /home/mlflow

WORKDIR /mlflow
VOLUME ["/mlflow"]
USER 10001:10001
EXPOSE 5000
ENTRYPOINT ["mlflow"]
CMD ["server", "--host", "0.0.0.0", "--port", "5000"]
