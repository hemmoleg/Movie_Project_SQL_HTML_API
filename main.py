import json
import random
import matplotlib.pyplot as plt
import os

import requests
from requests.exceptions import ConnectionError

from storage import user_storage_sql, movie_storage_sql
from fuzzywuzzy import process


def get_input(expected_type, text):
    while True:
        try:
            user_input = expected_type(input(text))
            if user_input == "":
                print("Please enter a value")
            else:
                return user_input
        except ValueError:
            if expected_type is str:
                print("Please enter a string")
            elif expected_type is int:
                print("Please enter an integer value")
            elif expected_type is float:
                print("Please enter an integer or float value")


def print_menu(user):
    print(f"********** {user["name"]}'s Movies Database **********\n")
    print("Menu:")
    print("0. End program")
    print("1. List movies")
    print("2. Add movie")
    print("3. Delete movie")
    print("4. Update movie")
    print("5. Create Website")
    print("6. Stats")
    print("7. Random movie")
    print("8. Search movie")
    print("9. Movies sorted by rating")
    print("10. Generate histogram of movie ratings")
    print("11. Movies sorted by year")


def end_program(_, __):
    exit()


def list_movies(movies, _):
    print(f"{len(movies)} movies in total")
    for movie, info in movies.items():
        print(f"{movie} ({info["year"]}): {info["rating"]}")

    input("Press Enter to go back to main menu")


def add_movie(movies, user):
    print("Add movie")
    title = get_input(str, "Please enter movie title: ")

    if title in movies:
        print(f"Movie {title} already exist!")
        return

    try:
        response = requests.post(f"https://www.omdbapi.com/?apikey=9d3237b8&t={title}")
    except ConnectionError:
        print("No connection to API!")
        return

    response = json.loads(response.text)
    if response["Response"] == "False":
        print("Movie not found in OMDb")
        return

    movie_storage_sql.add_movie(title, response["Year"], response["imdbRating"], response["Poster"], user["id"])
    movies[title] = {"rating": float(response["imdbRating"]),
                     "year": response["Year"],
                     "poster": response["Poster"],
                     "user": user["id"]}

    print(f"Movie {title} added to {user["name"]}'s collection!")
    input("Press Enter to go back to main menu")


def delete_movie(movies, user):
    print("Delete movie")
    title = get_input(str, "Please enter movie title to delete: ")
    if title in movies.keys():
        del movies[title]
        print(f"Movie {title} removed from {user["name"]}'s collection!")
        movie_storage_sql.delete_movie(title, user)
    else:
        print(f"Movie {title} doesnt exist")

    input("Press Enter to go back to main menu")


def update_movie(movies, _):
    """
    update a movie with a new rating
    :param movies:
    """
    print("Update movie")
    title = get_input(str, "Please enter movie title to update: ")
    if title in movies.keys():
        new_rating = get_input(float, f"Please enter the new rating for {title}: ")
        movies[title]["rating"] = new_rating
        movie_storage_sql.update_movie(title, new_rating)
        print(f"Movie {title} updated")
    else:
        print(f"Movie {title} doesnt exist")

    input("Press Enter to go back to main menu")


def create_website(movies, user):
    with open(os.path.join("static", "index_template.html"), "r") as source:
        content = source.read()
        grid = ""
        for movie, info in movies.items():
            print(info)
            grid += f"""<li><div class ="movie"><img class ="movie-poster" src={info["poster"]} title="">
            <div class ="movie-title"> {movie} </div>
            <div class ="movie-year" > {info["year"]} </div>
            <div class ="movie-year" > Rating: {info["rating"]} </div>
            </div>
            </li>\n"""

        content = content.replace("__TEMPLATE_MOVIE_GRID__", grid)
        content = content.replace("__USERS_MOVIES__", f"{user["name"]}'s Movies")

        with open(os.path.join("static", f"{user["name"]}s_movies.html"), "w", encoding='utf-8') as destination:
            destination.write(content)

            print("SUCCESS")


def print_stats(movies, _):
    """
    print out certain statistics about all movies
    :param movies:
    """
    print("Movie statistics")
    total_rating = sum(float(movie["rating"]) for movie in movies.values())
    avg_rating = round(total_rating / len(movies), 1)

    print(f"Average movie rating: {avg_rating}")
    print(f"Median movie rating: {get_median_movie_rating(movies)}")

    best_movies_array = get_best_movies(movies, True)
    print("Best movie(s): ", end="")
    print(*best_movies_array, sep=", ")

    worst_movies_array = get_best_movies(movies, False)
    print("Worst movie(s): ", end="")
    print(*worst_movies_array, sep=", ")

    print()
    input("Press Enter to go back to main menu")


