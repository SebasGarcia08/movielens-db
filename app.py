import os
import os.path as osp
import typing as ty
import urllib.request
import zipfile

import numpy as np
import oracledb
import pandas as pd

genres_columns = [
    'unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary',
    'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
    'Thriller', 'War', 'Western'
]

DATA_FOLDER = "data/ml-100k"

oracledb.init_oracle_client()

connection = oracledb.connect(
   user=os.environ['DB_USER'],
   password=os.environ['DB_PWD'],
   host=os.environ['DB_HOST'],
   port=int(os.environ['DB_PORT']),
   service_name=os.environ['DB_SERVICE_NAME'],
)

cursor = connection.cursor()

def download_data(url: str, save_path: str) -> None:
    # Specify the directory to save the downloaded file

    # Download the dataset
    zip_file_path = f"{save_path}.zip"
    if not osp.exists(zip_file_path):
        urllib.request.urlretrieve(url, zip_file_path)

    os.makedirs("./data", exist_ok=True)

    # Extract the downloaded ZIP file
    if not osp.exists(save_path):
        with zipfile.ZipFile(save_path, 'r') as zip_ref:
            zip_ref.extractall('./data')

    print('MovieLens 100K dataset downloaded and extracted successfully!')

def read_dataset(data_folder: str, genres_columns: ty.List[str]) -> ty.Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    movies_path = osp.join(data_folder, "u.item")
    user_path = osp.join(data_folder, "u.user")
    ratings_path = osp.join(data_folder, "u.data")


    movies_df = pd.read_csv(movies_path, sep='|', encoding='latin-1', header=None,
                           names=['movie_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL', 'unknown',
                                  'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary',
                                  'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
                                  'Thriller', 'War', 'Western'])
    movies_df[genres_columns] = movies_df[genres_columns].astype(np.int8)
    # Read users.data file into a DataFrame
    users_df = pd.read_csv(user_path, sep='|', encoding='latin-1', header=None,
                          names=['user_id', 'age', 'gender', 'occupation', 'zip_code'])

    # Read ratings.data file into a DataFrame
    ratings_df = pd.read_csv(ratings_path, sep='\t', encoding='latin-1', header=None,
                            names=['user_id', 'movie_id', 'rating', 'timestamp'])

    # Display the first few rows of each DataFrame
    print('Movies DataFrame:')
    print(movies_df.head())
    print('\nUsers DataFrame:')
    print(users_df.head())
    print('\nRatings DataFrame:')
    print(ratings_df.head())
    return movies_df, users_df, ratings_df

def group_genres(movies_df: pd.DataFrame, genres_columns: ty.List[str]) -> pd.DataFrame:
    movies_df['genre'] = movies_df[genres_columns].apply(lambda x: ','.join(x[x==1].index), axis=1)
    movies_df['num_genres'] = movies_df[genres_columns].apply(lambda x: len((x[x==1].index)), axis=1)
    # Drop the individual genre columns
    movies_df = movies_df.drop(columns=genres_columns)
    return movies_df

def create_movie_genre_table(movies_df: pd.DataFrame, genres_2_id: ty.Dict[str, int]) -> pd.DataFrame:
    movie_genres = dict(movie_id=[], genre_id=[])

    for _, row in movies_df.iterrows():
        genres = row['genre'].split(',')
        for genre in genres:
            movie_genres["movie_id"].append(row['movie_id'])
            movie_genres['genre_id'].append(genres_2_id[genre])

    movie_genres_df = pd.DataFrame(movie_genres)
    return movie_genres_df

def get_tables(url) -> ty.Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    download_data(url, DATA_FOLDER)
    movies_df, users_df, ratings_df = read_dataset(DATA_FOLDER, genres_columns)
    genres = pd.DataFrame(dict(genre_name=genres_columns)).reset_index(drop=False)
    genres.rename(columns={'index': 'genre_id'}, inplace=True)
    genres_2_id = dict(zip(genres.genre_name, genres.genre_id))
    movies_df = group_genres(movies_df, genres_columns)
    movie_genres_df = create_movie_genre_table(movies_df, genres_2_id)
    movie_genres_df['movie_genre_id'] = movie_genres_df.index
    movies_df.drop(columns=['genre'], inplace=True)
    ratings_df['rating_id'] = ratings_df.index
    return movies_df, users_df, ratings_df, genres, movie_genres_df


def create_schema(sql_code_path: str) -> None:
    with open(sql_code_path, 'r') as f:
        ddl = f.read()
    statements = ddl.split(';')

    table_names = ['genre', 'movies', 'movie_genres', 'users', 'ratings']

    for table_name in table_names:
        cursor.execute(f"DROP TABLE {table_name} CASCADE CONSTRAINTS")

    for statement in statements[:-1]:
        print("Creating schema...")
        print(statement)
        cursor.execute(statement)

def main() -> None:
    # URL to download the MovieLens 100K dataset
    url = 'http://files.grouplens.org/datasets/movielens/ml-100k.zip'
    movies_df, users_df, ratings_df, genres, movie_genres_df = get_tables(url)
    print("Movies DataFrame:")
    print(movies_df.head())
    print("Movie Genres DataFrame:")
    print(movie_genres_df.head())
    print("Genres DataFrame:")
    print(genres.head())
    print("Users DataFrame:")
    print(users_df.head())
    print("Ratings DataFrame:")
    print(ratings_df.head())

    create_schema("ddl.sql")

    genre_data = [tuple(x) for x in genres.values]
    cursor.executemany('INSERT INTO genre (genre_id, genre_name) VALUES (:1, :2)', genre_data)
    connection.commit()

    movies_df['release_date'] = movies_df['release_date'].astype("datetime64[ns]").astype(str)
    movies_df['video_release_date'] =  movies_df['video_release_date'].astype("datetime64[ns]").astype(str)
    movies_df['IMDb_URL'] = movies_df['IMDb_URL'].astype(str)
    movies_df.drop(columns=['release_date', 'video_release_date'], inplace=True)
    print(movies_df.info())
    
    movies_data = [tuple(x) for x in movies_df.values]
    cursor.executemany('INSERT INTO movies (movie_id, title, imdb_url, num_genres) VALUES (:1, :2, :3, :4)', movies_data)
    connection.commit()

    print(movie_genres_df.info())
    movies_genres_data = [tuple(map(int, x)) for x in movie_genres_df[['movie_genre_id', 'movie_id', 'genre_id']].values]
    cursor.executemany('INSERT INTO movie_genres (movie_genre_id, movie_id, genre_id) VALUES (:1, :2, :3)', movies_genres_data)
    connection.commit()

    users_data = [tuple(x) for x in users_df.values]
    cursor.executemany('INSERT INTO users (user_id, age, gender, occupation, zip_code) VALUES (:1, :2, :3, :4, :5)', users_data)
    connection.commit()

    print(ratings_df.info())
    ratings_data = [tuple(map(int, x)) for x in ratings_df[["rating_id", "user_id", "movie_id", "rating", "timestamp"]].values]
    cursor.executemany('INSERT INTO ratings (rating_id, user_id, movie_id, rating, timestamp) VALUES (:1, :2, :3, :4, :5)', ratings_data)
    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()