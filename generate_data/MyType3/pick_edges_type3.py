# for all the files in the /generate_data/MyType3 directory, find those who has
# edges that are linking two clusters of obvious differnt concepts.
# the resulting data can be further processed as that of Type 2


# from mygraph import *
import networkx as nx
import matplotlib.pyplot as plt
import random
import itertools
from operator import itemgetter
# from z3 import *
import tldextract
# from mygraph import MyGraph
import urllib.parse
import datetime
import pickle
import time
import csv
import random
from random import randint

IDENTICAL = 0
CONV_IDENTICAL = 0
DIFFERENT = 1

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

    def load_graph_with_error_degree(self, file_error_degree, file_term_to_class):
        g = nx.Graph()
        eq_file = open(file_error_degree, 'r')
        reader = csv.DictReader(eq_file, delimiter=";")
        for row in reader:
            s = row["term1"]
            o = row["term2"]
            error = row["error_degree"]
            self.error_degree[(s,o)] = error
            g.add_edge(s, o)
        self.subgraphs[0] = g
        self.groups +=1

        t2c_file = open(file_term_to_class, 'r')
        reader = csv.DictReader(t2c_file, delimiter=";")
        for row in reader:
            t = row["Term"]
            c = row["Class"]
            self.term_to_class [t] = c


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
                    print ('index ', ind, ' = ', n)
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


def compare_names (t1, t2):
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

def find_label (dict, term):
    names = dict.keys()
    for n in names:
        if compare_names(n, term) != DIFFERENT:
            return dict[n]
    else:
        return '?'


if __name__ == "__main__":
    n = MyGraph()
    n.load_graph('./SA9_11_edges.csv')
    g = n.subgraphs[0]
    # n.save_graph(file_name = 'SA2_4')
    # N = 2 # related to pokemon or the person
    # collect_person_nodes = []
    # for e in g.edges:
    #     (l, r) = e
    #     if l == 'http://rdf.freebase.com/ns/m.07f_3m':
    #         print ('right  = ', r)
    #     if r == 'http://rdf.freebase.com/ns/m.07f_3m':
    #         print ('left  = ', l)
    #
    # NOW Export the nodes
    # file_name = './generate_data/MYType3/SA4_0_nodes.csv'
    # file =  open(file_name, 'w', newline='')
    # writer = csv.writer(file)
    # writer.writerow(['Node','Label'])
    # for n in g.nodes:
    #     writer.writerow([n, '?'])

    # read the file and see what the potential edges errornous edges are about
    file_name = open('./SA9_11_nodes_labelled.csv', 'r')
    reader = csv.DictReader(file_name)
    label_dict = {}
    for row in reader:
        n = row["Entity"]
        l = row["Label"]
        label_dict[n] = l

    file_name.close()



    # find the labels for the rest of the entities with messed up URIs
    file_name = './SA9_11_nodes_labelled_auto.csv'
    file =  open(file_name, 'w+')
    writer = csv.writer(file)
    writer.writerow(["Entity", "Label"])
    names = label_dict.keys()
    print ('size = ', len(names))
    for n in label_dict.keys():
        if label_dict[n] == None or label_dict[n] == '?':
            # print (n, label_dict[n])
            l = find_label(label_dict, n)
            if l != None and l != '?':
                # print ('FOUND:', n,',', l)
                writer.writerow([n, l])
            elif l == None:
                # pass
                print ('TODO: ', n)
            else:
                print ('WTF:', n)
                writer.writerow([n, label_dict[n]])
        else:
            writer.writerow([n, label_dict[n]])


    count = 0
    for e in g.edges:
        (l, r) = e
        if label_dict[l] != label_dict[r] and label_dict[l] != '?'  and label_dict[r] != '?':
            print ('REMOVE: l (', label_dict[l], ') = ', l)
            print ('REMOVE: r (', label_dict[r], ') = ', r, '\n')
            count += 1
        if label_dict[l] == '?'  or label_dict[r] == '?':
            print ('?= l (', label_dict[l], ') = ', l)
            print ('?= r (', label_dict[r], ') = ', r, '\n')
    print ('count = ', count)


    #
    #

    # now export the decisions:
    #
    file_name = './SA9_11_edges_labelled.csv'
    file =  open(file_name, 'w+')
    writer = csv.writer(file)
    writer.writerow(["SUBJECT","OBJECT","LABEL"]) #SUBJECT,OBJECT,LABEL
    count = 0
    for e in g.edges:
        (l, r) = e
        if label_dict[l] != label_dict[r] and label_dict[l] != '?'  and label_dict[r]!= '?':
            print ('l (', label_dict[l], ') = ', l)
            print ('r (', label_dict[r], ') = ', r, '\n')
            count += 1
            writer.writerow([l, r, 'x'])
        elif label_dict[l] == '?'  or label_dict[r] == '?':
            print ('?= l (', label_dict[l], ') = ', l)
            print ('?= r (', label_dict[r], ') = ', r, '\n')
            writer.writerow([l, r, 'x'])
        else :
            writer.writerow([l, r, 'k']) # maintain this row if no conflict
    print ('count = ', count, ' edges removed')

    # collect all the edges that involve :http://yi.dbpedia.org/resource/בראנדנבורג
    #
    # for e in g.edges:
    #     (l,r) = e
    #     if r == "http://yi.dbpedia.org/resource/בראנדנבורג" and label_dict[r] == label_dict[l]:
    #         print ('SAME l (', label_dict[l], ') = ', l)
    #         print ('SAME r (', label_dict[r], ') = ', r, '\n')
    #
    # for e in g.edges:
    #     (l,r) = e
    #     if l == "http://yi.dbpedia.org/resource/בראנדנבורג" and label_dict[r] == label_dict[l]:
    #         print ('SAME l (', label_dict[l], ') = ', l)
    #         print ('SAME r (', label_dict[r], ') = ', r, '\n')
    #
    #
    #

    # collect_u = []
    # collect_m = []
    # collect_x = []
    #
    # for n in g.nodes:
    #     print (n, flush=True)
    #     c = input()
    #     if c == 'u':
    #         collect_u.append(n)
    #     elif c == 'm' :
    #         collect_m.append(n)
    #     elif c == 'x':
    #         collect_x.append(n)
    #     elif c == 'n':
    #         collect_x.append(n)
    #
    # print (n)
    # for e in g.edges:
    #     (l, r) = e
    #     if (l in collect_u and r not in collect_u) or (l not in collect_u and r in collect_u):
    #         print ('this may be a wrong edge for u: ', e)
    #     if (l in collect_m and r not in collect_m) or (l not in collect_m and r in collect_m):
    #         print ('this may be a wrong edge for m: ', e)
    #     if (l in collect_x and r not in collect_x) or (l not in collect_x and r in collect_x):
    #         print ('this may be a wrong edge for x: ', e)
    #     if (l in collect_n and r not in collect_n) or (l not in collect_n and r in collect_n):
    #         print ('this may be a wrong edge for n: ', e)
    #
    #
