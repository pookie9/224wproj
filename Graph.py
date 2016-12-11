import mlbgame
import nflgame
import random
import numpy as np
from sklearn.linear_model import LogisticRegression
from collections import defaultdict

#Adds the values in dict1 to dict2 and returns it
def add(dict1, dict2):
    out=defaultdict(int)
    for key in dict1:
        if key not in dict2:
            out[key]=dict1[key]
    for key in dict2:
        out[key]=dict1[key]+dict2[key]
    return out
class Graph(object):
    
    #Edge list is a list of edges from winners to losers
    def __init__(self, edge_list,hits=False):
        self.edge_list={}#Maps ids to lists of neigbhors

        self.edge_weights={}#Maps tuples of (node1, node2) to True or False, True means node1 beat node2, False means node2 beat node1
        for edge in edge_list:
            if edge[0] not in self.edge_list:
                self.edge_list[edge[0]]=[]
            if edge[1] not in self.edge_list:
                self.edge_list[edge[1]]=[]
            self.edge_list[edge[0]].append(edge[1])
            self.edge_list[edge[1]].append(edge[0])
            self.edge_weights[edge]=True
            self.edge_weights[(edge[1],edge[0])]=False
        self.hits=None
        attrs,labels=self.get_all_features(hits=hits)
        self.model=LogisticRegression()
        self.model.fit(attrs,labels)
    
    #Returns a dictionary of types of triads starting at node1, going to intermediarary, node2, and then node1 mapped to counts
    def get_triads(self,node1,node2):        
        triads=defaultdict(int)#types of triads to counts, e.g. (True, False, True):4
        if node1 not in self.edge_list[node2]:
            return triads
        for neigh1 in self.edge_list[node1]:
            if node2 in self.edge_list[neigh1]:
                triads[(self.edge_weights[(node1,neigh1)],self.edge_weights[(neigh1,node2)],self.edge_weights[(node2,node1)])]+=1
        return triads
        
    def get_all_triads(self):
        triads=defaultdict(int)
        for node in self.edge_list:
            for neigh in self.edge_list[node]:
                triads=add(triads,self.get_triads(node,neigh))
        return triads
    
    def get_partial_triads(self,node1,node2):
        triads={(True,True):0,(True,False):0,(False,True):0,(False,False):0}
        for neigh1 in self.edge_list[node1]:
            if node2 in self.edge_list[neigh1]:
                triads[(self.edge_weights[(node1,neigh1)],self.edge_weights[(neigh1,node2)])]+=1
        return triads
    
    #Returns a numpy array of features and labels, note that the ordering of the features is done by sorting the keys
    def get_all_features(self,hits=False):
        if hits:
            attrs=np.zeros((0,6))
            if self.hits==None:
                self.hits=HITS(self.edge_list.keys(),self.edge_list)
        else:
            attrs=np.zeros((0,4))
        labels=np.zeros((0))
        for node in self.edge_list:
            for neigh in self.edge_list[node]:
                cur_attrs=sorted(self.get_partial_triads(node,neigh).items())
                if hits:
                    cur_attrs=[item[1] for item in cur_attrs]
                    cur_attrs.extend([self.hits[node],self.hits[neigh]])
                    cur_attrs=np.array(cur_attrs).reshape((1,6))
                else:
                    cur_attrs=np.array([item[1] for item in cur_attrs])
                    cur_attrs=cur_attrs.reshape((1,4))
                attrs=np.append(attrs,cur_attrs,axis=0)
                labels=np.append(labels,1*self.edge_weights[(node,neigh)])
        return attrs,labels

        
    def predict(self,node1,node2,model=None):
        cur_attrs=sorted(self.get_partial_triads(node1,node2).items())
        if self.hits:
            cur_attrs=[item[1] for item in cur_attrs]
            cur_attrs.extend([self.hits[node1],self.hits[node2]])
            cur_attrs=np.array(cur_attrs).reshape((1,6))
        else:
            cur_attrs=np.array([item[1] for item in cur_attrs])
            cur_attrs=cur_attrs.reshape((1,4))
        if model==None:
            return self.model.predict(cur_attrs)
        else:
            print "Using foreign model"
            return model.predict(cur_attrs)

#Returns a length k list of 2 tuples where the first element of each tuple is a list of training examples
#and the second is a list of test examples
def k_folds(edge_list,k=20):
    random.shuffle(edge_list)
    out=[]
    fold_size=float(len(edge_list)/k)
    for i in range(k):
        test=edge_list[int(i*fold_size):int((i+1)*fold_size)]
        train=edge_list[:int(i*fold_size)]
        train.extend(edge_list[int((i+1)*fold_size):])
        out.append((train,test))
    return out
        
def eval_acc(edge_list,model=None,hits=False):
    folds=k_folds(edge_list)
    accs=[]
    for fold in folds:
        g=Graph(fold[0],hits=hits)
        correct=0
        wrong=0
        for edge in fold[1]:
            if g.predict(edge[0],edge[1],model)==1:
                correct+=1
            else:
                wrong+=1
            if g.predict(edge[1],edge[0])==0:
                correct+=1
            else:
                wrong+=1            
        accs.append(float(correct)/(correct+wrong))
    print sum(accs)/len(accs)

def mlb_edge_list(year):
    teams = [ team.club.upper() for team in mlbgame.teams() ]
    edge_list=[]
    edge_weights={}
    games = mlbgame.combine_games(mlbgame.games(year))
    team_dict = { team.club_common_name : team.club.upper() for team in mlbgame.teams() }
    for game in games:
        try:
            if str(game.w_team) not in team_dict or str(game.l_team) not in team_dict:
                continue
            w_team=team_dict[game.w_team]
            l_team=team_dict[game.l_team]
            if (str(w_team),str(l_team)) in edge_list:
                edge_weights[(str(w_team),str(l_team))]+=1
            else:
                edge_weights[(str(w_team),str(l_team))]=1#abs(game.score_home-game.score_away)
            edge_list.append((str(w_team),str(l_team)))
        except AttributeError:
            pass
    new_edge_list=[]
    for winner,loser in edge_list:
        if (loser,winner) not in edge_weights or edge_weights[(winner,loser)]>edge_weights[(loser,winner)]:
            new_edge_list.append((winner,loser))
    return new_edge_list

def nfl_edge_list(year):
    teams = [ str(team[0]) for team in nflgame.teams ]
    games=nflgame.games(year)
    edge_list=[]
    for game in games:
        if game.winner in teams and game.loser in teams:
            edge_list.append((str(game.winner),str(game.loser)))
    return edge_list

def HITS(nodes,edge_list):
    authorities={}
    hubs={}
    for node in nodes:
        authorities[node]=1.0
    for i in range(100):
        total_auth=0.0
        for node in edge_list:
            authorities[node]+=sum([authorities[neigh] for neigh in edge_list[node]])
            total_auth+=sum([authorities[neigh] for neigh in edge_list[node]])
        for node in edge_list:
            authorities[node]/=(total_auth**.5)
    total=0.0
    for node in edge_list:
        total+=authorities[node]
    for node in edge_list:
        authorities[node]/=total/100
    return authorities


if __name__=='__main__':

    random.seed(10)
    edge_list=mlb_edge_list(2015)    
    eval_acc(edge_list,hits=True)
    
