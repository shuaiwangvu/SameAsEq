# this file extrats the SA2_4.csv from edges to nodes
# this file also extract the edges , and assert the default label 'k': to keep

import networkx as nx
import matplotlib.pyplot as plt
import random
import itertools
from operator import itemgetter
from z3 import *
import tldextract
# from mygraph import MyGraph
import urllib.parse
import datetime
import pickle
import time
import csv



names = ['SA2_4', 'SA4_0', 'SA5_19','SA5_18', 'SA6_2', 'SA6_19', 'SA7_3', 'SA8_6', 'SA8_11', 'SA8_15', 'SA8_17','SA9_11','SA9_18', 'SA9_19']

# for nm in names:
    # open the file and generate a graph

    # g = nx.Graph()
    # file_name = nm + '.csv'
    # file = open(file_name, 'r')
    # reader = csv.DictReader(file, delimiter = ',')
    # for row in reader:
    #     s = row["SUBJECT"]
    #     o = row["OBJECT"]
    #     g.add_edge(s, o)
    #
    # # export to the local file
    # file_name = nm + '_nodes.csv'
    # file =  open(file_name, 'w', newline='')
    # writer = csv.writer(file)
    # # for n in g.nodes:
    # writer.writerow(["Entity"])
    # for n in g.nodes:
    #     writer.writerow([n])

# below is about getting edges & labels ready
for nm in names:
    g = nx.Graph()
    file_name = nm + '.csv'
    edges_file_name = nm + '_edges.csv'
    labelled_edges_file_name = nm + '_edges_labelled.csv'

    file = open (file_name, 'r')
    file_e = open(edges_file_name, 'w+')
    file_le = open(labelled_edges_file_name, 'w+')

    reader = csv.DictReader(file, delimiter = ',')
    writer_e = csv.writer(file_e)
    writer_e.writerow(["SUBJECT","OBJECT"])
    writer_le = csv.writer(file_le)
    writer_le.writerow(["SUBJECT","OBJECT","LABEL"])
    for row in reader:
        s = row["SUBJECT"]
        o = row["OBJECT"]
        g.add_edge(s, o)
        writer_e.writerow([s,o])
        writer_le.writerow([s,o,'k'])
