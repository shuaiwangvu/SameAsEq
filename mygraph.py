# generate some groups and visualise them
import networkx as nx
import matplotlib.pyplot as plt
import random
import itertools
from operator import itemgetter
from z3 import *

class MyGraph():
    # parameters

    def __init__(self, concepts_size = 5, N =100, M = 5, alpha = 1.5, beta = 1.0):

        self.G = nx.Graph()
        self.subgraphs = {}
        self.subgraphs_representative = {}

        #part 1
        self.concepts_size = concepts_size
        self.N = N
        self.M = M
        self.alpha = alpha
        self.beta = beta

        #part 2
        self.edges_between = []

    def update_para(self, concepts_size, N, M, alpha, beta):
        self.N = N
        self.M = M
        self.alpha = alpha
        self.beta = beta
        self.G = None

    def create_BA_graph(self, n, m):
        # Create a BA model graph
        # n = 1000
        # m = 4
        G = nx.generators.barabasi_albert_graph(n, m)

        # find node with largest degree
        node_and_degree = G.degree()
        (largest_hub, degree) = sorted(node_and_degree, key=itemgetter(1))[-1]

        # Create ego graph of main hub
        hub_ego = nx.ego_graph(G, largest_hub)

        return hub_ego, largest_hub

    def update_graph_index (self, g, update_index):

        mapping = {}
        for i in g.nodes:
            j = i + update_index
            mapping[i] = j
        updated = nx.relabel_nodes(g,mapping)

        return updated

    def create_graph (self):
        nodes_shift_index = 0 # track index
        print ('there are ', self.concepts_size, ' subgraphs')
        # update its indeces
        for i in range (self.concepts_size):
            # print ('the edge index is now', nodes_shift_index)
            n = int (random.betavariate(2, 2) * self.N) + 1
            m = int (random.betavariate(2, 2) * self.M) + 1
            if (m > n):
                n = m + 1
            original, representative = self.create_BA_graph(n, m)
            # print ('created a subgraph with', len(original.nodes), ' nodes')
            # print (i, 'original: ',original.nodes)
            # print (i, 'original: ',original.edges)

            updated = self.update_graph_index(original, nodes_shift_index)
            # print (i, 'updated: ',updated.nodes)
            # print (i, 'updated: ',updated.edges)
            nodes_shift_index += max(updated.nodes) + 1

            self.G.update(nodes = updated.nodes, edges = updated.edges)
            # self.G.add_edges_from()

            self.subgraphs[i] = updated #
            self.subgraphs_representative [i] = representative
            # print ('G nodes = ', self.G.nodes)
            # print ('G edges = ', self.G.edges)
        print ('now there are ', len(self.subgraphs), 'subgraphs, we add the links in between')


        coll_edges_between = []

        BETA = int(self.beta * self.concepts_size) +1
        # create random links between the these subgraphs
        print ('BETA (pairs chosen) = ', BETA)
        chosen_pairs = []
        for r in range (BETA):
            [a, b] = random.sample(list(range(self.concepts_size)), 2) # randomly chose two
            while (a, b) in chosen_pairs:
                [a, b] = random.sample(list(range(self.concepts_size)), 2)
            chosen_pairs.append((a,b))
            ALPHA = int (random.betavariate(2, 5) * self.alpha * self.N) + 1
            print ('ALPHA (edges in between) = ', ALPHA)
            for i in range (ALPHA):
                # print ('chose a = ', a, ' and b =', b)
                # print('this subgraph has len nodes = ', len (self.subgraphs[a].nodes))
                # print('this subgraph has len nodes = ', len (self.subgraphs[b].nodes))
                l = random.choice(list(self.subgraphs[a].nodes()))
                r = random.choice(list(self.subgraphs[b].nodes()))
                coll_edges_between.append((l, r))

        self.G.add_edges_from(coll_edges_between)
        self.edges_between = coll_edges_between


    def save_graph(self, file_name, colors):
        # Draw graph
        tmpG = self.G.remove_edges_from(self.edges_between)
        pos = nx.spring_layout(self.G)
        self.G.add_edges_from(self.edges_between)

        for i in self.subgraphs.keys():
            g = self.subgraphs[i]
            nx.draw_networkx_nodes(self.G, pos,
                                   nodelist= g.nodes,
                                   node_color=colors[i], # TODO: subgraphs_representative
                                   node_size=5,
                               alpha=0.8)
            nx.draw_networkx_edges(self.G, pos,
                                   edgelist=g.edges,
                                   width=2,alpha=0.5,edge_color='b')


        nx.draw_networkx_edges(self.G, pos,
                               edgelist=self.edges_between,
                               width=2,alpha=0.5,edge_color='y')

        plt.savefig(file_name)
        plt.close()
        return pos


    def export_graph(self, file_name):
        # print ('pos = ', pos)

        pos = nx.spring_layout(self.G)
        nx.draw_networkx_nodes(self.G, pos,
                               nodelist = self.G.nodes,
                               node_color='b', # TODO: subgraphs_representative
                               node_size=5,
                           alpha=0.8)
        nx.draw_networkx_edges(self.G, pos,
                               edgelist=self.G.edges,
                               width=2,alpha=0.5,edge_color='y')

        plt.savefig(file_name)
        plt.close()
        print ('saved to: ', file_name)

        return pos


    def find_group(self, n):
        for i in range (self.concepts_size):
            if n in self.subgraphs[i].nodes():
                return i
        return 'not in graph'

    def test_same_groups(self, a, b):
        return (self.find_group(a) == self.find_group(b))

    def test_between_groups(self, a, b):
        return not (self.test_same_groups(a, b))


