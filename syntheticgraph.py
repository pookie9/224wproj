import snap
import random

def generateSyntheticGraph(numNodes, alpha = 0.3, seed = None):
    """
    Generates a directed tournament graph with nodes 0, ..., numNodes - 1
    where an edge points from node i to node j if i < j with probability 1 - alpha
    and in the other direction with probability alpha

    Args:
        numNodes (int): the number of nodes in the graph
        alpha (float): the probability that an edge flips its direction
        seed (object): a seed for random
    
    Returns:
        graph (snap.TNGraph): the generated graph
    """

    if seed is not None:
        random.seed(seed)

    graph = snap.TNGraph.New()
    for i in range(numNodes):
        graph.AddNode(i)

    for i in range(numNodes):
        for j in range(i + 1, numNodes):
            if random.random() < alpha:
                graph.AddEdge(i, j)
            else:
                graph.AddEdge(j, i)

    return graph
