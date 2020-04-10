# this file is about retrieving the corresponding groups of the mannually annotated
# groups by Al.

# data sent by Joe
import csv
import matplotlib.pyplot as plt
import numpy as np
import random
from hdt import HDTDocument, IdentifierPosition
import networkx as nx

sameas = "http://www.w3.org/2002/07/owl#sameAs"
PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
hdt_file = HDTDocument(PATH_LOD)

def export_graph_csv (file_name, graph):
    file =  open(file_name, 'w', newline='')
    writer = csv.writer(file)
    writer.writerow([ "SUBJECT", "OBJECT"])
    for (l, r) in graph.edges:
        writer.writerow([l, r])

def read_graph_csv(file_name):
    g = nx.Graph()
    eq_file = open(file_name, 'r')
    reader = csv.DictReader(eq_file)
    for row in reader:
        s = row["SUBJECT"]
        o = row["OBJECT"]
        g.add_edge(s, o)
    return g

def obtain_graph(list_terms):
    g = nx.Graph()
    # add these nodes in it
    g.add_nodes_from(list_terms)
    for n in list_terms:
        (triples, cardi) = hdt_file.search_triples(n, sameas, "")
        for (_,_,o) in triples:
            if o in list_terms:
                g.add_edge(n, o)
        (triples, cardi) = hdt_file.search_triples("", sameas, n)
        for (s,_,_) in triples:
            if s in list_terms:
                g.add_edge(s, n)
    return g




name_list = []

f = open("names.txt", "r")
for l in f:
    print ('Now working on group index', l[:-1])
    name_list.append(int (l[:-1]))
    # file_name = l[:-1] + '_annotation.txt'
    # print ('file name =', file_name)

print (name_list)


# go through the csv file and check if the group is in this name_list

path = './closure_all/id2terms_all.csv'
#
# with open(path) as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=' ')
#     # count = 0
#     for row in csv_reader:
#         index = int(row[0])
#         if index in name_list:
#             terms = []
#             for i in range (len (row)):
#                 if i > 0:
#                     # print (index, row[i])
#                     terms.append(row[i][1:-1])
#                     # export to csv file
#             print ('terms = ', terms)
#             g = obtain_graph( terms )
#             print (index, ' has number of edges is: ', len(g.edges))
#             export_filename = 'AL' + str(index) + ".csv"
#             export_graph_csv(export_filename, g)


for n in name_list:
    print ('AL name = ', n)
    terms = []
    file_name = str(n) + '_annotation.txt'
    print ('File Name = ', file_name)
    file = open(file_name, 'r')
    reader = csv.DictReader(file, delimiter = '\t')
    for row in reader:
        s = row["Entity"]
        # o = row["OBJECT"]
        terms.append(s)
    print ('Total amount of terms/nodes: ',len(terms))
    g = obtain_graph( terms )
    print (str(n), ' has number of nodes is: ', len(g.nodes))
    print (str(n), ' has number of edges is: ', len(g.edges))
    export_filename = 'AL_subgraph_edegs_' + str(index) + ".csv"
    export_graph_csv(export_filename, g)

    
