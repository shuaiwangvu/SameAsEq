import csv
import matplotlib.pyplot as plt
import numpy as np
import random
from hdt import HDTDocument, IdentifierPosition
import networkx as nx

sameas = "http://www.w3.org/2002/07/owl#sameAs"
PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
hdt = HDTDocument(PATH_LOD)



def obtain_graph(list_terms):
    g = nx.Graph()
    # add these nodes in it
    g.add_nodes_from(list_terms)
    for n in list_terms:
        (triples, cardi) = hdt.search_triples(n, "", "")
        # print (n, ' has cardi', cardi, ' as subject')
        for (_,p,o) in triples:
            # print ('p = ', p)
            # print ('o = ', o)
            if o in list_terms:
                g.add_edge(n, o)
        (triples, cardi) = hdt.search_triples("", "", n)
        # print (n, ' has cardi', cardi, ' as object')
        for (s,p,_) in triples:
            if s in list_terms:
                g.add_edge(s, n)
    return g


# read the file
eq_file = open('V23.csv', 'r')
reader = csv.reader(eq_file, delimiter=',')

index = 0
for row in reader:
    print (index, ' has length ', len (row))
    g = obtain_graph(row)
    print ('#nodes', len(g.nodes))
    print ('#edges', len(g.edges))
    # export the graph
    export_filename = str(index) + ".edgelist"
    nx.write_edgelist(g, export_filename)
    index += 1
