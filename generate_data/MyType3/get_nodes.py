# this file extrats the SA2_4.csv from edges to nodes
# it doesn't do anything more than that.

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

for nm in names:
    # open the file and generate a graph

    g = nx.Graph()
    file_name = nm + '.csv'
    file = open(file_name, 'r')
    reader = csv.DictReader(file, delimiter = ',')
    for row in reader:
        s = row["SUBJECT"]
        o = row["OBJECT"]
        g.add_edge(s, o)

    # export to the local file
    file_name = nm + '_nodes.csv'
    file =  open(file_name, 'w', newline='')
    writer = csv.writer(file)
    # for n in g.nodes:
    writer.writerow(["Entity"])
    for n in g.nodes:
        writer.writerow([n])
