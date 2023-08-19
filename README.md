# Checkbox Test Project

## Dependencies

- [docker](https://docs.docker.com/get-docker/)

## Api envinronment

- ### create `.env` file in `root` folder

#### `.env` example

```dosini
ENVIRONMENT=LOCAL
DATABASE_URL=postgresql://postgres:password@db:5432/webshop
authjwt_secret_key=dd10c933a88919a18bb1074b6b0250e11caab74221cddad45853b492341108ef
```

- ### create `.db.env` file in `root` folder

#### `.db.env` example

```dosini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=webshop
```

## Build

```shell
docker-compose build
```

## Start

```shell
docker-compose up -d
```

## To apply migrations

```shell
docker-compose exec web alembic upgrade head
```

## Open API Documentaion

```shell
http://localhost:8000/docs
```

## Pytest Tests

### To run tests use

```shell
docker-compose exec web pytest
```
