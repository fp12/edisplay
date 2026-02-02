from dataclasses import dataclass
from datetime import datetime, timedelta
from pprint import pprint

from babel.dates import format_date


@dataclass
class Game:
    season_id: str
    team_id: int
    team_abbreviation: str
    team_name: str
    game_id: str
    game_date: str
    matchup: str
    wl: str
    min: int
    fgm: int
    fga: int
    fg_pct: float
    fg3m: int
    fg3a: int
    fg3_pct: float
    ftm: int
    fta: int
    ft_pct: float
    oreb: int
    dreb: int
    reb: int
    ast: int
    stl: int
    blk: int
    tov: int
    pf: int
    pts: int
    plus_minus: int
    video_available: int


def _prio(matchup):
    if 'LAL' in matchup:
        return 0
    if 'DAL' in matchup:
        return 1
    if 'SAS' in matchup:
        return 2
    return 99


def get_results(date_from, date_to):
    from nba_api.stats.endpoints import LeagueGameLog

    date_from = format_date(date_from, format='yyyy-MM-dd') if isinstance(date_from, datetime) else date_from
    date_to = format_date(date_to, format='yyyy-MM-dd') if isinstance(date_to, datetime) else date_to

    game_log = LeagueGameLog(date_from_nullable=date_from, date_to_nullable=date_to)

    games = {}
    for game_raw in game_log.league_game_log.data['data']:
        game = Game(*game_raw)
        if games.get(game.game_id):
            games[game.game_id] += f'{game.pts:3} {game.team_abbreviation}'
        else:
            games[game.game_id] = f'{game.team_abbreviation} {game.pts:3}-'
    
    return sorted([matchup for _, matchup in games.items()], key=_prio)


def get_games(date):
    from nba_api.stats.endpoints import ScoreboardV3

    date = format_date(date, format='yyyy-MM-dd') if isinstance(date, datetime) else date
    
    scoreboard = ScoreboardV3(game_date=date)

    matchups = []
    for game_raw in scoreboard.game_header.data['data']:
        matchup = game_raw[1][-6:]
        matchups.append(f'{matchup[:3]} @ {matchup[-3:]}')

    return sorted(matchups, key=_prio)


if __name__ == '__main__':
    now = datetime.now()
    date_from = now - timedelta(days=3) if now.weekday == 0 else now - timedelta(days=1)
    date_to = now

    #games = get_results(format_date(date_from, format='yyyy-MM-dd'), format_date(date_to, format='yyyy-MM-dd'))
    #for game in games:
    #    print(game)

    date = now + timedelta(days=1)
    games = get_games(date)
    for game in games:
        print(game)
