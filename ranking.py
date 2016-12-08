import snap
import process_mlb
import random

def randomShuffle(nodes, graph, edgeAttrs):
    random.shuffle(nodes)
    return nodes

def winLossSpread(nodes, graph, edgeAttrs):
    diffs = { node : 0 for node in nodes }
    for node in nodes:
        winningEdges = [ edge for edge in edgeAttrs if edge[1] == node]
        losingEdges = [ edge for edge in edgeAttrs if edge[0] == node]
        for edge in winningEdges:
            diffs[node] += edgeAttrs[edge]
        for edge in losingEdges:
            diffs[node] -= edgeAttrs[edge]
    return sorted(diffs, key=lambda nodeID: diffs[nodeID], reverse=True)

def ranking(graph, alpha, tiebreaker=randomShuffle, edgeAttrs=None):
    """
    Implements the node ranking algorithm described by Guo, Yang, and Zhou

    Args:
        graph (snap.TNGraph): a directed graph to rank
        alpha (float): the relative size of the leader partition
        tiebreaker ((nodes, graph, edgeAttrs) -> nodes): a tiebreaking function for nodes
            with the same degree difference
    Returns:
        A list of node IDs ordered in descending order by ranking
    """
    
    # Group the nodes by degree difference (d_in - d_out)
    degDiffs = {}
    for node in graph.Nodes():
        degDiff = node.GetInDeg() - node.GetOutDeg()
        if degDiff in degDiffs:
            degDiffs[degDiff] += [node.GetId()]
        else:
            degDiffs[degDiff] = [node.GetId()]

    # Generate a descending ordering where nodes with same degree difference
    # are randomly ordered
    nodeOrdering = []
    for key in sorted(degDiffs.keys(), reverse=True):
        nodeOrdering += tiebreaker(degDiffs[key], graph, edgeAttrs)

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
    return ranking(leaderGraph, alpha, tiebreaker, edgeAttrs) + ranking(followerGraph, alpha, tiebreaker, edgeAttrs)


def rankingEvaluation(graph, ranking):
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

def rankingTest():
    testGraph = snap.TNGraph.New()
    for i in range(9):
        testGraph.AddNode(i)

    testGraph.AddEdge(7, 8)
    testGraph.AddEdge(6, 7)
    testGraph.AddEdge(5, 7)
    testGraph.AddEdge(0, 5)
    testGraph.AddEdge(1, 5)
    testGraph.AddEdge(2, 5)
    testGraph.AddEdge(3, 5)
    testGraph.AddEdge(1, 6)
    testGraph.AddEdge(2, 6)
    testGraph.AddEdge(3, 6)
    testGraph.AddEdge(4, 6)

    edgeDict = {}
    edgeDict[(7, 8)] = 1
    edgeDict[(6, 7)] = 1
    edgeDict[(5, 7)] = 1
    edgeDict[(0, 5)] = 5
    edgeDict[(1, 5)] = 5
    edgeDict[(2, 5)] = 5
    edgeDict[(3, 5)] = 5
    edgeDict[(1, 6)] = 5
    edgeDict[(2, 6)] = 5
    edgeDict[(3, 6)] = 5
    edgeDict[(4, 6)] = 5

    nodeRanking = ranking(testGraph, 0.6)
    print "Toy graph results (random)"
    print "================="
    print nodeRanking
    print rankingEvaluation(testGraph, nodeRanking)

    nodeRanking = ranking(testGraph, 0.6, winLossSpread, edgeDict)
    print "Toy graph results (win/loss spread)"
    print "================="
    print nodeRanking
    print rankingEvaluation(testGraph, nodeRanking)

    mlbGraph = snap.TNGraph.New()
    (nodes, edgeDict) = process_mlb.read_folder('data/mlb/2015')
    #print nodes
    #print [ game for game in edgeDict if game[0] == "OAK" or game[1] == "OAK" ]

    for i in range(len(nodes)):
        mlbGraph.AddNode(i)

    # Take only the edges with positive weight, representing team1 beating team2
    edgeDict = { edge : edgeDict[edge] for edge in edgeDict if edgeDict[edge] > 0}
    for edge in edgeDict:
        srcNodeID = nodes.index(edge[1])
        dstNodeID = nodes.index(edge[0])
        mlbGraph.AddEdge(srcNodeID, dstNodeID)

    print ""
    print "MLB graph results (random)"
    print "================="
    for alpha10 in range(1, 10):
        alpha = alpha10 * 0.1
        print "alpha:", alpha
        mlbRanking = ranking(mlbGraph, alpha)
        evaluation = rankingEvaluation(mlbGraph, mlbRanking)

        print [nodes[i] for i in mlbRanking]
        print evaluation
        print ""

    print "MLB graph results (win/loss tiebreak)"
    print "================="
    for alpha10 in range(1, 10):
        alpha = alpha10 * 0.1
        print "alpha:", alpha
        mlbRanking = ranking(mlbGraph, alpha, winLossSpread, edgeDict)
        evaluation = rankingEvaluation(mlbGraph, mlbRanking)

        print [nodes[i] for i in mlbRanking]
        print evaluation
        print ""

if __name__ == "__main__":
    rankingTest()
