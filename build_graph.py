import process_mlb
import numpy as np
import random

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
    def get_weighted_triads(self,node):
        triads=[]
        for neigh1 in self.edge_list[node]:
            for neigh2 in self.edge_list[neigh1]:
                if node in self.edge_list[neigh2] and (neigh1,neigh2):
                    if (node,neigh1) in self.edge_dict and (neigh1,neigh2) in self.edge_dict and (neigh2,node) in self.edge_dict:
                        triads.append((self.edge_dict[(node,neigh1)],self.edge_dict[(neigh1,neigh2)],self.edge_dict[(neigh2,node)]))
        return triads

    #Just treats them as positive or negative edges, discards edges with weight 0
    #Returns a dict where the keys are 3-tuples of booleans, where true means win, false means lose and the order is:
    # (node->neigh1, node->neigh2, neigh2->node), note that there are repeats because we make edges in both directions.
    #e.g. (False, False, False) which is node loses to neigh1 loses to neigh2 loses to node is the same as (True,True,True)
    #Which is node beats neigh2 beats neigh1 beats node
    def get_unweighted_triads(self,node):
        weighted_triads=self.get_weighted_triads(node)
        unweighted_triads={}
        for triad in weighted_triads:
            if 0 in triad:
                continue
            signs=(triad[0]>0,triad[1]>0,triad[2]>0)
            unweighted_triads[signs]=unweighted_triads.get(signs,0)+1
        return unweighted_triads

    #Does this for the whole graph
    def get_all_weighted_triads(self):
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
                triads[(k1,k2,k3)]=triads.get((k1,k2,k3),0)+t[(k1,k2,k3)]
        return triads
    
    def get_unweighted_attrs_and_labels(self):
        triads=self.get_all_unweighted_triads()
        attrs=np.zeros((len(triads),2))
        labels=np.zeros((len(triads)))
        weights=np.zeros((len(triads)))
        i=0
        for triad in triads:
            attrs[i,0]=1*triad[0]
            attrs[i,1]=1*triad[1]
            labels[i]=1*triad[2]
            weights[i]=triads[triad]
            i+=1
        return (attrs,labels,weights)

    def get_weighted_partial_triads(self,node1,node2):
        partial=[]
        for neigh in self.edge_list[node1]:
            if node2 in self.edge_list[neigh]:
                    partial.append((self.edge_dict[(node1,neigh)],self.edge_dict[(neigh,node2)]))
        return partial

    def get_unweighted_partial_triads(self,node1,node2):
        partial=[]
        for neigh in self.edge_list[node1]:
            if node2 in self.edge_list[neigh]:
                if (node1,neigh) in self.edge_dict and (neigh,node2) in self.edge_dict and self.edge_dict[(node1,neigh)]!=0 and self.edge_dict[(neigh,node2)]!=0:
                    partial.append((self.edge_dict[(node1,neigh)]>0,self.edge_dict[(neigh,node2)]>0))
        return partial

    #returns a length k tuple of (graph, [(node1,node2,edge_weight)...]) where node1 and node2 are nodes that previously had an edge between them 
    #with weight/sign edge_weight, but it was removed so is now test data
    def k_folds(self,k):
        out_test_edges=[]
        edges=[]
        for edge in self.edge_dict:
            edges.append((edge,self.edge_dict[edge]))
        random.shuffle(edges)
        graphs=[]
        interval=len(edges)/float(k)
        for i in range(k):
            new_dict={}
            test_edges=edges[int(i*interval):int((i+1)*interval)]
            train_edges=edges[:int(i*interval)]
            train_edges.extend(edges[int((i+1)*interval):])
            for edge in train_edges:
                new_dict[edge[0]]=edge[1]
            graphs.append(Graph(self.nodes, new_dict))
            out_test_edges.append(test_edges)
        return (graphs,out_test_edges)

def build_graph(data_folder):
    (nodes,edge_dict)=process_mlb.read_folder(data_folder)
    return Graph(nodes,edge_dict)

        

if __name__=='__main__':
    graph=build_graph('data/mlb/2015')
    #    print graph.get_unweighted_partial_triads('NYY','BOS')
    #    print graph.get_all_unweighted_triads()
    graphs,test_edges=graph.k_folds(4)
#    print len(graphs, test_edges)
