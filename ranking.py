import snap
import random

def ranking(graph, alpha):
    """
    Implements the node ranking algorithm described by Guo, Yang, and Zhou

    Args:
        graph (snap.TNGraph): a directed graph to rank
        alpha (float): the relative size of the leader partition

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
        random.shuffle(degDiffs[key])
        nodeOrdering += degDiffs[key]

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
    return ranking(leaderGraph, alpha) + ranking(followerGraph, alpha)

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
    testGraph.AddEdge(6, 5)
    testGraph.AddEdge(5, 7)
    testGraph.AddEdge(0, 5)
    testGraph.AddEdge(1, 5)
    testGraph.AddEdge(2, 5)
    testGraph.AddEdge(3, 5)
    testGraph.AddEdge(1, 6)
    testGraph.AddEdge(2, 6)
    testGraph.AddEdge(3, 6)
    testGraph.AddEdge(4, 6)

    nodeRanking = ranking(testGraph, 0.6)
    print nodeRanking
    print rankingEvaluation(testGraph, nodeRanking)

if __name__ == "__main__":
    rankingTest()
