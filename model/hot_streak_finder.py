import pandas as pd

import time

from nba_api.stats.library.parameters import SeasonYear

from nba_api.stats.endpoints import (
    leagueleaders,
    playergamelog,
    commonplayerinfo
)

from nba_api.stats.static import players

from model.opponents import (
    average_stats_against_opps,
    find_next_opp
)

from model.defense import team_defense_rank

HOT_STREAK_PLAYERS_PTS = []
HOT_STREAK_PLAYERS_3FGM = []


def create_player_average_df():
    # get first 150 league leaders in points
    top_players = pd.concat(leagueleaders.LeagueLeaders().get_data_frames()).iloc[0:100]

    # creates list of all players in above dataframe
    list_of_players = top_players["PLAYER_ID"].tolist()

    # sorts data frame by player and averages the PTS, reb, ast, and fg3m of the player
    top_players = top_players[["PLAYER_ID", "GP", "PTS", "REB", "AST", "FG3M"]].groupby("PLAYER_ID").apply(
        lambda x: x[["PTS", "REB", "AST", "FG3M"]].div(x.GP, axis=0)
    )

    return top_players, list_of_players


def find_hotstreak_players():
    print("creating season average df...")
    average_full_season, list_of_players = create_player_average_df()

    # create empty dataframe
    average_last_three_games = pd.DataFrame()

    # for loop for every player in the list
    print("creating recent game average df...")
    for player in list_of_players:
        print("getting info for player {}".format(player))

        # gets the last 3 games the player has played
        games = pd.concat(playergamelog.PlayerGameLog(
            player_id=player,
            season=SeasonYear.current_season_year).get_data_frames()
                          ).iloc[0:3]

        # sleep to prevent throttling
        time.sleep(0.9)

        # adds last 3 games of this player to dataframe
        average_last_three_games = pd.concat([average_last_three_games, games])

    # compresses dataframe to only pts, reb, ast, fg3m, etc. and averages these stats from the past 3 games
    average_last_three_games = average_last_three_games[
        ["Player_ID", "PTS", "REB", "AST", "FG3M", "FG_PCT", "FG3_PCT"]].groupby("Player_ID").mean()

    print("finding players currently on hotstreak and adding to list...")
    for player in list_of_players:
        print("getting hotstreak info for player {}".format(player))

        # sets player average of all stats for the full season
        player_season_average = average_full_season.loc[player]

        # sets player average of all stats for the last 3 games
        player_average_last_three_games = average_last_three_games.loc[player]

        players_average_pts = player_season_average.PTS.item()
        players_recent_average_pts = player_average_last_three_games.PTS.item()
        players_recent_fg_percen = player_average_last_three_games.FG_PCT.item()

        players_average_3pm = player_average_last_three_games.FG3M.item()
        players_recent_average_3pm = player_average_last_three_games.FG3M.item()
        players_recent_3p_percen = player_average_last_three_games.FG3_PCT.item()

        player_team = get_player_team(player)

        try:
            time.sleep(0.9)
            next_opp_team = find_next_opp(player, player_team)
        except Exception:
            next_opp_team = "N/A"

        if players_recent_average_pts >= players_average_pts + 6 \
                and players_recent_fg_percen >= 0.5:
            """
            if last 3 games pts average is larger than his season average (plus a couple standard
            deviations) along with a good field goal percentage, add it to a list
            """
            d = {
                "PLAYER_ID": player,
                "AVG": "{} pts".format(round(players_average_pts, 2)),
                "RECENT_AVG": "{} pts".format(round(players_recent_average_pts, 2)),
                "Percentage": "{}%".format(round(players_recent_fg_percen * 100, 2)),
                "TEAM": player_team,
                "NEXT_GAME_OPP": next_opp_team
            }
            HOT_STREAK_PLAYERS_PTS.append(d)
        elif players_recent_average_3pm > players_average_3pm + 1 \
                and players_recent_3p_percen >= 0.35:
            """
            if last 3 games FG3M is larger than his season average (plus a couple standard
            deviations) along with a good 3 point percentage, add it to a list
            """
            d = {
                "PLAYER_ID": player,
                "AVG": "{} 3PM".format(round(players_average_3pm, 2)),
                "RECENT_AVG": "{} 3PM".format(round(players_recent_average_3pm, 2)),
                "Percentage": "{}%".format(round(players_recent_3p_percen * 100, 2)),
                "TEAM": player_team,
                "NEXT_GAME_OPP": next_opp_team
            }
            HOT_STREAK_PLAYERS_3FGM.append(d)

    # print all collected players
    print("\n")
    print_hotstreak_players(HOT_STREAK_PLAYERS_PTS)
    print_hotstreak_players(HOT_STREAK_PLAYERS_3FGM)


def print_hotstreak_players(player_arr):
    for p in player_arr:
        average_stats_vs_opps = average_stats_against_opps(p["PLAYER_ID"], p["TEAM"])

        temp = players.find_player_by_id(p["PLAYER_ID"])
        full_name = temp["full_name"]

        print("{} is averaging {} at {} in the last 3 games with {} being his season average".format(
            full_name,
            p["RECENT_AVG"],
            p["Percentage"],
            p["AVG"]
        ))

        try:
            matchup_stats = average_stats_vs_opps.loc[p["NEXT_GAME_OPP"]]

            print("versus {} (next opponent), he is averaging {} pts, {} ast, {} rebs, and {} FG3M "
                  "in {} games in the last 2 years".format(
                p["NEXT_GAME_OPP"],
                matchup_stats["PTS"],
                matchup_stats["AST"],
                matchup_stats["REB"],
                matchup_stats["FG3M"],
                matchup_stats["count"],
            ))
        except Exception as e:
            print("{} has not played against {} in a while on current team".format(
                full_name,
                p["NEXT_GAME_OPP"]
            ))

        team_defense_row = team_defense_rank(p["NEXT_GAME_OPP"])
        print("Their opponent is also ranked at {} in the league for defense currently".format(
            team_defense_row.E_DEF_RATING_RANK.item()
        ))

        print("\n")


def get_player_team(player):
    player_info = commonplayerinfo.CommonPlayerInfo(
        player_id=player
    ).get_normalized_dict()["CommonPlayerInfo"][0]

    return player_info["TEAM_ABBREVIATION"]
