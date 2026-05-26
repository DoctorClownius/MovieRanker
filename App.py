# Write your code here :-)
import streamlit as st
import csv
import random
import pandas as pd

st.markdown("""
<style>

/* BIG MOVIE BUTTONS */
div.stButton > button[kind="primary"] {
    min-height: 160px;
    width: 200px;
    font-size: 24px;
    font-weight: 700;
    white-space: normal;
    overflow-wrap: break-word;
    padding: 20px;
    border-radius: 12px;
}

/* SMALL DEFAULT BUTTONS */
div.stButton > button[kind="secondary"] {
    min-height: 38px;
    height: 38px;
    font-size: 14px;
    padding: 0px 10px;
}

</style>
""", unsafe_allow_html=True)

def load_movies():
    movies = {}

    with open("movies.csv", "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            movies[row["Movie"]] = {
                "rating": int(row["Rating"]),
                "seen": row["Seen"].lower() == "true",
                "year": int(row["Year"])
            }

    return movies

movies = load_movies()

def save_movies(movies):
    with open("movies.csv", "w", newline="", encoding="utf-8-sig") as file:
        fieldnames = ["Movie", "Rating", "Seen", "Year"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for movie, data in movies.items():
            writer.writerow({
                "Movie": movie,
                "Rating": data["rating"],
                "Seen": data["seen"],
                "Year": data["year"]
            })

def update_elo(rating1, rating2, winner, k=32):
    expected1 = 1 / (1 + 10 ** ((rating2 - rating1) / 400))
    expected2 = 1 / (1 + 10 ** ((rating1 - rating2) / 400))

    if winner == 1:
        score1 = 1
        score2 = 0
    else:
        score1 = 0
        score2 = 1

    new_rating1 = rating1 + k * (score1 - expected1)
    new_rating2 = rating2 + k * (score2 - expected2)

    return round(new_rating1), round(new_rating2)

def load_stats():
    stats = {}

    try:
        with open("stats.csv", "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                stats[row["Stat"]] = int(row["Value"])

    except FileNotFoundError:
        stats["Matchups"] = 0

    return stats


def save_stats(stats):
    with open("stats.csv", "w", newline="", encoding="utf-8-sig") as file:
        fieldnames = ["Stat", "Value"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for stat, value in stats.items():
            writer.writerow({
                "Stat": stat,
                "Value": value
            })

stats = load_stats()

st.metric("Comparisons: ", stats.get("Matchups",0))

seen_movies = [
    movie for movie in movies
    if movies[movie]["seen"] == True
]

if "movie1" not in st.session_state or "movie2" not in st.session_state:
    st.session_state.movie1, st.session_state.movie2 = random.sample(seen_movies, 2)

movie1 = st.session_state.movie1
movie2 = st.session_state.movie2

st.title("MovieRanker")

st.write("Which movie do you prefer?")

col1, spacer, col2 = st.columns([5,1,5])

with col1:
    st.markdown(f'<div class="movie-year">{movies[movie1]["year"]}</div>', unsafe_allow_html=True)
    button_col1, button_col2, button_col3 = st.columns([1, 3, 1])

    with button_col2:
        if st.button(
            f"{movie1}\n({movies[movie1]['year']})",
            key="movie1button",
            type="primary"
        ):
            new1, new2 = update_elo(
                movies[movie1]["rating"],
                movies[movie2]["rating"],
                1
            )

            movies[movie1]["rating"] = new1
            movies[movie2]["rating"] = new2
            save_movies(movies)
            stats["Matchups"] = stats.get("Matchups", 0) + 1
            save_stats(stats)
            st.session_state.pop("movie1", None)
            st.session_state.pop("movie2", None)

            st.rerun()

    button_col1, button_col2, button_col3 = st.columns([1, 3, 1])

    with button_col2:
        if st.button(f"Haven't seen it", key="unseen1"):
            movies[movie1]["seen"] = False
            save_movies(movies)
            st.session_state.pop("movie1", None)
            st.session_state.pop("movie2", None)

            st.markdown('</div>', unsafe_allow_html=True)
            st.rerun()

with col2:
    st.markdown(f'<div class="movie-year">{movies[movie2]["year"]}</div>', unsafe_allow_html=True)
    button_col1, button_col2, button_col3 = st.columns([1, 3, 1])

    with button_col2:
        if st.button(
            f"{movie2}\n({movies[movie2]['year']})",
            key="movie2button",
            type="primary"
        ):
            new1, new2 = update_elo(
                movies[movie1]["rating"],
                movies[movie2]["rating"],
                2
            )

            movies[movie1]["rating"] = new1
            movies[movie2]["rating"] = new2
            save_movies(movies)
            stats["Matchups"] = stats.get("Matchups", 0) + 1
            save_stats(stats)
            del st.session_state.movie1
            del st.session_state.movie2
            st.rerun()

    button_col1, button_col2, button_col3 = st.columns([1, 3, 1])

    with button_col2:
        if st.button(f"Haven't seen it", key="unseen2"):
            movies[movie2]["seen"] = False
            save_movies(movies)
            del st.session_state.movie1
            del st.session_state.movie2

            st.markdown('</div>', unsafe_allow_html=True)
            st.rerun()

st.divider()

if "show_rankings" not in st.session_state:
    st.session_state.show_rankings = False

left_space, show_col, middle_space, hide_col, right_space = st.columns([1,2,1,2,1])

with show_col:
    if st.button("Show Rankings"):
        st.session_state.show_rankings = True

with hide_col:
    if st.button("Hide Rankings"):
        st.session_state.show_rankings = False

if st.session_state.show_rankings:

    sorted_movies = sorted(
    [
        (movie, data)
        for movie, data in movies.items()
        if data["seen"] == True
    ],
    key=lambda x: x[1]["rating"],
    reverse=True
)

    for movie, data in sorted_movies:
        st.write(
            f"{movie} ({data['year']}): {data['rating']}"
        )
