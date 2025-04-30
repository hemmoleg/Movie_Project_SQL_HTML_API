from storage.init_db import engine
from sqlalchemy import text


def get_users():
    """Retrieve all movies for a specific user from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT id, name FROM users "))
        users = result.fetchall()

    return [{"id": row[0], "name": row[1]} for row in users]


def add_user(name):
    """Add a new user to the database."""
    with engine.connect() as connection:
        try:
            connection.execute(text(
                "INSERT INTO users (name) VALUES (:name)"),
                {"name": name}
            )
            connection.commit()
            print(f"User '{name}' added successfully.")
        except Exception as e:
            print(f"Error: {e}")

