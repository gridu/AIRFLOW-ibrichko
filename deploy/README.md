### Set up credentials
Before docker compose up -d execuion you need to provide credentials.
create .env file with fillowing content(example values):
```
PG_AIRFLOW_USER=airflow
PG_AIRFLOW_PASSWD=airflow
PG_AIRFLOW_DB=airflow
AIRFLOW_VERSION=1.10.9
AIRFLOW_FERNET_KEY=GTt6PX_O5ZYEtmt-YJamGcrhPl6Q3bvPMN2vMmaTQBc=
DMD_USER_USERNAME=dmdadm
DMD_USER_PASSWD=P0gdp
DMD_USER_EMAIL=dmd@domain.tld
```
### Puge docker assets
```
cd path/to/docker-compose.yml
docker-compose down
docker volume rm dmd-airflow_elasticsearch-data dmd-airflow_grafana-data dmd-airflow_postgres-data
```

### Endpoints
Airflow Webserver: [127.0.0.1:8080](http://127.0.0.1:8080) 
Airflow flower: [127.0.0.1:5555](http://127.0.0.1:5555) 
Kibana: [127.0.0.1:5601](http://127.0.0.1:5601) 
Grafana: [127.0.0.1:3000](http://127.0.0.1:3000)
```