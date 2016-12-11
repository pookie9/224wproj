import snap
import process_mlb
import sportsdata
import random
import syntheticgraph

MLB_2015_STANDINGS = ['STL', 'PIT', 'CHC', 'KC', 'TOR', 'LA', 'NYM', 'TEX', 'NYY', 'HOU', 'ANA', 'SF', 'WAS', 'MIN', 'CLE', 'BAL', 'TB', 'ARI', 'BOS', 'SEA', 'CWS', 'DET', 'SD', 'MIA', 'MIL', 'OAK', 'COL', 'ATL', 'CIN', 'PHI']
NFL_2015_STANDINGS = ['CAR', 'DEN', 'SEA', 'ARI', 'NE', 'CIN', 'PIT', 'KC', 'MIN', 'GB', 'WAS', 'NYJ', 'HOU', 'BUF', 'ATL', 'OAK', 'IND', 'PHI', 'NO', 'DET', 'MIA', 'STL', 'NYG', 'TB', 'CHI', 'BAL', 'JAC', 'SD', 'SF', 'DAL', 'TEN', 'CLE']

def randomValue(nodeID, graph, edgeAttrs):
    return random.random()

def degreeDifference(nodeID, graph, edgeAttrs):
    node = graph.GetNI(nodeID)
    return node.GetInDeg() - node.GetOutDeg()

def edgeWeightDifference(nodeID, graph, edgeAttrs):
    diff = 0
    node = graph.GetNI(nodeID)
    for edgeID in node.GetInEdges():
        diff += edgeAttrs[(nodeID, edgeID)]

    for edgeID in node.GetOutEdges():
        diff -= edgeAttrs[(edgeID, nodeID)]

    return diff

def ranking(graph, alpha=0.6, primary=degreeDifference, secondary=randomValue, edgeAttrs=None):
    """
    Implements the node ranking algorithm described by Guo, Yang, and Zhou

    Args:
        graph (snap.TNGraph): a directed graph to rank
        alpha (float): the relative size of the leader partition
        primary ((nodeID, graph, edgeAttrs) -> int): sorting key for primary sorting of the nodes
        secondary ((nodes, graph, edgeAttrs) -> nodes): sorting key for secondary sorting of nodes
        edgeAttrs (dict): edge attributes for use with sorting key functions
    Returns:
        A list of node IDs ordered in descending order by ranking
    """
    
    # Group the nodes by degree difference (d_in - d_out)
    nodeOrdering = sorted([ node.GetId() for node in graph.Nodes()], key=lambda nodeID:
                            (primary(nodeID, graph, edgeAttrs), secondary(nodeID, graph, edgeAttrs)),
                            reverse=True)

    # Split the nodes in leaders and followers
    splitIndex = int(alpha * graph.GetNodes())
    leaders = nodeOrdering[:splitIndex]
    followers = nodeOrdering[splitIndex:]

    # Recursive base case check: if either leaders or followers is empty
    # then further recursing won't change the ordering, so just return the
    # current ordering
    if len(leaders) == 0 or len(followers) == 0:
        return leaders + followers

    # Create the subgraphs
    leaderNIdVector = snap.TIntV()
    for node in leaders:
        leaderNIdVector.Add(node)
    leaderGraph = snap.GetSubGraph(graph, leaderNIdVector)

    followerNIdVector = snap.TIntV()
    for node in followers:
        followerNIdVector.Add(node)
    followerGraph = snap.GetSubGraph(graph, followerNIdVector)

    # Recurse on the leaders and followers
    return ranking(leaderGraph, alpha, primary, secondary, edgeAttrs) + ranking(followerGraph, alpha, primary, secondary, edgeAttrs)

def graphRankingEvaluation(graph, ranking):
    """
    Evaluates the accuracy of the ranking within the graph. An edge is
    considered accurately predicted if the ranking of its destination is
    higher than the ranking of its source. The accuracy is given by the
    number of accurate edges divided by the total number of edges.

    Args:
        graph (snap.TNGraph): a directed graph
        ranking (list): a ranking of the nodes of the graph, from high to low

    Returns:
        A float representing the proportion of accurately predicted nodes.
    """
    # Generate a mapping of node to ranking for quick lookup
    rankingMap = {}
    for i in range(len(ranking)):
        rankingMap[ranking[i]] = i
    
    # Iterate through the edges
    correctCount = 0
    for edge in graph.Edges():
        sourceRank = rankingMap[edge.GetSrcNId()]
        destRank = rankingMap[edge.GetDstNId()]

        if destRank <= sourceRank:
            correctCount += 1

    return correctCount * 1.0 / graph.GetEdges()

