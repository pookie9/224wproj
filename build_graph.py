import process_mlb
class Graph:
    def __init__(self,nodes,edge_dict):
        self.nodes=nodes
        self.edge_dict=edge_dict
        self.edge_list={}
        for node in nodes:
            self.edge_list[node]=[]
        for edge in edge_dict:
            self.edge_list[edge[0]].append(edge[1])
            self.edge_list[edge[1]].append(edge[0])
    #Returns all triads that involve the given node
    def get_all_weighted_triads(self,node):
        triads=[]
        already_seen={}
        for neigh1 in self.edge_list[node]:
            for neigh2 in self.edge_list[neigh1]:
                if node in self.edge_list[neigh2] and (neigh1,neigh2) not in already_seen:
                    #already_seen[(neigh1,neigh2)]=True
                    #already_seen[(neigh2,neigh1)]=True
                    triads.append((self.edge_dict[(node,neigh1)],self.edge_dict[(neigh1,neigh2)],self.edge_dict[(neigh2,node)]))
        return triads

    #Just treats them as positive or negative edges, discards edges with weight 0
    #Returns a dict where the keys are 3-tuples of booleans, where true means win, false means lose and the order is:
    # (node->neigh1, node->neigh2, neigh2->node), note that there are repeats because we make edges in both directions.
    #e.g. (False, False, False) which is node loses to neigh1 loses to neigh2 loses to node is the same as (True,True,True)
    #Which is node beats neigh2 beats neigh1 beats node
    def get_all_unweighted_triads(self,node):
        weighted_triads=self.get_weighted_triads(node)
        unweighted_triads={}
        for triad in weighted_triads:
            if 0 in triad:
                continue
            signs=(triad[0]>0,triad[1]>0,triad[2]>0)
            unweighted_triads[signs]=unweighted_triads.get(signs,0)+1
        return unweighted_triads
        
    #Does this for the whole graph
    def get_weighted_triads(self):
        triads=[]
        for node in self.nodes:
            triads.append(self.get_weighted_triads(node))
        return triads
    #Gets for whole graph
    def get_all_unweighted_triads(self):
        triads={}
        for node in self.nodes:
            t=self.get_unweighted_triads(node)
            for k1,k2,k3 in t:
                triads[(k1,k2,k3)]+=t[(k1,k2,k3)]
        return triads
def build_graph(data_folder):
    (nodes,edge_dict)=process_mlb.read_folder(data_folder)
    return Graph(nodes,edge_dict)
        

if __name__=='__main__':
    graph=build_graph('data/mlb/2015')
    print graph.get_all_unweighted_triads()
