# great a graph solver

import networkx as nx
import matplotlib.pyplot as plt
import random
import itertools
from operator import itemgetter
from z3 import *
import tldextract
from mygraph import MyGraph
import urllib.parse
import datetime
import pickle
import time
import csv


IDENTICAL = 0
CONV_IDENTICAL = 0
DIFFERENT = 1

WEIGHT_EXISTING_ATTACKING_EDGES = -5
WEIGHT_EXISTING_EQUIVALENT_EDGES = 20
WEIGHT_ADDITIONAL_ATTACKING_EDGES = -5
WEIGHT_NORMAL_EDGES = 10

class GraphSolver():

    def __init__(self):
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
        timeout = 1000 * 60 * 5 # 5 mins
        self.o.set("timeout", timeout)
        print('timeout = ',timeout/1000/60, 'mins')

        self.model = None
        self.term2id = {}
        self.id2term = {}
        self.id2encode = {}
        self.existing_equivalent_edges = []
        self.existing_attacking_edges = [] # already in the graph
        self.additional_attacking_edges = [] # all additional edges in the graph
        self.num_subgraphs = 0
        self.num_removed_edges = 0
        self.removed_edges = []

        self.pos = None

    def compare_names (self, t1, t2):
        n1 = t1.rsplit('/', 1)[-1]
        n2 = t2.rsplit('/', 1)[-1]
        # print ('n1 = ', n1)
        # print ('n2 = ', n2)
        # print ('urllib n1 = ', urllib.parse.quote(n1))
        # print ('urllib n2 = ', urllib.parse.quote(n2))
        if (urllib.parse.quote(n2) == n1 or n2 == urllib.parse.quote(n1)):
            return IDENTICAL
        else: # process it bit by bit and obtain the
            coll_n1 = ''
            for t in n1:
                if t == '(' or t == ')':
                    coll_n1 += t
                else:
                    coll_n1 += urllib.parse.quote(t)

            coll_n2 = ''
            for t in n2:
                if t == '(' or t == ')':
                    coll_n2 += t
                else:
                    coll_n2 += urllib.parse.quote(t)
            # print ('conv n1 = ', coll_n1)
            # print ('conv n2 = ', coll_n2)

            if (n1 == coll_n2 or coll_n1 == n2):
                return CONV_IDENTICAL # identical after conversion

            # ====== NOW AGAIN ======
            coll_n1 = ''
            for t in n1:
                if t == '(' or t == ')' or t == '\'':
                    coll_n1 += t
                else:
                    coll_n1 += urllib.parse.quote(t)

            coll_n2 = ''
            for t in n2:
                if t == '(' or t == ')'or t == '\'':
                    coll_n2 += t
                else:
                    coll_n2 += urllib.parse.quote(t)

            # print ('*conv n1 = ', coll_n1)
            # print ('*conv n2 = ', coll_n2)
            if (n1 == coll_n2 or coll_n1 == n2):
                return CONV_IDENTICAL # identical after conversion

            # ====== NOW AGAIN ======
            coll_n1 = ''
            for t in n1:
                if t == '(' or t == ')' or t == '\'' or t == ',':
                    coll_n1 += t
                else:
                    coll_n1 += urllib.parse.quote(t)

            coll_n2 = ''
            for t in n2:
                if t == '(' or t == ')'or t == '\'' or t == ',':
                    coll_n2 += t
                else:
                    coll_n2 += urllib.parse.quote(t)

            # print ('*conv n1 = ', coll_n1)
            # print ('*conv n2 = ', coll_n2)
            if (n1 == coll_n2 or coll_n1 == n2):
                return CONV_IDENTICAL # identical after conversion

            else:
                # print (t1,' => ', n1, ' is now ',coll_n1)
                # print (t2,' => ', n2, ' is now ',coll_n2,'\n')
                return DIFFERENT

    def find_existing_attacking_edges(self):
        count_SAME = 0
        count_DIFF = 0
        coll_existing_attacking_edges = []
        for (t1, t2) in self.G.subgraphs[0].edges:
            t1_domain = tldextract.extract(t1).domain
            t1_subdomain = tldextract.extract(t1).subdomain
            t2_domain = tldextract.extract(t2).domain
            t2_subdomain = tldextract.extract(t2).subdomain


            if t1_subdomain != '' and t2_subdomain != '' and t1_domain == t2_domain and t1_subdomain == t2_subdomain:
                if (self.compare_names(t1, t2) == DIFFERENT):
                    self.existing_attacking_edges.append((t1, t2))
                    count_DIFF += 1
                    # print ('DIFF: ', t1, t2)
                else:
                    count_SAME += 1
                    self.existing_equivalent_edges.append((t1, t2))
        # print ('SAME = ', count_SAME)
        # print ('DIFF = ', count_DIFF)

    def find_additional_attacking_edges(self):
        for x in self.domain_subdomain.keys():
            if len(self.domain_subdomain[x]) >= 2:
                for t1 in self.domain_subdomain[x]:
                    for t2 in self.domain_subdomain[x]:
                        if t1 != t2:
                            if (self.compare_names(t1, t2) == DIFFERENT):
                                self.additional_attacking_edges.append((t1, t2))


    # def compute_weight(self, t1, t2): # the most important function for now
    #     weight = 0
    #     if (t1, t2) in self.G.subgraphs[0].edges:
    #         weight = 10
    #     else:
    #         weight = -6
    #     return weight

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
        # for k in self.domain_subdomain.keys():
        #     print ('domain.subdomain = ', k)
        #     print (self.domain_subdomain[k])




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
            self.o.add(self.id2encode[id] < 50) # we fix all values to non-negative values
            id += 1
        # First, do a preprocessing before choosing nodes
        self.preprocessing_before_encode()

        # find existing attacking edges: #TODO change the weight function
        print ('There are in total ', len (self.G.subgraphs[0].edges))
        edges = list(g.edges).copy()
        self.find_existing_attacking_edges()
        for (t1, t2) in self.existing_attacking_edges:
            self.o.add_soft(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]], WEIGHT_EXISTING_ATTACKING_EDGES)
            # print('existing attacking edge: ', t1, t2)
        print('\tThere are in total: ', len (self.existing_attacking_edges), ' existing attacking edges!')
        for (t1, t2) in self.existing_equivalent_edges:
            self.o.add_soft(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]],  WEIGHT_EXISTING_EQUIVALENT_EDGES)
            # print('existing equivalent edge: ', t1, t2)
        print('\tThere are in total: ', len (self.existing_equivalent_edges), ' existing equivalence edges!')

        edges = list(filter(lambda x: x not in self.existing_attacking_edges, edges))
        edges = list(filter(lambda x: x not in self.existing_equivalent_edges, edges))
        print ('Now there are normal', len(edges), ' edges left')
        # other normal edges
        for (t1, t2) in edges:
            self.o.add_soft(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]], WEIGHT_NORMAL_EDGES) # each edge within graphs

        # find additional attacking edges:
        self.find_additional_attacking_edges()
        for (t1, t2) in self.additional_attacking_edges:
            # self.o.add(Not(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]])) # each edge within graphs
            self.o.add_soft(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]], WEIGHT_ADDITIONAL_ATTACKING_EDGES) # each edge within graphs
        print('There are in total: ', len (self.additional_attacking_edges), ' additional attacking edges!')


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
        # print ('there are in total ', group_size, ' graphs')
        for m in range (group_size):
            h = nx.Graph()
            self.H.subgraphs[m] = h

        for id in self.id2encode.keys():
            group_id = int(self.model.evaluate(self.id2encode[id]).as_long())
            t = self.id2term[id]
            self.H.subgraphs[group_id].add_node(t)
            # print (group_id, ' add node ', t)

        # print ('max = ', group_size)
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
        # TODO: tidy up the group index/id so there is no empty graph in it
        tmp = self.G.subgraphs[0].copy()

        ind = 0
        dict = {}
        acc_num_edges = 0
        for k in self.H.subgraphs.keys():
            g = self.H.subgraphs[k]
            tmp.remove_edges_from(g.edges)
            if len (g.nodes) != 0:
                acc_num_edges += len(self.H.subgraphs[k].edges)
                dict[ind] = g
                ind += 1
        self.H.subgraphs = dict
        print('there are in total ', ind, ' subgraphs in the solution')
        print ('and they have ', acc_num_edges, ' edges')

        # for e in self.G.subgraphs[0].edges:
        #     if e not in Big.edges:
        #         self.removed_edges.append(e)
        self.removed_edges = tmp.edges

        self.num_removed_edges = len(self.G.subgraphs[0].edges) - acc_num_edges
        print ('SHOULD BE EQUAL: ', self.num_removed_edges, ' = ',len(self.removed_edges))
        self.num_subgraphs = ind

    def obtain_statistics(self, file_name):
        dict_al = {}

        print ('obtain statistics now!')
        print ('compare against the manual decision from AL in the file ', file_name)
        # now load the data in
        # file_name = str(n) + '_annotation.txt'
        print ('File Name = ', file_name)
        file = open(file_name, 'r')
        reader = csv.DictReader(file, delimiter = '\t')
        for row in reader:
            e = row["Entity"]
            o = row["Annotation"]
            dict_al [e] = o

        # al_count_remain = 0
        al_remain = []
        # al_count_remove = 0
        al_removed = []

        my_remain = list(filter(lambda v: v not in self.removed_edges, self.G.subgraphs[0].edges))
        my_removed = self.removed_edges

        count_edges_involving_unknow = 0

        for (l, r) in self.G.subgraphs[0].edges:
            if dict_al[l] != 'Uncertain' and dict_al[r] != 'Uncertain': # Error
                if dict_al[l] == dict_al[r] :
                    al_remain.append((l,r))
                else:
                    # al_count_remove += 1
                    al_removed.append((l,r))

        print ('# al removed: ', len(al_removed))
        print ('# al remain: ', len(al_remain))

        print('# my removed:', len(my_removed))
        print('# my remain:', len(my_remain))

        for e in self.G.subgraphs[0].edges:
            (l, r) = e
            if dict_al[l] != 'Uncertain' and dict_al[r] != 'Uncertain':
                if e in my_remain and e in al_remain:
                    self.count_TN += 1
                elif e in my_removed and e in al_removed:
                    self.count_TP += 1
                elif e in my_remain and e in al_removed:
                    self.count_FN += 1
                elif e in my_removed and e in al_remain:
                    self.count_FP += 1
                else:
                    print ('error', l, ' and ', r)
            else :
                count_edges_involving_unknow += 1

        print ('Total edges ', len(self.G.subgraphs[0].edges))
        print ('There are in total ', count_edges_involving_unknow, ' edges involving unknown')

        print ('==============================')

        print ('TP = both remove: ', self.count_TP)
        print ('TN = both keep:   ', self.count_TN)
        print ('FP = predicted to remove but SHOULD KEEP: ', self.count_FP)
        print ('FN = predicted to keep but SHOULD REMOVE: ', self.count_FN)

        print ('==============================')

        if self.count_TP + self.count_FP  != 0:
            self.precision = self.count_TP / (self.count_TP + self.count_FP)
            print('precision = TP/(TP+FP) = ', self.precision)  #TP/TP + FP
        if self.count_TP + self.count_FN != 0:
            self.recall = self.count_TP / (self.count_TP + self.count_FN )
            print('recall  = TP / (FN+TP) = ', self.recall) # TP / ( FN +  TP)

        self.accuracy = (self.count_TN + self.count_TP) / (len(self.G.subgraphs[0].edges) - count_edges_involving_unknow)
        print('accuracy = ', self.accuracy) #

