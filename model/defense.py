import pandas as pd

from nba_api.stats.endpoints import teamestimatedmetrics, matchupsrollup

from nba_api.stats.static import teams

from nba_api.stats.library.parameters import (
    GameScopeDetailed,
    LeagueID,
    PlayerOrTeam,
    PlayerScope,
    Season,
    SeasonType,
    PerMode36
)


def team_defense_rank(team):
    team_metrics = pd.concat(teamestimatedmetrics.TeamEstimatedMetrics(
        league_id=LeagueID.default,
        season=Season.default,
        season_type=SeasonType.default
    ).get_data_frames())[["TEAM_ID", "TEAM_NAME", "E_DEF_RATING_RANK"]]

    team = teams.find_team_by_abbreviation(team.lower())['id']

    team_rank = team_metrics.loc[team_metrics['TEAM_ID'] == team]

    return team_rank


def matchups(team):
    team_id = teams.find_team_by_abbreviation(team.lower())['id']

    matchups = pd.concat(matchupsrollup.MatchupsRollup(
        league_id=LeagueID.default,
        per_mode_simple=PerMode36.default,
        season=Season.default,
        season_type_playoffs=SeasonType.default,
        def_team_id_nullable=team_id
    ).get_data_frames())

    matchups = matchups[matchups["POSITION"] == "TOTAL"]

    return matchups.loc[matchups['DEF_PLAYER_NAME'] == 'Nikola Jokic'].iloc[0]