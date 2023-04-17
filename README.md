# Tutorial

## How to run

git clone https://github.com/SebasGarcia08/movielens-db.git

cd movielens-db

pip install -e .

python app.py


docker build -t movielens .

docker run \
    -v ${PWD}/app.py:/app/app.py \
    -v ${PWD}/ddl.sql:/app/ddl.sql \
    -it \
    movielens python app.py

