import pandas as pd

from model.streak_finder import (
    find_hot_or_cold_streak_players, create_player_average_df
)

from model.defense import team_defense_rank, matchups


def main():
    find_hot_or_cold_streak_players()

    # who are they playing against?
    # defensive rating?
    # is it a veteran vs a rookie?

    # https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/playervsplayer.md
    # team he plays above average against?


if __name__ == "__main__":
    main()