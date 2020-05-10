# Shuai Wang
# VU Amsterdam
import networkx as nx
import matplotlib.pyplot as plt
import random
import itertools
from operator import itemgetter
import csv

from random import randint
colors = []
n = 300
for i in range(n):
    colors.append('#%06X' % randint(0, 0xFFFFFF))


class MyGraph ():
    def __init__(self):
        self.subgraphs = {}
        self.groups = 0
        # self.edges_between = []
        self.error_degree = {}
        self.term_to_class = {}
        self.edge_label = {}
        self.should_remove = []
        self.node_label = {}

    def load_graph(self, file_name):
        g = nx.Graph()
        eq_file = open(file_name, 'r')
        reader = csv.DictReader(eq_file)
        for row in reader:
            s = row["SUBJECT"]
            o = row["OBJECT"]
            # l = row ["LABEL"]
            if s != o:
                g.add_edge(s, o)
                # self.edge_label[(s,o)] = l
            # if l == 'x':
            #     self.should_remove.append((s,o))
        print ('before = ',len(g.edges))
        print ('after = ', len(g.to_undirected().edges))

        self.subgraphs[0] = g.to_undirected()
        self.groups +=1
    #
    # def load_graph_with_error_degree(self, file_error_degree, file_term_to_class):
    #     g = nx.Graph()
    #     eq_file = open(file_error_degree, 'r')
    #     reader = csv.DictReader(eq_file, delimiter=";")
    #     for row in reader:
    #         s = row["term1"]
    #         o = row["term2"]
    #         error = row["error_degree"]
    #         self.error_degree[(s,o)] = error
    #         g.add_edge(s, o)
    #     self.subgraphs[0] = g
    #     self.groups +=1
    #
    #     t2c_file = open(file_term_to_class, 'r')
    #     reader = csv.DictReader(t2c_file, delimiter=";")
    #     for row in reader:
    #         t = row["Term"]
    #         c = row["Class"]
    #         self.term_to_class [t] = c



    def load_node_manual_label (self, file_name):
        file = open(file_name, 'r')
        reader = csv.DictReader(file)
        for row in reader:
            e = row["Entity"]
            l = row ["Label"]
            self.node_label[e] = l


# https://stackoverflow.com/questions/3567018/how-can-i-specify-an-exact-output-size-for-my-networkx-graph
    def save_graph(self, file_name, pos = None, labels = None, attacking_edges = []):
        if pos == None and self.groups == 1: # export as the input graph OR there is only one graph in the end
            pos = nx.spring_layout(self.subgraphs[0])


        Big = nx.Graph()
        for k in self.subgraphs.keys():
            # print ('======= GROUP ', k, ' =========')
            g = self.subgraphs[k]
            Big = nx.compose(Big, g)
            nx.draw_networkx_nodes(g, pos,
                                   nodelist = g.nodes,
                                   node_color = colors[k],
                                   node_size=5,
                               alpha=0.8)
            nx.draw_networkx_edges(g, pos,
                                   edgelist=g.edges,
                                   width=1,alpha=0.5,edge_color=colors[k])

            if labels == None:
                labels={}
                ind = 0
                for n in g.nodes:
                    labels[n] =  str(ind)
                    # print ('index ', ind, ' = ', n)
                    ind += 1
            else:
                pass
                # for n in g.nodes:
                    # print ('index ', labels[n], ' = ', n)
                    # print ('')
            nx.draw_networkx_labels(g,pos,labels,font_size=5)
            # print ('\n')

        nx.draw_networkx_edges(Big, pos,
                   edgelist=attacking_edges,
                   width=1,alpha=0.3,edge_color='r')

        plt.savefig(file_name+'.png')
        plt.savefig(file_name+'.svg')
        plt.close()
        print ('saved to: ', file_name)

        return pos,labels

#
# if __name__ == "__main__":
#     n = MyGraph()
#     n.load_graph('./generate_data/V10_24.csv')
#     n.save_graph(file_name = 'test')
