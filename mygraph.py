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

    def load_graph(self, file_name):
        g = nx.Graph()
        eq_file = open(file_name, 'r')
        reader = csv.DictReader(eq_file)
        for row in reader:
            s = row["SUBJECT"]
            o = row["OBJECT"]
            g.add_edge(s, o)
        self.subgraphs[0] = g
        self.groups +=1

    def save_graph(self, file_name, pos = None, labels = None):
        if pos == None and self.groups == 1: # export as the input graph OR there is only one graph in the end
            pos = nx.spring_layout(self.subgraphs[0])


        # Big = nx.Graph()
        for k in self.subgraphs.keys():
            print ('======= GROUP ', k, ' =========')
            g = self.subgraphs[k]
            # Big = nx.compose(Big, g)
            nx.draw_networkx_nodes(g, pos,
                                   nodelist = g.nodes,
                                   node_color = colors[k],
                                   node_size=5,
                               alpha=0.8)
            nx.draw_networkx_edges(g, pos,
                                   edgelist=g.edges,
                                   width=2,alpha=0.5,edge_color=colors[k])

            if labels == None:
                labels={}
                ind = 0
                for n in g.nodes:
                    labels[n] =  str(ind)
                    print ('index ', ind, ' = ', n)
                    ind += 1
            else:
                for n in g.nodes:
                    print ('index ', labels[n], ' = ', n)
            nx.draw_networkx_labels(g,pos,labels,font_size=10)
            print ('\n')

        # nx.draw_networkx_edges(Big, pos,
        #            edgelist=self.edges_between,
        #            width=2,alpha=0.5,edge_color='g')

        plt.savefig(file_name)
        plt.close()
        print ('saved to: ', file_name)

        return pos,labels


if __name__ == "__main__":
    n = MyGraph()
    n.load_graph('./generate_data/V10_24.csv')
    n.save_graph(file_name = 'test.png')
