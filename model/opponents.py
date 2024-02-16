import pandas as pd

from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import playernextngames
from nba_api.stats.endpoints import defensehub
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll
from nba_api.stats.static import players


def create_matchup_df(player):
    gamelog = pd.concat(playergamelog.PlayerGameLog(player_id=player, season=SeasonAll.all).get_data_frames())
    gamelog["GAME_DATE"] = pd.to_datetime(gamelog["GAME_DATE"], format="%b %d, %Y")

    gamelog = gamelog.query("GAME_DATE.dt.year in [2023, 2024]")

    return gamelog


def average_stats_against_opps(player, player_team):
    gamelog = create_matchup_df(player)
    gamelog = gamelog.replace({
        "vs.": "",
        "@": "",
        player_team: "",
        " ": ""
    }, regex=True)

    df1 = gamelog[["MATCHUP", "PTS", "AST", "REB", "FG3M"]].groupby("MATCHUP").mean()

    df2 = gamelog["MATCHUP"].value_counts()

    df1 = df1.merge(df2, left_index=True, right_index=True)

    return df1.sort_values(by="count", ascending=False)


def find_next_opp(player, player_team):
    next_game = playernextngames.PlayerNextNGames(
        player_id=player,
        number_of_games=1
    ).get_normalized_dict()['NextNGames'][0]

    home_team = next_game["HOME_TEAM_ABBREVIATION"]
    away_team = next_game["VISITOR_TEAM_ABBREVIATION"]

    if home_team == player_team:
        return away_team

    return home_team

