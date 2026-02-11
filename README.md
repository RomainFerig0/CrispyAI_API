# CrispyAI

## LAUNCH THE API

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

