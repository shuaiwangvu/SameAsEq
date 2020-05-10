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

WEIGHT_EXISTING_ATTACKING_EDGES = 50
WEIGHT_EXISTING_EQUIVALENT_EDGES = 50
WEIGHT_ADDITIONAL_ATTACKING_EDGES = -4
WEIGHT_NORMAL_EDGES = 150
WEIGHT_WEAKER_NORMAL_EDGES = 94


import glob
l_names = glob.glob("*.csv")

# creat a struct such that :
# index -> file_name
#       -> num_nodes
#       -> num_edges
#       -> other statistics

class LargeGraph():
    def __init__(self, index, file_name, num_nodes, num_edges):
        self.index = index
        self.file_name = file_name
        self.num_nodes = num_nodes # reconsider
        self.num_edges = num_edges # reconsider

lg1000 = []

for l in l_names:
    [index, num_nodes, num_edges] = l[3:-4].split('_')
    # print (index, num_nodes, num_edges)
    lg1000.append ( LargeGraph(int(index), l, int(num_nodes), int(num_edges)))



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
        self.SMTvalue = 0.0

        self.o = Optimize()
        timeout = 1000 * 60 * 5 # one minute
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

    def same_domain (self, t1, t2):
        t1_domain = tldextract.extract(t1).domain
        # t1_subdomain = tldextract.extract(t1).subdomain
        t2_domain = tldextract.extract(t2).domain
        # t2_subdomain = tldextract.extract(t2).subdomain
        if t1_domain == t2_domain:
            return True
        else:
            return False

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
        for e in self.existing_attacking_edges:
            print ('existing_attacking_edges: ', e)

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

    def load_node_manual_label (self, file_name):
        self.G.load_node_manual_label(file_name)

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
            # self.o.add(self.id2encode[id] < max_size) # we fix all values to non-negative values
            id += 1
        # First, do a preprocessing before choosing nodes
        self.preprocessing_before_encode()

        # find existing attacking edges: #TODO change the weight function
        print ('There are in total ', len (self.G.subgraphs[0].edges))
        edges = list(g.edges).copy()
        self.find_existing_attacking_edges()
        for (t1, t2) in self.existing_attacking_edges:
            self.o.add(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]]) # WEIGHT_EXISTING_ATTACKING_EDGES)
            # self.o.add_soft(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]], WEIGHT_EXISTING_ATTACKING_EDGES)
            # print('existing attacking edge: ', t1, t2)
        print('\tThere are in total: ', len (self.existing_attacking_edges), ' existing attacking edges!')
        for (t1, t2) in self.existing_equivalent_edges:
            self.o.add(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]]) #,  WEIGHT_EXISTING_EQUIVALENT_EDGES)
            # self.o.add_soft(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]],  WEIGHT_EXISTING_EQUIVALENT_EDGES)
            # print('existing equivalent edge: ', t1, t2)
        print('\tThere are in total: ', len (self.existing_equivalent_edges), ' existing equivalence edges!')

        edges = list(filter(lambda x: x not in self.existing_attacking_edges, edges))
        edges = list(filter(lambda x: x not in self.existing_equivalent_edges, edges))
        print ('Now there are normal', len(edges), ' edges left')
        # other normal edges
        for (t1, t2) in edges:
            # if t1 and t2 has different domain, then they have a lower weight
            if self.same_domain(t1, t2):
                # self.o.add_soft(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]], WEIGHT_NORMAL_EDGES) # each edge within graphs
                self.o.add(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]]) #, WEIGHT_NORMAL_EDGES) # each edge within graphs
            else:
                self.o.add_soft(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]], WEIGHT_WEAKER_NORMAL_EDGES) # each edge within graphs

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
        # update the SMT value
        self.calculate_SMTvalue()

    def calculate_SMTvalue (self):

        SMT_value = 0.0
        g = self.G.subgraphs[0]
        # find existing attacking edges: #TODO change the weight function
        # print ('There are in total ', len (self.G.subgraphs[0].edges))
        # edges = list(g.edges).copy()
        # self.find_existing_attacking_edges()
        for (t1, t2) in self.existing_attacking_edges:
            if self.model.evaluate(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]]):
                SMT_value += WEIGHT_EXISTING_ATTACKING_EDGES
            # print('existing attacking edge: ', t1, t2)
        # print('\tThere are in total: ', len (self.existing_attacking_edges), ' existing attacking edges!')
        for (t1, t2) in self.existing_equivalent_edges:
            if self.model.evaluate(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]]):
                SMT_value += WEIGHT_EXISTING_EQUIVALENT_EDGES
            # print('existing equivalent edge: ', t1, t2)
        # print('\tThere are in total: ', len (self.existing_equivalent_edges), ' existing equivalence edges!')
        edges = list(g.edges).copy()
        edges = list(filter(lambda x: x not in self.existing_attacking_edges, edges))
        edges = list(filter(lambda x: x not in self.existing_equivalent_edges, edges))
        # print ('Now there are normal', len(edges), ' edges left')
        # other normal edges
        for (t1, t2) in edges:
            if self.model.evaluate(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]]):
                SMT_value += WEIGHT_NORMAL_EDGES # each edge within graphs

        # find additional attacking edges:
        # self.find_additional_attacking_edges()
        for (t1, t2) in self.additional_attacking_edges:
            # self.o.add(Not(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]])) # each edge within graphs
            if self.model.evaluate(self.id2encode[self.term2id[t1]] == self.id2encode[self.term2id[t2]]):
                SMT_value += WEIGHT_ADDITIONAL_ATTACKING_EDGES # each edge within graphs
        # print('There are in total: ', len (self.additional_attacking_edges), ' additional attacking edges!')
        print ('SMT value is', SMT_value)
        self.SMTvalue = SMT_value

    def decode (self):
        g = self.G.subgraphs[0]
        group_size = 0
        for id in self.id2encode.keys():
            # print ('eva = ', self.model.evaluate(self.id2encode[id]).as_string())
            if group_size < int(self.model.evaluate(self.id2encode[id]).as_string()):
                group_size = int(self.model.evaluate(self.id2encode[id]).as_string())
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
    #
    # def obtain_statistics(self, file_name):
    #     # dict_al = {}
    #     #
    #     # print ('obtain statistics now!')
    #     # print ('compare against the manual decision from AL in the file ', file_name)
    #     # # now load the data in
    #     # # file_name = str(n) + '_annotation.txt'
    #     # print ('File Name = ', file_name)
    #     # file = open(file_name, 'r')
    #     # reader = csv.DictReader(file, delimiter = '\t')
    #     # for row in reader:
    #     #     e = row["Entity"]
    #     #     o = row["Annotation"]
    #     #     dict_al [e] = o
    #     #
    #     # # al_count_remain = 0
    #     # al_remain = []
    #     # # al_count_remove = 0
    #     # self.G.should_remove = []
    #     #
    #     # my_remain = list(filter(lambda v: v not in self.removed_edges, self.G.subgraphs[0].edges))
    #     # my_removed = self.removed_edges
    #     #
    #     # count_edges_involving_unknow = 0
    #     #
    #     # for (l, r) in self.G.subgraphs[0].edges:
    #     #     if dict_al[l] != 'Uncertain' and dict_al[r] != 'Uncertain': # Error
    #     #         if dict_al[l] == dict_al[r] :
    #     #             al_remain.append((l,r))
    #     #         else:
    #     #             # al_count_remove += 1
    #     #             self.G.should_remove.append((l,r))
    #     #
    #     # print ('# al removed: ', len(self.G.should_remove))
    #     # print ('# al remain: ', len(al_remain))
    #     #
    #     # print('# my removed:', len(my_removed))
    #     # print('# my remain:', len(my_remain))
    #     print ('#my removed edges:', len(self.removed_edges))
    #     for e in self.removed_edges:
    #         (l, r) = e
    #         f = (r, l)
    #         if e in self.G.should_remove or f in self.G.should_remove:
    #             print ('\t*removed edges: ', e)
    #         else:
    #             print ('\tremoved edges: ', e)
    #
    #
    #     print ('# SHOULD REMOVE: ',len(self.G.should_remove))
    #     for e in self.G.should_remove:
    #         (l, r) = e
    #         f = (r, l)
    #         if e in self.removed_edges or f in self.removed_edges:
    #             print ('\t*should remove edge: ', e)
    #         else:
    #             print ('\tshould remove edge: ', e)
    #
    #
    #     # collectFN = []
    #     # collectTP = []
    #     collect_visited_edges = []
    #     for e in self.G.subgraphs[0].edges:
    #         (l, r) = e
    #         f = (r, l)
    #         collect_visited_edges.append(e)
    #         if f in collect_visited_edges:
    #             print ('!!!!ERROR: ', f)
    #         if ((e not in self.removed_edges) and (f not in self.removed_edges))and ((e not in self.G.should_remove) and (f not in self.G.should_remove)):
    #             self.count_TN += 1
    #         elif ((e in self.removed_edges) or (f in self.removed_edges)) and ((e in self.G.should_remove) or (f in self.G.should_remove)):
    #             self.count_TP += 1
    #             # collectTP.append(e)
    #         elif ((e not in self.removed_edges) and (f not in self.removed_edges) )  and ((e in self.G.should_remove) or (f in self.G.should_remove)):
    #             self.count_FN += 1
    #             # collectFN.append(e)
    #         elif ((e in self.removed_edges) or (f in self.removed_edges)) and ((e not in self.G.should_remove) and (f not in self.G.should_remove)):
    #             self.count_FP += 1
    #         else:
    #             print ('ERROR : error', l, ' and ', r)
    #     print ('Total edges ', len(self.G.subgraphs[0].edges))
    #     # print ('There are in total ', count_edges_involving_unknow, ' edges involving unknown')
    #
    #     count_diff = 0
    #     for e in self.G.subgraphs[0].edges:
    #         (l,r) = e
    #         if self.G.node_label[l] != self.G.node_label[r]:
    #             count_diff += 1
    #             print('l = ', l, ': ', self.G.node_label[l])
    #             print('r = ', r, ': ', self.G.node_label[r])
    #     print ('VERIFY: COUNT_DIFF    = ', count_diff)
    #     print ('VERIFY: SHOULD_REMOVE = ', len(self.G.should_remove))
    #
    #     print ('==============================')
    #
    #     print ('TP = both remove: ', self.count_TP)
    #     print ('TN = both keep:   ', self.count_TN)
    #     print ('FP = predicted to remove but SHOULD KEEP: ', self.count_FP)
    #     print ('FN = predicted to keep but SHOULD REMOVE: ', self.count_FN)
    #     # print ('FN = ', collectFN)
    #     # print ('TP = ', collectTP)
    #     print ('==============================')
    #
    #     if self.count_TP + self.count_FP  != 0:
    #         self.precision = self.count_TP / (self.count_TP + self.count_FP)
    #         print('precision = TP/(TP+FP) = ', self.precision)  #TP/TP + FP
    #     if self.count_TP + self.count_FN != 0:
    #         self.recall = self.count_TP / (self.count_TP + self.count_FN )
    #         print('recall  = TP / (FN+TP) = ', self.recall) # TP / ( FN +  TP)
    #
    #     self.accuracy = (self.count_TN + self.count_TP) / (len(self.G.subgraphs[0].edges))
    #     print('accuracy = ', self.accuracy) #



