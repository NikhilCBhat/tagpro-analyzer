import os
import json
import pandas as pd
import seaborn as sns
from collections import defaultdict, Counter
import spotipy
import spotipy.util as util
import matplotlib.pyplot as plt
from utils import string_date_to_attributes, date_to_time_elapsed
from data_collection import load_tagpro_data
from spotify_functions import get_spotify_api_object, get_recent_spotify_songs, get_genres

outcome_to_name = {
    1: "won", 2: "lost", 3: "dc", 4: "save"
}

def tagpro_data_to_dataframe(data):

    tagpro_data = defaultdict(list)

    for i, dataset in enumerate(data):
        tagpro_data["game_id"].append(-i)
        for key, value in dataset.items():
            tagpro_data[key].append(value)
    
    return pd.DataFrame(tagpro_data)

def add_extra_parameters(df):
    df["outcome_name"] = [outcome_to_name[outcome] for outcome in df["outcome"]]
    for i,time_unit in enumerate(["second", "minute", "hour", "day", "month", "year"]):
        df[time_unit] = [string_date_to_attributes(playtime)[i] for playtime in df["played"]]
    df["time_elapsed"] = [date_to_time_elapsed(playtime) for playtime in df["played"]]
    df["game_status"] = [1 if outcome == "won" else 0 for outcome in df["outcome_name"]]
    df["cumulative_sum"] = df["game_status"].cumsum()
    df["cumulative_average"] = [s/(i+1) for i,s in enumerate(list(df["cumulative_sum"]))]
    return df

def get_songs_per_game(df, songs):
    game_to_songs = defaultdict(set)
    song_index = 0

    df["song_ids"] = [set() for _ in df.index]
    for game_number in range(300):
        game_end = date_to_time_elapsed(df["played"][game_number])
        duration = df["timePlayed"][game_number]
        game_start = game_end - duration

        for song_number in range(song_index, 50):
            song = songs["items"][song_number]
            song_end = date_to_time_elapsed(song["played_at"])
            duration = song["track"]["duration_ms"] / 1000
            song_start = song_end - duration

            if song_start <= game_start <= song_end or song_start <= game_end <= song_end:
                game_to_songs["Game {} ({})".format(300-game_number, df["outcome_name"][game_number])].add(song["track"]["name"])
                df["song_ids"][game_number].add(song["track"]["id"])

    return game_to_songs, df

def make_plot():

    cmap = sns.cubehelix_palette(dark=.3, light=.8, as_cmap=True)
    tagpro_data = load_tagpro_data(".")
    tagpro_data = load_tagpro_data()
    df = tagpro_data_to_dataframe(tagpro_data)
    df = add_extra_parameters(df)
    sns.boxplot(x="gameMode", y="score", data=df)
    plt.show()

def make_plot_2(df):
    hour_data = pd.DataFrame({
        "hour": [(h-12)%24 for h in range(24)],
        "win_percentage": [sum(list(df.loc[df["hour"].isin({hour})]["game_status"]))/max(len(list(df.loc[df["hour"].isin({hour})]["game_status"])),1) for hour in range(24)],
        "count": [len(list(df.loc[df["hour"].isin({hour})]["game_status"])) for hour in range(24)]
    })

    sns.scatterplot(x="hour", y="win_percentage", size="count", data=hour_data)
    plt.show()

def make_plot_3(df):
    sns.scatterplot(x="game_id", y="score", data=df, palette="Set2", hue="outcome_name", size="tags")
    plt.show()

def generate_win_percentage_df(df):
    genre_to_win_percentage = {}

    for i in range(300):
        song_ids = df["song_ids"][i]
        if type(song_ids) == str:
            song_ids = eval(song_ids)

        for id in song_ids:
            for genre in get_genres(id):
                if genre in genre_to_win_percentage:
                    genre_to_win_percentage[genre][0] += df["game_status"][i]
                    genre_to_win_percentage[genre][1] += 1
                else:
                    genre_to_win_percentage[genre] = [df["game_status"][i], 1]

    g2wp = sorted([[genre, 100*won/total, total] for genre, (won, total) in genre_to_win_percentage.items()], key=lambda x: x[1], reverse=True)
    return pd.DataFrame(g2wp, columns=["Genre", "win percentage", "total games"])

if __name__ == "__main__":

    tagpro_data = load_tagpro_data()
    tagpro_df = tagpro_data_to_dataframe(tagpro_data)
    tagpro_df = add_extra_parameters(tagpro_df)
    songs = get_recent_spotify_songs()
    _, tagpro_df = get_songs_per_game(tagpro_df, songs)
    wpf = generate_win_percentage_df(tagpro_df)
    print(wpf)
    # wpf.to_csv("wpf_data.csv", index=None)