if __name__ == "__main__":

    start = time.time()

    name_list = []

    f = open("process.txt", "r")
    for l in f:
        print ('Now working on group index', l[:-1])
        name_list.append(int (l[:-1]))

    avg_TP = 0.0
    avg_FP = 0.0
    avg_TN = 0.0
    avg_FN = 0.0
    avg_precision = 0.0
    avg_recall = 0.0
    avg_accuracy = 0.0

    for n in name_list:

        solver = GraphSolver ()
        solver.load_graph('./generate_data/AL_subgraph_edges_' + str(n) + '.csv')

        pos, labels = solver.G.save_graph(file_name = str(n)+'before')
        solver.encode()

        # result = solver.compare_names("http://ru.dbpedia.org/resource/Обама,_Барак", "http://ru.dbpedia.org/resource/%D0%9E%D0%B1%D0%B0%D0%BC%D0%B0,_%D0%91%D0%B0%D1%80%D0%B0%D0%BA")
        # print ('TEST: ', result)


        print ('now solve')
        solver.solve()
        print ('now decode')
        solver.decode()
        solver.H.save_graph(file_name = str(n) + 'after',  pos=pos, labels = labels)
        # also obtain obtain statistics
        solver.obtain_statistics('./generate_data/' + str(n) + '_annotation.txt')

        avg_TP += solver.count_TP
        avg_TN += solver.count_TN
        avg_FN += solver.count_FN
        avg_FP += solver.count_FP
        avg_precision += solver.precision
        avg_recall += solver.recall
        avg_accuracy += solver.accuracy
    # ===============
    avg_TP /= len(name_list)
    avg_TN /= len(name_list)
    avg_FN /= len(name_list)
    avg_FP /= len(name_list)
    avg_precision /= len(name_list)
    avg_recall /= len(name_list)
    avg_accuracy /= len(name_list)

    print('=========FINALLY==========')
    print('average precision: ', avg_precision)
    print('average recall: ', avg_recall)
    print('average accuracy: ', avg_accuracy)

    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
