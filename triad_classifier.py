import build_graph
from sklearn.linear_model import LogisticRegression
import numpy as np

class TriadClassifier:    
    def __init__(self,graph,weighted=False):
        self.graph=graph
        self.weighted=weighted
        self.model=None
        if not weighted:
            self.attrs,self.labels,self.weights=(self.graph.get_unweighted_attrs_and_labels())
        else:
            print "NOT CREATED YET"
            exit(1)

    def train(self):
        self.model=LogisticRegression(solver='newton-cg')
        self.model.fit(self.attrs,self.labels,self.weights)

    def classify_pair(self,node1, node2):
        attrs=np.array(self.graph.get_unweighted_partial_triads(node1,node2))        
        attrs=np.multiply(attrs,1)
        print attrs.shape
        probs=self.model.predict_log_proba(attrs)
        probs=np.exp(np.sum(probs,axis=0))
        return np.divide(probs,sum(probs))
        
    def k_folds(self,k=4):
        tp=0
        fp=0
        tn=0
        fn=0
        (graphs,test_edge_list)=self.graph.k_folds(k)
        for graph,test_edges in zip(graphs,test_edge_list):
            tc=TriadClassifier(graph)
            tc.train()
            for test in test_edges:
                node1=test[0][0]
                node2=test[0][1]
                weight=test[1]
                pred=tc.classify_pair(node1,node2)
                if 1*weight>=0:
                    if pred[0]>pred[1]:
                        tp+=1
                    else:
                        fn+=1
                else:
                    if pred[0]<pred[1]:
                        tn+=1
                    else:
                        fp+=1
        return (tp,tn,fp,fn)

if __name__=='__main__':
    tc=TriadClassifier(build_graph.build_graph('data/mlb/2015'))
    (tp,tn,fp,fn)=tc.k_folds()
    print (tp,tn,fp,fn)
    print "Accuracy: ",float(tp+tn)/(tp+fp+tn+fn)
    

