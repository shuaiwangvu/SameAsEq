# great a graph solver

import networkx as nx
import matplotlib.pyplot as plt
import random
import itertools
from operator import itemgetter
from z3 import *
import tldextract
from mygraph import MyGraph

class GraphSolver():

    def __init__(self, additional_edges = 2000):
        self.G = MyGraph()
        self.H = MyGraph()

        self.count_TN = 0.0
        self.count_FN = 0.0
        self.count_FP = 0.0
        self.count_TP = 0.0

        self.precision = 0.0
        self.recall = 0.0
        self.accuracy = 0.0

        self.o = Optimize()
        self.model = None
        self.term2id = {}
        self.id2term = {}
        self.id2encode = {}
        self.additional_edges = additional_edges

    def choose_nodes(self):
        # g = self.G.subgraphs[0]
        # i1 = random.choice(list(g.nodes))
        # i2 = random.choice(list(g.nodes))
        # while i1 == i2:
        #     i2 = random.choice(list(g.nodes))
        # return (i1, i2)
        while True:
            k = random.choice(list(self.domain_subdomain.keys()))
            if len(self.domain_subdomain[k]) >= 2:
                (t1, t2) = random.sample(self.domain_subdomain[k], 2)
                return (t1, t2)

    def compute_weight(self, t1, t2): # the most important function for now
        weight = 0
        if (t1, t2) in self.G.subgraphs[0].edges:
            weight = 10
        else:
            weight = -6


        return weight

    def load_graph(self, file_name):
        self.G.load_graph(file_name)

    def preprocessing_before_encode(self):
        g = self.G.subgraphs[0]
        self.domain = {}
        self.domain_subdomain = {}
        for n in g.nodes:
            n_domain = tldextract.extract(n).domain
            if n_domain not in self.domain.keys():
                self.domain[n_domain] = []
            self.domain[n_domain].append(n)
        for d in self.domain.keys():
            for t in self.domain[d]:
                t_subdomain = tldextract.extract(t).subdomain
                if t_subdomain != ''  and t_subdomain!= 'www':
                    x = t_subdomain + '.' + d
                    if (x) not in self.domain_subdomain.keys():
                        self.domain_subdomain[x] = []
                    self.domain_subdomain[x].append(t)
        # print ('subdomain = ', self.domain_subdomain)
        for k in self.domain_subdomain.keys():
            print ('domain.subdomain = ', k)
            print (self.domain_subdomain[k])




    def encode(self):
        # encode each node with an integer
        g = self.G.subgraphs[0]
        id = 0

        for n in g.nodes:
            self.term2id[n] = id
            self.id2term[id] = n
            # print ('node n = ', n, ' id = ', id)
            self.id2encode[id] = Int(str(self.term2id[n]))
            self.o.add(self.id2encode[id] >= 0) # we fix all values to non-negative values
            id += 1

        for (t1, t2) in g.edges:
            w = self.compute_weight(t1, t2)
            # print (t1, t2, ' have weights: ', w)
            self.o.add_soft(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]], w) # each edge within graphs

        # First, do a preprocessing before choosing nodes
        self.preprocessing_before_encode()


        # add the edges between groups, with negative weights
        i = 0
        while i < int(self.additional_edges):
            (t1, t2) = self.choose_nodes()
            w = self.compute_weight(t1, t2)
            # print (w, ' : ', t1, t2)
            self.o.add_soft(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]], w)
            i += 1

    def solve(self):
        result = self.o.check()
        print ('solving result = ', result)
        self.model = self.o.model()

    def decode (self):
        g = self.G.subgraphs[0]
        group_size = 0
        for id in self.id2encode.keys():
            # print ('eva = ', self.model.evaluate(self.id2encode[id]).as_long())
            if group_size < int(self.model.evaluate(self.id2encode[id]).as_long()):
                group_size = int(self.model.evaluate(self.id2encode[id]).as_long())
        group_size += 1
        print ('there are in total ', group_size, ' graphs')
        for m in range (group_size):
            h = nx.Graph()
            self.H.subgraphs[m] = h

        for id in self.id2encode.keys():
            group_id = int(self.model.evaluate(self.id2encode[id]).as_long())
            t = self.id2term[id]
            self.H.subgraphs[group_id].add_node(t)
            # print (group_id, ' add node ', t)

        print ('max = ', group_size)
        for m in range(group_size):
            g_tmp = g.subgraph(self.H.subgraphs[m].nodes)
            # print ('size = ', len(g_tmp.nodes))
            for (t1, t2) in g_tmp.edges:
                # for (t1, t2) in g.edges:
                # print ('THIS : ',t1, t2)
                id1 = self.term2id[t1]
                id2 = self.term2id[t2]

                if int(self.model.evaluate(self.id2encode[id1]).as_long()) == int(self.model.evaluate(self.id2encode[id2]).as_long()):
                    self.H.subgraphs[m].add_edge(t1, t2)
                # and finally add h to self.H
                # self.H.subgraphs[m] = h



if __name__ == "__main__":

    solver = GraphSolver ()
    solver.load_graph('./generate_data/SA3_7.csv')

    pos, labels = solver.G.save_graph(file_name = 'before.png')
    solver.encode()
    print ('now solve')
    solver.solve()
    print ('now decode')
    solver.decode()
    solver.H.save_graph(file_name = 'after.png',  pos=pos, labels = labels)
