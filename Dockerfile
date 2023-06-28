FROM python:3.11-alpine
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY fastapi_pg_async_app /app/fastapi_pg_async_app
CMD ["python", "-m", "uvicorn", "--host", "0.0.0.0", "fastapi_pg_async_app.app:app"]

#FROM app_main as app_dev
#CMD ["python", "-m", "uvicorn", "--host", "0.0.0.0", "fastapi_pg_async_app.app:app", "--reload"]