if __name__ == "__main__":

    start = time.time()

    # name_list = ['4_0','5_19','6_2','8_6','8_11','9_11']
    # lg1000

    # f = open("process3.txt", "r")
    # for l in f:
    #     print ('Now working on group index', l[:-1])
    #     name_list.append(int (l[:-1]))

    avg_TP = 0.0
    avg_FP = 0.0
    avg_TN = 0.0
    avg_FN = 0.0
    avg_precision = 0.0
    avg_recall = 0.0
    avg_accuracy = 0.0
    avg_SMTvalue = 0.0
    SMTvalues = []
    count_too_big = 0
    for n in lg1000:
        if n.num_nodes >= 10000:
        #     count_too_big += 1
        #     print (n.index)
        # elif n.num_nodes > 4000 :
            print ('\n\n\n\n NOW WORKING ON: ', n.index)
            # filename_labelled_edges = './labelled/SA' + str(n) + '_edges_labelled.csv'
            # filename_labelled_nodes = './labelled/SA' + str(n) + '_nodes_labelled.csv'
            filename_edges = n.file_name
            print ('file is at: ', filename_edges)
            solver = GraphSolver ()
            solver.load_graph(filename_edges)
            # solver.load_node_manual_label(filename_labelled_nodes)

            pos, labels = solver.G.save_graph(file_name = str(n.index)+'before')
            # compute the size limit
            # max_size = int(len(solver.G.subgraphs[0].nodes)/300) + 5
            # print ("max_size = ", max_size)
            solver.encode()

            print ('now solve')
            solver.solve()
            print ('now decode')
            solver.decode()
            solver.H.save_graph(file_name = str(n.index) + 'after',  pos=pos, labels = labels)

        # also obtain obtain statistics
        # solver.obtain_statistics(filename_labelled_edges)

        # avg_TP += solver.count_TP
        # avg_TN += solver.count_TN
        # avg_FN += solver.count_FN
        # avg_FP += solver.count_FP
        # avg_precision += solver.precision
        # avg_recall += solver.recall
        # avg_accuracy += solver.accuracy
        # avg_SMTvalue += solver.SMTvalue
        # SMTvalues.append(solver.SMTvalue)
    # ===============
    # avg_TP /= len(name_list)
    # avg_TN /= len(name_list)
    # avg_FN /= len(name_list)
    # avg_FP /= len(name_list)
    # avg_precision /= len(name_list)
    # avg_recall /= len(name_list)
    # avg_accuracy /= len(name_list)
    # avg_SMTvalue /= len(name_list)
    # print('=========FINALLY==========')
    # print('average precision: ', avg_precision)
    # print('average recall: ', avg_recall)
    # print('average accuracy: ', avg_accuracy)
    # print('\n The average SMT values', SMTvalues)
    # print('\n Average SMTvalue:', avg_SMTvalue)
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("TOTAL Time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
    print('TOO BIG: ', count_too_big)
