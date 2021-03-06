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


# # read the file
# for i in range(40):
#     eq_file = open('V' + str(i) + '.csv', 'r')
#     reader = csv.reader(eq_file, delimiter=',')
#
#     index = 0
#     for row in reader:
#         # print (index, ' has length ', len (row))
#         row = [ r[1:-1] for r in row]
#         g = obtain_graph(row)
#         # export the graph
#         export_filename = 'V' + str(i) + '_' + str(index) + ".csv"
#         # nx.write_edgelist(g, export_filename)
#         export_graph_csv(export_filename, g)
#         index += 1
#
#         # h = nx.read_edgelist(export_filename)
#         h = read_graph_csv(export_filename)
#
#         # print ('G- No. Edges: ', len(g.edges))
#         # print ('H- No. Edges: ', len(h.edges))
#         if len(h.edges) != len(g.edges):
#             print ('********* error *************')
#
# print('now dealing with SA')
#
# # read the file
# for i in range(10):
#     eq_file = open('SA' + str(i) + '.csv', 'r')
#     reader = csv.reader(eq_file, delimiter=',')
#     print ('i = ', i)
#     index = 0
#     for row in reader:
#         print (index, ' has length ', len (row))
#         row = [ r[1:-1] for r in row]
#         g = obtain_graph(row)
#         # export the graph
#         export_filename = 'SA' + str(i) + '_' + str(index) + ".csv"
#         # nx.write_edgelist(g, export_filename)
#         export_graph_csv(export_filename, g)
#         index += 1
#
#         # h = nx.read_edgelist(export_filename)
#         h = read_graph_csv(export_filename)
#
#         # print ('G- No. Nodes: ', len(g.nodes))
#         # print ('G- No. Edges: ', len(g.edges))
#         # print ('H- No. Nodes: ', len(h.nodes))
#         # print ('H- No. Edges: ', len(h.edges))
#         if len(h.edges) != len(g.edges):
#             print ('********* error *************')



print('now dealing with SB')

# read the file
for i in range(10):
    eq_file = open('SA' + str(i) + '.csv', 'r')
    reader = csv.reader(eq_file, delimiter=',')
    print ('i = ', i)
    index = 0
    for row in reader:
        print (index, ' has length ', len (row))
        row = [ r[1:-1] for r in row]
        g = obtain_graph(row)
        # export the graph
        export_filename = 'SB' + str(i) + '_' + str(index) + ".csv"
        # nx.write_edgelist(g, export_filename)
        export_graph_csv(export_filename, g)
        index += 1

        # h = nx.read_edgelist(export_filename)
        h = read_graph_csv(export_filename)

        # print ('G- No. Nodes: ', len(g.nodes))
        # print ('G- No. Edges: ', len(g.edges))
        # print ('H- No. Nodes: ', len(h.nodes))
        # print ('H- No. Edges: ', len(h.edges))
        if len(h.edges) != len(g.edges):
            print ('********* error *************')
