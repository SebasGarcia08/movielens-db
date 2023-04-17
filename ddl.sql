CREATE TABLE genre(
  genre_id INT PRIMARY KEY,
  genre_name VARCHAR(100)
);

CREATE TABLE movies (
  movie_id INT PRIMARY KEY,
  title VARCHAR(255),
  imdb_url VARCHAR(255),
  num_genres INT
);

CREATE TABLE movie_genres(
  movie_genre_id INT PRIMARY KEY,
  movie_id INT,
  genre_id INT,
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
  FOREIGN KEY (genre_id) REFERENCES genre(genre_id)
);

CREATE TABLE users (
  user_id INT PRIMARY KEY,
  age INT,
  gender CHAR(1),
  occupation VARCHAR(255),
  zip_code VARCHAR(10)
);

CREATE TABLE ratings (
  rating_id INT PRIMARY KEY,
  user_id INT,
  movie_id INT,
  rating INT,
  timestamp INT,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);