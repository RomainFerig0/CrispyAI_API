# CrispyAI

## SET THE .ENV FILE

The following values are mandatory:
DATABRICKS_HOST=https://dbc-5e4ae4b7-6437.cloud.databricks.com
DATABRICKS_CLIENT_ID=76e8f188-e3e3-4093-bf6a-a16ffd45acdd
DATABRICKS_CLIENT_SECRET=dose4efbeed57b30c3a11c44e36ccd0447fc

The following values are based on your convenience:
API_EMAIL=
API_PASSWORD=
API_SECRET=

## LAUNCH THE API

### EXECUTE LOCALLY
```
uvicorn main:app --host 0.0.0.0 --port 80
```
### SET UP THE DOCKER FILE
```
docker build -t myapi .
docker run --env-file .env -p 8080:8080 myapi
```