import mlbgame
import nflgame
import numpy as np
from numpy.linalg import norm
from numpy.linalg import eig
import random

#Returns a dictionary of the HITS score for each node.
#HITS is generally supposed to work in a directed graph, so to modify it to work in an undirected setting I
#am not using hubs, because hubs and authorities are essentially the same in the undirected setting. 
#So I am just updating authorities, using authorities. Also, I am only utilizing edges where consorting appears.
#So failed attempts do not influence the HITS score for a node.
def HITS(nodes,edge_list,edge_weights):
    authorities={}
    hubs={}
    for node in nodes:
        authorities[node]=1.0
    for i in range(100):
        total_auth=0.0
        for edge in edge_list:
            authorities[edge[0]]+=authorities[edge[1]]
            total_auth+=authorities[edge[1]]
        for node in nodes:
            authorities[node]/=(total_auth**.5)
    return authorities

#Regular pagerank, beta is 1 minus the teleport probability, so set it to 1 to never teleport
#ids is a list of tuples where the first element is the first baboons id, second is the second baboons id
#1 indicating consort, 0 indicating non-consort
#Note that like HITS we only utilize the successful edges, but unlike in HITS we utilize the number of successes. E.g.
#A successfully connecting with B twice means that it gets twice the amount of rank from B then if it did it once.
#Also, note that like HITS we are treating this as undirected.
#ids, attrs, labels 
def PageRank(ids,labels,beta=.9):
    edge_list,edge_class=construct_edges(ids,labels)
    #Constructing weighted adjacency matrix
    M=np.zeros((len(edge_list),len(edge_list)))
    indices={}
    counter=0
    for node in edge_list:
        if node not in indices:
            indices[node]=counter
            counter+=1
        num_edges=0
        for neigh in edge_list[node]:
            num_edges+=edge_class[(node,neigh)].count(1)
        for neigh in edge_list[node]:
            if neigh not in indices:
                indices[neigh]=counter
                counter+=1
            if num_edges>0:
                M[indices[node],indices[neigh]]=edge_class[(node,neigh)].count(1)/float(num_edges)
    M=beta*M+(1-beta)/float(M.size)
    values,vectors=eig(M.T)
    largest_index=0
    for i in range(len(values)):
        if values[i]>values[largest_index]:
            largest_index=i
    principle_vector=vectors[:,largest_index]
    principle_vector/=sum(principle_vector)
    ranks={}
    for node in indices:
        ranks[node]=principle_vector[indices[node]]
    return ranks

def construct_edges(ids, labels):
    features=[]
    for i in range(len(ids)):
        features.append((ids[i][0],ids[i][1],labels[i]))
    edge_list={}
    edge_class={}
    counter=0
    for entry in features:
        if entry[0] not in edge_list:
            edge_list[entry[0]]=[]
        if entry[1] not in edge_list:
            edge_list[entry[1]]=[]
        if entry[1] not in edge_list[entry[0]]:
            edge_list[entry[0]].append(entry[1])
        if entry[0] not in edge_list[entry[1]]:
            edge_list[entry[1]].append(entry[0])
        if (entry[0],entry[1]) not in edge_class:
            edge_class[(entry[0],entry[1])]=[]
            edge_class[(entry[1],entry[0])]=[]
        edge_class[(entry[0],entry[1])].append(entry[2])
        edge_class[(entry[1],entry[0])].append(entry[2])
    size=0
    return (edge_list,edge_class)

#Returns a length k list of 2 tuples where the first element of each tuple is a list of training examples
#and the second is a list of test examples
def k_folds(edge_list,k=5):
    random.shuffle(edge_list)
    out=[]
    fold_size=float(len(edge_list)/k)
    for i in range(k):
        test=edge_list[int(i*fold_size):int((i+1)*fold_size)]
        train=edge_list[:int(i*fold_size)]
        train.extend(edge_list[int((i+1)*fold_size):])
        out.append((train,test))
    return out

def eval_acc(nodes,edge_list,edge_weights):
    folds=k_folds(edge_list)
    accs=[]
    for fold in folds:
        auths=HITS(nodes,edge_list,edge_weights)
        #auths={"NE":100,"SD":99,"PHI":98,"IND":97,"ATL":96,'OAK':95,'NYG':94,'DAL':93,'HOU':92,'GB':91,'NO':90,'PIT':89,'NYJ':88,'KC':87,'DET':86.5,'BAL':86,'TEN':85,'JAC':84,'DEN':83,'TB':82,'CHI':81,'CIN':80,'SEA':23,'SF':22,'WAS':21,'STL':20,'ARI':19,'BUF':18,'MIN':17,'MIA':16,'CLE':15,'CAR':14} #NFL 2010
        correct=0
        wrong=0
        for game in fold[1]:
            if auths[game[0]]>auths[game[1]]:
                correct+=1
            else:
                wrong+=1
        accs.append(float(correct)/(correct+wrong))
    print sum(accs)/len(accs)



if __name__=='__main__':
    random.seed(10)
    teams = [ str(team[0]) for team in nflgame.teams ]
    games=nflgame.games(2011)

    #print games
    print teams
    edge_list=[]
    edge_weights={}
    for game in games:
        if str(game.winner) not in teams or str(game.loser) not in teams:
            continue
        if (str(game.winner),str(game.loser)) in edge_list:
            edge_weights[(str(game.winner),str(game.loser))]=max(edge_weights[(str(game.winner),str(game.loser))],abs(game.score_home-game.score_away))
        else:
            edge_weights[(str(game.winner),str(game.loser))]=abs(game.score_home-game.score_away)
        edge_list.append((str(game.winner),str(game.loser)))
    eval_acc(teams,edge_list,edge_weights)
    """
    teams = [ team.club.upper() for team in mlbgame.teams() ]
    print teams
    games=mlbgame.combine_games(mlbgame.games(2010))
    edge_list=[]
    edge_weights={}
    games = mlbgame.combine_games(mlbgame.games(2015))
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
#            edge_weights[(winner,loser)]=edge_weights[(winner,loser)]-edge_weights[(loser,winner)]
    edge_list=list(set(new_edge_list))
        
    print edge_weights
#    print edge_list
#    print len(edge_list)
"""
#    eval_acc(teams,edge_list,edge_weights)
