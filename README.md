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
    -e DB_USER="P09551_1_3" \
    -e DB_PWD="P09551_1_3_20231" \
    -e DB_HOST="200.3.193.24" \
    -e DB_PORT=1522 \
    -e DB_SERVICE_NAME="ESTUD" \
    -v ${PWD}/app.py:/app/app.py \
    -v ${PWD}/ddl.sql:/app/ddl.sql \
    -it \
    movielens python app.py
```
