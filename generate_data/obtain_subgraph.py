import csv
import matplotlib.pyplot as plt
import numpy as np
import random
from hdt import HDTDocument, IdentifierPosition
import networkx as nx

sameas = "http://www.w3.org/2002/07/owl#equivalentClass"
PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
hdt = HDTDocument(PATH_LOD)


# read the file
eq_file = open('V12.csv', 'r')
reader = csv.reader(eq_file, delimiter=',')
index = 0
for row in reader:
    print (index, ' has length ', len (row))
    index +=1
    for t in row:
        print ('\t', t)


hdt.search_triples(s, p, o)
