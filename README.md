# Feedback Ingestion API

This repository contains three codebases :

- The code for setting up the AFC API, for ingesting and 
- The code for simulating traffic to the AFC API
- The notebook directory containing 
## Ports

The CrispyAI API uses  port 80 locally. The containerized version uses port 8080.
The MongoDB database uses port 27017.
Ngrok uses port 4040.
## Setup (Local execution)

These instructions are for running the API on a local computer without connecting to the internet.

## Setup (Containerized)

These instructions are for running the API on a container along with a MongoDB and a Ngrok container for exposing the API to the internet.

### EXECUTE LOCALLY
```
uvicorn main:app --host <host> --port <port>
```

Exemple:
```
uvicorn main:app --host 0.0.0.0 --port 80
```
### SET UP DOCKER

Install Docker Desktop

```
docker-compose up
```


## Configuration
```ini
[API]
endpoint_url = http://localhost:8080/afc/api
endpoint_url_authentication = http://localhost:8080/afc/signup

[API_AUTH (MASTER)]
API_EMAIL= ABCD # Master email
API_PASSWORD= 1234 # Master password
API_SECRET=

