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
        
    
if __name__=='__main__':
    tc=TriadClassifier(build_graph.build_graph('data/mlb/2015'))
    tc.train()
    print tc.classify_pair('NYY','BOS')