def get_median_movie_rating(movies):
    """
    :param movies:
    :return: the median movie rating of all movies
    """
    sorted_ratings = sorted(movie["rating"] for movie in movies.values())
    ratings_amount = len(sorted_ratings)
    if len(sorted_ratings) % 2 == 0:
        median = (sorted_ratings[(ratings_amount // 2) - 1] + sorted_ratings[ratings_amount // 2]) / 2
        return round(median, 1)
    else:
        return sorted_ratings[(ratings_amount // 2) + 1]


def get_best_movies(movies, get_best):
    """
    :param get_best: if True return best movies, else worst movies
    :return: either best or worst movies
    """
    best_movie_rating = sorted((movie["rating"] for movie in movies.values()), reverse=get_best)[0]

    return [
        f"{title} ({info['year']}): {info['rating']}"
        for title, info in movies.items()
        if info["rating"] == best_movie_rating
    ]


def print_random_movie(movies, _):
    """
    print a random movie
    :param movies:
    """
    title, info = list(movies.items())[random.randint(0, len(movies)-1)]
    print(f"Random movie: {title} ({info["year"]}): {info["rating"]}")
    print()
    input("Press Enter to go back to main menu")


def search_movie(movies, _):
    """
    search movie by title
    :param movies:
    """
    print("Search movie")
    search_str = get_input(str, "Enter part of the movie name: ")

    found = False
    for key, value in movies.items():
        if search_str.lower() in key.lower():
            print(f"Found movie: {key}: {value}")
            found = True

    if not found:
        results = process.extract(search_str, movies.keys())
        results = [item for item in results if item[1] > 49]

        if len(results) > 0:
            print(f'The movie "{search_str}" does not exist. Did you mean:')
            for title, _ in results:
                print(title)
        else:
            print("No matches found")

    input("Press Enter to go back to main menu")


def print_movie_ranking(movies, _):
    """
    print movie rankings from best to worst
    :param movies:
    """
    sorted_movies = sorted(movies.items(), key=lambda x: x[1]["rating"], reverse=True)
    for title, info in sorted_movies:
        print(f"{title} ({info["year"]}): {info["rating"]}")
    print()
    input("Press Enter to go back to main menu")


def create_rating_histogram(movies, _):
    """
    creates a histogram in the user specified path
    :param movies:
    """
    movie_ratings = list(movie["rating"] for movie in movies.values())
    plt.hist(movie_ratings, bins=50, edgecolor="black")
    plt.title('Movie Ratings Histogram')
    plt.xlabel('Ratings')
    plt.ylabel('Frequency')

    file_path = get_input(str, "Please enter the full path where you want to save the file: ")
    if os.path.exists(file_path):
        plt.savefig(file_path + "my_plot.jpeg")
        print(f"Histogram saved to {file_path}")
    else:
        print("The path does not exist. Histogram not saved.")

    input("Press Enter to go back to main menu")


def print_movie_years(movies, _):

    print("Do you want to order the release year ascending or descending?")
    print("1. ascending")
    print("2. descending")

    while True:
        user_input = get_input(int, "Please enter your choice: ")
        if user_input == 1 or user_input == 2:
            break
        else:
            print("Please enter either a 1 or a 2.")
    print()

    reverse = True if user_input == 2 else False
    sorted_movies = sorted(movies.items(), key=lambda x: x[1]["year"], reverse=reverse)
    for title, info in sorted_movies:
        print(f"{title} ({info["year"]}): {info["rating"]}")
    print()
    input("Press Enter to go back to main menu")


def select_user():
    print("Welcome to the Movie App!")

    users = user_storage_sql.get_users()

    while True:
        print()
        print("Select a user:")
        i = 1
        for user in users:
            print(f"{i}. {user["name"]}")
            i += 1

        print(f"{i}. Create new User")
        choice = get_input(int, f"Enter choice: ")

        if 0 < choice <= len(users):
            return users[choice - 1]
        elif choice == i:
            return create_new_user()


def create_new_user():
    print()
    name = get_input(str, "Enter your name: ")
    user_storage_sql.add_user(name)
    users = user_storage_sql.get_users()
    return users[len(users) - 1]


def main():

    user = select_user()

    movies = movie_storage_sql.get_movies_for_user(user["id"])

    commands = {"0": end_program,
                "1": list_movies,
                "2": add_movie,
                "3": delete_movie,
                "4": update_movie,
                "5": create_website,
                "6": print_stats,
                "7": print_random_movie,
                "8": search_movie,
                "9": print_movie_ranking,
                "10": create_rating_histogram,
                "11": print_movie_years}

    while True:
        print_menu(user)
        i = get_input(int, "Enter choice (0-11): ")

        if i in range(len(commands.items())):
            print()
            commands[str(i)](movies, user)
            print()
        else:
            print("Please enter a value between 0 and 10")


if __name__ == "__main__":
    main()