class GraphSolver():

    def __init__(self, myG, ratio_additional_edges):
        self.G = myG.G
        self.Gsubgraphs = myG.subgraphs
        self.Gsubgraphs_representative = myG.subgraphs_representative

        self.Gedges_between = myG.edges_between

        self.Hedges_between = []

        self.H = nx.Graph()
        self.Hsubgraphs = {}

        self.ratio_additional_edges = ratio_additional_edges
        self.test_between_groups = myG.test_between_groups
        self.test_same_groups = myG.test_same_groups

        self.count_TN = 0.0
        self.count_FN = 0.0
        self.count_FP = 0.0
        self.count_TP = 0.0

        self.precision = 0.0
        self.recall = 0.0
        self.accuracy = 0.0

        self.o = Optimize()
        self.m = None # model
        self.id2encode = {}

    def compute_weight(self, l, r):
        if self.test_between_groups(l, r):
            weight = random.choice([-2, -4, -6, 2, 1])
        else:
            weight = random.choice([-2, 2, 6, 8, 10])
        return weight

    def solve(self):
        # encode each node with an integer
        for n in self.G.nodes:
            self.id2encode[n] = Int(str(n))
            # o.add(id2encode[n] < 10)
            self.o.add(self.id2encode[n] >= 0) # we fix all values to non-negative values

        for e in self.G.edges:
            (l, r) = e
            w = self.compute_weight(l, r)
            self.o.add_soft(self.id2encode[l] == self.id2encode[r], w) # each edge within graphs
        # add the edges between groups, with negative weights
        i = 0
        while i < int(self.ratio_additional_edges * len(self.Gedges_between)):
            i1 = random.choice(list(self.G.nodes))
            i2 = random.choice(list(self.G.nodes))
            if (i1 != i2):
                w = self.compute_weight(i1, i2)
                self.o.add_soft(self.id2encode[i1] == self.id2encode[i2], w)
                i += 1

        result = self.o.check()
        print(result)
        self.m = self.o.model()


    def obtain_statistics_and_graph(self):
        self.H.add_nodes_from(self.G.nodes)
        for e in self.G.edges:
            (id1, id2) = e
            decision = self.m.evaluate(self.id2encode[id1] == self.id2encode[id2])
            if decision:
                # print ('the ids: ',id1, id2)
                self.H.add_edge(id1, id2)

            if self.test_same_groups(id1, id2)== True and decision == True:
                # in the same group and decision to be True
                self.count_TN += 1
            elif self.test_same_groups(id1, id2) == False and decision == True:
                self.count_FN += 1
            elif self.test_same_groups(id1, id2) == False and decision == False:
                self.count_TP += 1
            else:
                self.count_FP +=1


        for i in self.Gsubgraphs.keys():
            self.Hsubgraphs[i] = nx.Graph()
            g = self.Gsubgraphs[i]
            for e in g.edges:
                (id1, id2) = e
                decision = self.m.evaluate(self.id2encode[id1] == self.id2encode[id2])
                if decision:
                    self.Hsubgraphs[i].add_edge(id1, id2)
                #else, add it to a faulty edge set?
        for e in self.Gedges_between:
            (id1, id2) = e
            decision = self.m.evaluate(self.id2encode[id1] == self.id2encode[id2])
            if decision:
                self.Hedges_between.append(e)

        # remove z3 model and solver to free the memory?

        print ('G: THE EDGES BETWEEN: ', len (self.Gedges_between))
        print ('H: THE EDGES BETWEEN: ', len (self.Hedges_between))


        print ('total edges', len(self.G.edges))

        print ('TP = both remove: ', self.count_TP)
        print ('TN = both keep:   ', self.count_TN)
        print ('FP = predicted to remove but SHOULD KEEP: ', self.count_FP)
        print ('FN = predicted to keep but SHOULD REMOVE: ', self.count_FN)
        # print ('There are in total ', count_1, ' Obama')
        if self.count_TP + self.count_FP  != 0:
            self.precision = self.count_TP / (self.count_TP + self.count_FP)
            print('precision = TP/(TP+FP) = ', self.precision)  #TP/TP + FP
        if self.count_TP + self.count_FN != 0:
            self.recall = self.count_TP / (self.count_TP + self.count_FN )
            print('recall  = TP / (FN+TP) = ', self.recall) # TP / ( FN +  TP)

        self.accuracy = (self.count_TN + self.count_TP) / len(self.G.edges)

    def save_graph(self, file_name, pos, colors):
        # print ('pos = ', pos)
        pps = nx.spring_layout(self.H)
        print ('saving it accoring to the position')
        for i in self.Hsubgraphs.keys():
            g = self.Hsubgraphs[i]
            nx.draw_networkx_nodes(self.H, pos,
                                   nodelist= g.nodes,
                                   node_color=colors[i], # TODO: subgraphs_representative
                                   node_size=5,
                               alpha=0.8)
            nx.draw_networkx_edges(self.H, pos,
                                   edgelist=g.edges,
                                   width=2,alpha=0.5,edge_color='b')


        nx.draw_networkx_edges(self.H, pos,
                               edgelist=self.Hedges_between,
                               width=2,alpha=0.5,edge_color='y')

        plt.savefig(file_name)
        plt.close()
        return pos


        # for i in self.subgraphs.keys():
        #     g = self.subgraphs[i]
        #     nx.draw_networkx_nodes(self.G, pos,
        #                            nodelist= g.nodes,
        #                            node_color=colors[i], # TODO: subgraphs_representative
        #                            node_size=5,
        #                        alpha=0.8)
        #     nx.draw_networkx_edges(self.G, pos,
        #                            edgelist=g.edges,
        #                            width=2,alpha=0.5,edge_color='b')
        #
        #
        # nx.draw_networkx_edges(self.G, pos,
        #                        edgelist=self.edges_between,
        #                        width=2,alpha=0.5,edge_color='y')
        #
        # plt.savefig(file_name)