def gameRankingEvaluation(games, ranking):
    """
    Evaluates the accuracy of the ranking against a list of games. A game is
    considered accurately predicted if the winner is ranked higher than the loser.
    The accuracy is given by the number of accurate games divided by the total number
    of games.

    Args:
        games (list): a list of games represented as tuples (loser, winner)
        ranking (list): a ranking of the teams, ordered from high to low

    Returns:
        A float representing the proportion of accurately predicted games
    """

    # Generate a mapping of team to ranking for quick lookup
    rankingMap = {}
    for i in range(len(ranking)):
        rankingMap[ranking[i]] = i

    # Iterate through the games
    correctCount = 0
    for game in games:
        try:
            winnerIndex = rankingMap[game[0]]
            loserIndex= rankingMap[game[1]]
            if loserIndex > winnerIndex:
                correctCount += 1
        except:
            pass
    
    return correctCount * 1.0 / len(games)

def rankingTest():
    """
    Run analysis on the MLB and NFL graphs. For each league, we:
        1) Generate our own ranking for 2015
        2) Determine how accurately our ranking reflects 2015 games
        3) Determine how accurately the actual ranking reflects 2015 games
        4) Calculate the Levenshtein (edit) distance between 2015 rankings
        5) Generate a ranking for 2012-2014 data
        6) Determine how accurately our historical ranking reflects 2015 games
    """
    # Results for 2015 MLB data
    randomResults = []
    edgeWeightPrimaryResults = []
    edgeWeightSecondaryResults = []

    teams, edgeWeights = sportsdata.getMLBEdges(2015, 2015)
    edgeWeights = { edge : weight for edge, weight in edgeWeights.items() if weight > 0 } 
    currentGraph = createGraph(teams, edgeWeights)
    games = sportsdata.getMLBGames(2015)
    edgeWeights = { (teams.index(edge[0]), teams.index(edge[1])) : weight for edge, weight in edgeWeights.items() }
    for alpha in [ j * 0.1 for j in range(1, 10) ]:
        randomRanking = [ teams[i] for i in ranking(currentGraph, alpha) ]
        edgeWeightPrimaryRanking = [ teams[i] for i in ranking(currentGraph, alpha, edgeWeightDifference, randomValue, edgeWeights) ]
        edgeWeightSecondaryRanking = [ teams[i] for i in ranking(currentGraph, alpha, degreeDifference, edgeWeightDifference, edgeWeights) ]

        randomAccuracy = gameRankingEvaluation(games, randomRanking)
        edgeWeightPrimaryAccuracy = gameRankingEvaluation(games, edgeWeightPrimaryRanking)
        edgeWeightSecondaryAccuracy = gameRankingEvaluation(games, edgeWeightSecondaryRanking)

        randomDistance = levenshtein(randomRanking, MLB_2015_STANDINGS)
        edgeWeightPrimaryDistance = levenshtein(edgeWeightPrimaryRanking, MLB_2015_STANDINGS)
        edgeWeightSecondaryDistance = levenshtein(edgeWeightSecondaryRanking, MLB_2015_STANDINGS)

        randomResults.append((alpha, randomRanking, randomAccuracy, randomDistance))
        edgeWeightPrimaryResults.append((alpha, edgeWeightPrimaryRanking, edgeWeightPrimaryAccuracy, edgeWeightPrimaryDistance))
        edgeWeightSecondaryResults.append((alpha, edgeWeightSecondaryRanking, edgeWeightSecondaryAccuracy, edgeWeightSecondaryDistance))

    randomOptimal = max(randomResults, key=lambda result: result[2])
    edgeWeightPrimaryOptimal = max(edgeWeightPrimaryResults, key=lambda result: result[2])
    edgeWeightSecondaryOptimal = max(edgeWeightSecondaryResults, key=lambda result: result[2])

    # Predicting with 2012-2014 data
    randomResults = []
    edgeWeightPrimaryResults = []
    edgeWeightSecondaryResults = []
    for gamma in [ i * 0.1 for i in range(0, 11) ]:
        (teams, edgeWeights) = sportsdata.getMLBEdges(2012, 2014, gamma)
        edgeWeights = { edge : weight for edge, weight in edgeWeights.items() if weight > 0 } 
        historicalGraph = createGraph(teams, edgeWeights)
        edgeWeights = { (teams.index(edge[0]), teams.index(edge[1])) : weight for edge, weight in edgeWeights.items() }
        for alpha in [ j * 0.1 for j in range(1, 10) ]:
            randomRanking = [ teams[i] for i in ranking(historicalGraph, alpha) ]
            edgeWeightPrimaryRanking = [ teams[i] for i in ranking(historicalGraph, alpha, edgeWeightDifference, randomValue, edgeWeights) ]
            edgeWeightSecondaryRanking = [ teams[i] for i in ranking(historicalGraph, alpha, degreeDifference, edgeWeightDifference, edgeWeights) ]

            randomAccuracy = gameRankingEvaluation(games, randomRanking)
            edgeWeightPrimaryAccuracy = gameRankingEvaluation(games, edgeWeightPrimaryRanking)
            edgeWeightSecondaryAccuracy = gameRankingEvaluation(games, edgeWeightSecondaryRanking)

            randomDistance = levenshtein(randomRanking, MLB_2015_STANDINGS)
            edgeWeightPrimaryDistance = levenshtein(edgeWeightPrimaryRanking, MLB_2015_STANDINGS)
            edgeWeightSecondaryDistance = levenshtein(edgeWeightSecondaryRanking, MLB_2015_STANDINGS)

            randomResults.append((gamma, alpha, randomRanking, randomAccuracy, randomDistance))
            edgeWeightPrimaryResults.append((gamma, alpha, edgeWeightPrimaryRanking, edgeWeightPrimaryAccuracy, edgeWeightPrimaryDistance))
            edgeWeightSecondaryResults.append((gamma, alpha, edgeWeightSecondaryRanking, edgeWeightSecondaryAccuracy, edgeWeightSecondaryDistance))

    histRandomOptimal = max(randomResults, key=lambda result: result[3])
    histEdgeWeightPrimaryOptimal = max(edgeWeightPrimaryResults, key=lambda result: result[3])
    histEdgeWeightSecondaryOptimal = max(edgeWeightSecondaryResults, key=lambda result: result[3])

    print "MLB Results"
    print "==========="
    print "DR", randomOptimal
    print "EWR", edgeWeightPrimaryOptimal
    print "DEW", edgeWeightSecondaryOptimal
    print "Actual ranking", gameRankingEvaluation(games, MLB_2015_STANDINGS)
    print "Historical DR", histRandomOptimal
    print "Historical EWR", histEdgeWeightPrimaryOptimal
    print "Historical DEW", histEdgeWeightSecondaryOptimal

    randomResults = []
    edgeWeightPrimaryResults = []
    edgeWeightSecondaryResults = []

    teams, edgeWeights = sportsdata.getNFLEdges(2015, 2015)
    edgeWeights = { edge : weight for edge, weight in edgeWeights.items() if weight > 0 } 
    currentGraph = createGraph(teams, edgeWeights)
    games = sportsdata.getNFLGames(2015)
    edgeWeights = { (teams.index(edge[0]), teams.index(edge[1])) : weight for edge, weight in edgeWeights.items() }
    for alpha in [ j * 0.1 for j in range(1, 10) ]:
        randomRanking = [ teams[i] for i in ranking(currentGraph, alpha) ]
        edgeWeightPrimaryRanking = [ teams[i] for i in ranking(currentGraph, alpha, edgeWeightDifference, randomValue, edgeWeights) ]
        edgeWeightSecondaryRanking = [ teams[i] for i in ranking(currentGraph, alpha, degreeDifference, edgeWeightDifference, edgeWeights) ]

        randomAccuracy = gameRankingEvaluation(games, randomRanking)
        edgeWeightPrimaryAccuracy = gameRankingEvaluation(games, edgeWeightPrimaryRanking)
        edgeWeightSecondaryAccuracy = gameRankingEvaluation(games, edgeWeightSecondaryRanking)

        randomDistance = levenshtein(randomRanking, MLB_2015_STANDINGS)
        edgeWeightPrimaryDistance = levenshtein(edgeWeightPrimaryRanking, MLB_2015_STANDINGS)
        edgeWeightSecondaryDistance = levenshtein(edgeWeightSecondaryRanking, MLB_2015_STANDINGS)

        randomResults.append((alpha, randomRanking, randomAccuracy, randomDistance))
        edgeWeightPrimaryResults.append((alpha, edgeWeightPrimaryRanking, edgeWeightPrimaryAccuracy, edgeWeightPrimaryDistance))
        edgeWeightSecondaryResults.append((alpha, edgeWeightSecondaryRanking, edgeWeightSecondaryAccuracy, edgeWeightSecondaryDistance))

    randomOptimal = max(randomResults, key=lambda result: result[2])
    edgeWeightPrimaryOptimal = max(edgeWeightPrimaryResults, key=lambda result: result[2])
    edgeWeightSecondaryOptimal = max(edgeWeightSecondaryResults, key=lambda result: result[2])

    # Predicting with 2012-2014 data
    randomResults = []
    edgeWeightPrimaryResults = []
    edgeWeightSecondaryResults = []
    for gamma in [ i * 0.1 for i in range(0, 11) ]:
        (teams, edgeWeights) = sportsdata.getNFLEdges(2012, 2014, gamma)
        edgeWeights = { edge : weight for edge, weight in edgeWeights.items() if weight > 0 } 
        historicalGraph = createGraph(teams, edgeWeights)
        edgeWeights = { (teams.index(edge[0]), teams.index(edge[1])) : weight for edge, weight in edgeWeights.items() }
        for alpha in [ j * 0.1 for j in range(1, 10) ]:
            randomRanking = [ teams[i] for i in ranking(historicalGraph, alpha) ]
            edgeWeightPrimaryRanking = [ teams[i] for i in ranking(historicalGraph, alpha, edgeWeightDifference, randomValue, edgeWeights) ]
            edgeWeightSecondaryRanking = [ teams[i] for i in ranking(historicalGraph, alpha, degreeDifference, edgeWeightDifference, edgeWeights) ]

            randomAccuracy = gameRankingEvaluation(games, randomRanking)
            edgeWeightPrimaryAccuracy = gameRankingEvaluation(games, edgeWeightPrimaryRanking)
            edgeWeightSecondaryAccuracy = gameRankingEvaluation(games, edgeWeightSecondaryRanking)

            randomDistance = levenshtein(randomRanking, NFL_2015_STANDINGS)
            edgeWeightPrimaryDistance = levenshtein(edgeWeightPrimaryRanking, NFL_2015_STANDINGS)
            edgeWeightSecondaryDistance = levenshtein(edgeWeightSecondaryRanking, NFL_2015_STANDINGS)

            randomResults.append((gamma, alpha, randomRanking, randomAccuracy, randomDistance))
            edgeWeightPrimaryResults.append((gamma, alpha, edgeWeightPrimaryRanking, edgeWeightPrimaryAccuracy, edgeWeightPrimaryDistance))
            edgeWeightSecondaryResults.append((gamma, alpha, edgeWeightSecondaryRanking, edgeWeightSecondaryAccuracy, edgeWeightSecondaryDistance))

    histRandomOptimal = max(randomResults, key=lambda result: result[3])
    histEdgeWeightPrimaryOptimal = max(edgeWeightPrimaryResults, key=lambda result: result[3])
    histEdgeWeightSecondaryOptimal = max(edgeWeightSecondaryResults, key=lambda result: result[3])

    print "NFL Results"
    print "==========="
    print "DR", randomOptimal
    print "EWR", edgeWeightPrimaryOptimal
    print "DEW", edgeWeightSecondaryOptimal
    print "Actual ranking", gameRankingEvaluation(games, NFL_2015_STANDINGS)
    print "Historical DR", histRandomOptimal
    print "Historical EWR", histEdgeWeightPrimaryOptimal
    print "Historical DEW", histEdgeWeightSecondaryOptimal

    """
    (teams, edgeDict) = sportsdata.getMLBEdges(2015, 2015)
    currentMLBGraph = createGraph(teams, edgeDict)

    mlbRandomResults = []
    mlbWinLossResults = []
    for gamma in [ i * 0.1 for i in range(0, 11) ]:
        (teams, edgeDict) = sportsdata.getMLBEdges(2012, 2014, gamma)
        mlbHistoricalGraph = createGraph(teams, edgeDict)
        for alpha in [ j * 0.1 for j in range(1, 10) ]:
            mlbRanking = ranking(mlbHistoricalGraph, alpha)
            historicalEval = rankingEvaluation(mlbHistoricalGraph, mlbRanking)
            currentEval = rankingEvaluation(currentMLBGraph, mlbRanking)
            mlbRandomResults.append((gamma, alpha, mlbRanking, historicalEval, currentEval))

            mlbRanking = ranking(mlbHistoricalGraph, alpha, edgeWeightSecondarySpread, edgeDict)
            historicalEval = rankingEvaluation(mlbHistoricalGraph, mlbRanking)
            currentEval = rankingEvaluation(currentMLBGraph, mlbRanking)
            mlbWinLossResults.append((gamma, alpha, mlbRanking, historicalEval, currentEval))

    randomMax = max(mlbRandomResults, key=lambda x: x[4])
    edgeWeightSecondaryMax = max(mlbWinLossResults, key=lambda x: x[4])
    print "MLB Results"
    print "==============="
    print randomMax
    print edgeWeightSecondaryMax
            
    (teams, edgeDict) = sportsdata.getNFLEdges(2015, 2015)
    currentNFLGraph = createGraph(teams, edgeDict)

    nflRandomResults = []
    nflWinLossResults = []
    for gamma in [ i * 0.1 for i in range(0, 11) ]:
        (teams, edgeDict) = sportsdata.getNFLEdges(2012, 2014, gamma)
        nflHistoricalGraph = createGraph(teams, edgeDict)
        for alpha in [ j * 0.1 for j in range(1, 10) ]:
            nflRanking = ranking(nflHistoricalGraph, alpha)
            historicalEval = rankingEvaluation(nflHistoricalGraph, nflRanking)
            currentEval = rankingEvaluation(currentNFLGraph, nflRanking)
            nflRandomResults.append((gamma, alpha, nflRanking, historicalEval, currentEval))

            nflRanking = ranking(nflHistoricalGraph, alpha, edgeWeightSecondarySpread, edgeDict)
            historicalEval = rankingEvaluation(nflHistoricalGraph, nflRanking)
            currentEval = rankingEvaluation(currentNFLGraph, nflRanking)
            nflWinLossResults.append((gamma, alpha, nflRanking, historicalEval, currentEval))

    randomMax = max(nflRandomResults, key=lambda x: x[4])
    edgeWeightSecondaryMax = max(nflWinLossResults, key=lambda x: x[4])
    print ""
    print "NFL Results"
    print "==============="
    print randomMax
    print edgeWeightSecondaryMax

    print ""
    print "Synthetic graph"
    print "==============="
    historicalSynthGraph = syntheticgraph.generateSyntheticGraph(1000, alpha = 0.25)
    currentSynthGraph = syntheticgraph.generateSyntheticGraph(1000, alpha = 0.25)
    synthRanking = ranking(historicalSynthGraph)
    evaluation = rankingEvaluation(currentSynthGraph, synthRanking)
    print evaluation
    print rankingEvaluation(historicalSynthGraph, range(1000))
    """

def createGraph(nodes, edgeDict):
    graph = snap.TNGraph.New()
    for i in range(len(nodes)):
        graph.AddNode(i)

    for edge in edgeDict:
        srcNodeID = nodes.index(edge[1])
        dstNodeID = nodes.index(edge[0])
        graph.AddEdge(srcNodeID, dstNodeID)

    return graph

def levenshtein(a,b):
    """
    Calculates the Levenshtein distance between a and b.
    """
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]

if __name__ == "__main__":
    rankingTest()
