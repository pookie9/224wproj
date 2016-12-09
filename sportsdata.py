import mlbgame
import nflgame

def getMLBEdges(start, end, gamma=0.8):
    """
    Generates a dictionary of (team1, team2) -> wl_spread where
    wl_spread is the sum of discounted win-loss spreads of seasons
    between start and end. Win-loss spreads are calculated as the number
    of wins team1 has against team2 minus the number of losses

    Args:
        start (int): the first season to gather data for
        end (int): the last season to collect data for
        gamma (float): the discount factor to apply to past seasons

    Returns:
        A dictionary of edges to win/loss spreads
    """

    edges = {}
    teams = { team.club_common_name : team.club.upper() for team in mlbgame.teams() }
    for year in range(start, end + 1):
        games = mlbgame.combine_games(mlbgame.games(year))
        discount = gamma**(end - year)
        for game in games:
            try:
                # Some game data is with teams not in the MLB, some games don't have winners, so check for that
                if game.w_team in teams and game.l_team in teams:
                    winner = teams[game.w_team]
                    loser = teams[game.l_team]
                    edges[(winner, loser)] = edges.get((winner, loser), 0.0) + 1 * discount
                    edges[(loser, winner)] = edges.get((loser, winner), 0.0) - 1 * discount
            except AttributeError:
                pass
        
    return teams.values(), edges

def getNFLEdges(start, end, gamma=0.8):
    """
    Generates a dictionary of (team1, team2) -> wl_spread where
    wl_spread is the sum of discounted win-loss spreads of seasons
    between start and end. Win-loss spreads are calculated as the number
    of wins team1 has against team2 minus the number of losses

    Args:
        start (int): the first season to gather data for
        end (int): the last season to collect data for
        gamma (float): the discount factor to apply to past seasons

    Returns:
        A dictionary of edges to win/loss spreads
    """

    edges = {}
    teams = [ team[0] for team in nflgame.teams ]
    for year in range(start, end + 1):
        games = nflgame.games(year)
        discount = gamma**(end - year)
        for game in games:
            try:
                winner = str(game.winner)
                loser = str(game.loser)
                if winner != loser:
                # Ignore tie games
                    edges[(winner, loser)] = edges.get((winner, loser), 0.0) + 1 * discount
                    edges[(loser, winner)] = edges.get((loser, winner), 0.0) - 1 * discount
            except:
                print "Error accessing data for game", game
                pass
        
    return teams, edges