# g = MyGraph(concepts_size = 15, N =100, M = 5, alpha = 0.05, beta = 3)
# g.create_graph()
# # g.show_graph()
#
# ratio_additional_edges = 6060
# s = GraphSolver(g, ratio_additional_edges)
# s.solve()
# s.obtain_statistics_and_graph()
# s.print_info()




#
# # encode to z3
# from z3 import *
# o = Optimize()
#
# # plot H
# color = ['r', 'g', 'b','c', 'm', 'y']
# pos=nx.spring_layout(H)
# coll_edges_ploted = []
# for i in range(len(dict.keys())):
#     g = list(dict.keys())[i]
#     nx.draw_networkx_nodes(H,pos,
#                            nodelist=dict[g],
#                            node_color=color[i],
#                            node_size=5,
#                        alpha=0.8)
#     #obtain a subgraph between these nodes
#     subH = nx.subgraph(H,dict[g])
#     nx.draw_networkx_edges(H,pos,
#                            edgelist=subH.edges(),
#                            width=2,alpha=0.5,edge_color=color[i])
#
#     coll_edges_ploted += subH.edges()
#
# for e in H.edges:
#     if e not in coll_edges_ploted:
#         nx.draw_networkx_edges(H,pos,
#                                edgelist=subH.edges(),
#                                width=2,alpha=0.5,edge_color='y')
#
# print ('into %d groups: ',len (dict.keys()))
# plt.show()
