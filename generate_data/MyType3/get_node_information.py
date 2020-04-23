# this file gets information from HDT about the labels and comments of the node_size

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
from hdt import HDTDocument, IdentifierPosition


names = ['SA2_4', 'SA4_0', 'SA5_19','SA5_18', 'SA6_2', 'SA6_19', 'SA7_3', 'SA8_6', 'SA8_11', 'SA8_15', 'SA8_17','SA9_11','SA9_18', 'SA9_19']

PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
hdt_file = HDTDocument(PATH_LOD)

rdfs_subClassOf = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
rdfs_lable = "http://www.w3.org/2000/01/rdf-schema#label"
rdfs_comment = "http://www.w3.org/2000/01/rdf-schema#comment"
owl_sameas = "http://www.w3.org/2002/07/owl#sameAs"
for nm in names:
    print(nm)
    # open the file and generate a graph
    g = nx.Graph()
    file_name = nm + '_nodes.csv'
    file = open(file_name, 'r')
    reader = csv.DictReader(file, delimiter = ',')
    entity_list = []
    for row in reader:
        e = row["Entity"]
        entity_list.append(e)
    print ('size of nodes: ', len(entity_list))
    for e in entity_list:
        export_filename = nm + '_node_information.txt'
        with open(export_filename, 'w') as f:
            f.write ('\n\nNow dealing with: ' + e)
            # use HDT and print essential information
            try:
                (triples, cardinality) = hdt_file.search_triples(e, rdfs_subClassOf, "")
                for (_, _, sup) in triples:
                    f.write ('\tSUBCLASSOF: '+ sup)
            except:
                print('error in subclass')


            try:
                (triples, cardinality) = hdt_file.search_triples(e, rdfs_lable, "")
                for (_, _, sup) in triples:
                    f.write ('\tLABEL: ' + sup)
            except:
                print('error in label')


            try:
                (triples, cardinality) = hdt_file.search_triples(e, rdfs_comment, "")
                for (_, _, sup) in triples:
                    f.write ('\tCOMMENT: ' + sup)
            except:
                print('error in comment')

            try:
                (triples, cardinality) = hdt_file.search_triples(e, owl_sameas, "")
                for (_, _, sup) in triples:
                    f.write ('\tSAMEAS->: ' + sup)
            except :
                print('error in sameas >')

            try:
                (triples, cardinality) = hdt_file.search_triples('', owl_sameas, e)
                for (sub, _, _) in triples:
                    f.write ('\tSAMEAS<-: ' + sub)
            except :
                print('error in sameas <')
