import pandas as pd

from model.hot_streak_finder import (
    find_hotstreak_players
)

from model.defense import team_defense_rank, matchups


def main():
    find_hotstreak_players()

    # https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/playervsplayer.md
    # team he plays above average against?


if __name__ == "__main__":
    main()