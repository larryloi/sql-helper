# sql_helper
## Introduction
It is a tools to simulate rdbms activities, there is 2 type of databases below support currently 
- MySQL
- SQL Server

## How to use?

### Build the images
```shell
make build.base
make build.app
```

### Prepare your config
- MySQL 
  - update mysql_inventory/config.yml

- SQL Server
  - update mssql_inventory/config.yml

### What we can config
sample config 
```yaml
services:
  default_config: &default
    DATABASE_URL: mysql+pymysql://sql_helper:Abcd1234@dev01.kaskade.local:3306/inventory
    TIMEOUT_SECONDS: 30
    MAX_RETRIES: 3

  supplier_creator:
    <<: *default
    WAIT_TIME: [3600, 7200]        ## wait interval that random arrange between these 2 figure
    # WAIT_TIME: [1, 3]
    TYPE: ['music','vehicle']      ## fake data array, only these 2 type, no need to change
    NUM_PROCESSES: 1               ## Number of processes will be spawn
    RETENTION_HOUR: 2160           ## data retention by hour

  my_orders_creator:
    <<: *default
    NUM_PROCESSES: 100
    WAIT_TIME: [1,7]
    TYPE: [{"name":"vehicle", "provider":"VehicleProvider", "method":"fake.vehicle_object()"},{"name":"music","provider":"MusicProvider","method":"fake.music_genre_object()"}]
    STATUS:
      created: 50
      pending: 8
      shipped: 20
      delivered: 2
      others: 12
    RETENTION_HOURS: 240
```

### Run test
- For MySQL
```shell
docker compose --profile mysql up -d
```

- For SQL Server
```shell
docker compose --profile mssql up -d
```