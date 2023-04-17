# Tutorial

## How to run

```console
git clone https://github.com/SebasGarcia08/movielens-db.git

cd movielens-db

pip install -e .

python app.py
```

```console
docker build -t movielens .
```

```console
docker run \
    -e DB_USER="<user>" \
    -e DB_PWD="<pwd>" \
    -e DB_HOST="<host>" \
    -e DB_PORT=<port> \
    -e DB_SERVICE_NAME="<service name>" \
    -v ${PWD}/app.py:/app/app.py \
    -v ${PWD}/ddl.sql:/app/ddl.sql \
    -it \
    movielens python app.py
```
