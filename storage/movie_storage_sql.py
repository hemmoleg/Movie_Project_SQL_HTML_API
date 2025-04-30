from storage.init_db import engine
from sqlalchemy import text


def get_movies_for_user(user_id):
    """Retrieve all movies for a specific user from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT title, year, rating, poster, user_id "
                 "FROM movies "
                 "WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        movies = result.fetchall()

    return {row[0]: {"year": row[1], "rating": row[2], "poster": row[3], "user_id": row[4]} for row in movies}


def add_movie(title, year, rating, poster, user_id):
    """Add a new movie to the database."""
    with engine.connect() as connection:
        try:
            connection.execute(text(
                "INSERT INTO movies (title, year, rating, poster, user_id) VALUES (:title, :year, :rating, :poster, :user_id)"),
                {"title": title, "year": year, "rating": rating, "poster": poster, "user_id": user_id}
            )
            connection.commit()
        except Exception as e:
            print(f"Error: {e}")


def delete_movie(title, user_id):
    with engine.connect() as connection:
        try:
            connection.execute(
                text("DELETE FROM movies WHERE title = :title AND user_id = user_id"),
                {"title": title, "user_id": user_id}
            )
            connection.commit()
        except Exception as e:
            print(f"Error: {e}")


def update_movie(title, new_rating):
    with engine.connect() as connection:
        try:
            connection.execute(
                text("UPDATE movies SET rating = :rating WHERE title = :title"),
                {"title": title, "rating": new_rating}
            )
            connection.commit()
            print(f"Movie '{title}' updated successfully.")
        except Exception as e:
            print(f"Error: {e}")

