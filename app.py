import os
import pickle

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Read the API key from the environment variables
tmdb_api_key = os.getenv("TMBD_API_KEY")

# print(tmdb_api_key)

movies = pickle.load(open("model/movies_list.pkl", "rb"))
movies_list = movies["title"].values

similarities = pickle.load(open("model/similarities.pkl", "rb"))

st.title("Movie Recommendation System")
select_movie = st.selectbox("Select movies from dropdown", movies_list)


def fetch_movie_poster(movie_id: int) -> str:

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/images?include_image_language=en"

    headers = {
        "accept": "application/json",
        "Authorization": tmdb_api_key,
    }

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        if "posters" in data:
            # Get the poster path from the first poster in the list (if available)
            poster_path = data["posters"][0]["file_path"]

            # Construct the full URL for the poster image
            full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"

            return full_path
        else:
            return "Poster not found"
    else:
        print(response.text)
        return f"Error: {response.status_code}"


def get_recommendation(movie_name: str):
    movie_name = (
        movie_name.title()
    )  # capitalizes the first letter of each word in a string

    if movie_name in movies["title"].values:
        index = movies[movies["title"] == movie_name].index[0]
        distance = sorted(
            list(enumerate(similarities[index])), reverse=True, key=lambda x: x[1]
        )

        recommended_movies = []
        recommended_movies_popularity = []
        movie_rating = []
        recommended_poster = []

        for i in distance[1:6]:
            movies_id = movies.iloc[i[0]].id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_popularity.append((movies.iloc[i[0]].popularity))
            movie_rating.append((movies.iloc[i[0]].vote_average))
            recommended_poster.append(fetch_movie_poster(movies_id))

    else:
        print("Error: Given movie name is invalid")

    return (
        recommended_movies,
        recommended_movies_popularity,
        movie_rating,
        recommended_poster,
    )


if st.button("Show Recommendation"):
    (
        recommended_movie_name,
        recommended_movies_popularity,
        movie_rating,
        recommended_poster,
    ) = get_recommendation(select_movie)

    col1, col2, col3, col4, col5 = st.columns(5)

    # Iterate over the columns
    for i, col in enumerate([col1, col2, col3, col4, col5]):
        with col:
            st.text(recommended_movie_name[i])
            st.image(recommended_poster[i])
            st.text(f"Rating: {movie_rating[i]}")
