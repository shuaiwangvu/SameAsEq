#test sameAs data
# read and analysis the data
import csv
import matplotlib.pyplot as plt
import numpy as np
import random
import networkx as nx
from hdt import HDTDocument, IdentifierPosition

sameas = "http://www.w3.org/2002/07/owl#sameAs"
PATH_LOD = "/scratch/wbeek/data/LOD-a-lot/data.hdt"
hdt_file = HDTDocument(PATH_LOD)

sameAs_dic = {}
# def read_line (line):
#     # read this line
#
#     return index
#
#
# with open('/Users/sw-works/Documents/backbone/sameAs_data/id2terms_0-99.csv', 'r') as thecsv:
#     count = 0
#     for line in thecsv:
#         index, term_list = read_line(line)
#         print ('index = ', index, ' terms = ', term_list)
#         count += 1
#         if count > 500:
#             break


# path = '/Users/sw-works/Documents/backbone/sameAs_data/id2terms_0-99.csv'
path = './closure_all/id2terms_all.csv'





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


#
# with open(path) as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=' ')
#     count = 0
#     for row in csv_reader:
#         index = int(row[0])
#         terms = []
#         for i in range (len (row)):
#             if i > 0:
#                 # print (index, row[i])
#                 terms.append(row[i])
#         sameAs_dic[index] = terms
#         # print ('\n')
#         count += 1
#         if count % 100000 == 0:
#             print (count)
#
# max = 0
# for k in sameAs_dic.keys():
#     l = len (sameAs_dic[k])
#     if l > max:
#         max = l
#
# print('max = ', max)

# # step 1:
# sample_size = 100
# # Generate the VM group
# # sameAs_dic
# for V in range (40): # 0 - 199, 40 groups
#     collect_data_VM = []
#     for k in sameAs_dic.keys():
#         terms = sameAs_dic[k] # k = group_id
#         VM_id = int(len(terms) / 5) # an VM id
#         if VM_id == V:
#             collect_data_VM.append((k,sameAs_dic[k]))
#     # select 100 randomly from them # size
#     Vsample = random.sample(collect_data_VM, sample_size)
#     # export these 100 to a file
#     file_name = 'V' + str(V) + '.csv'
#     file =  open(file_name, 'w', newline='')
#     writer = csv.writer(file)
#     # writer.writerow([ "GROUP_ID", "TERMS"])
#     for (k, terms) in Vsample:
#         writer.writerow(terms)
#
#     print ('finished exporting for ', V)


# # step 2:
# sample_size = 20
# # Generate the VM group
# # sameAs_dic
# for V in range (10): # 0 - 999, 10 groups
#     collect_data_VM = []
#     for k in sameAs_dic.keys():
#         terms = sameAs_dic[k] # k = group_id
#         VM_id = int(len(terms) / 100) # an VM id
#         if VM_id == V:
#             collect_data_VM.append((k,sameAs_dic[k]))
#     # select 100 randomly from them # size
#     print ('size = ', len (collect_data_VM))
#
#     Vsample = random.sample(collect_data_VM, sample_size)
#     # export these 100 to a file
#     file_name = 'SA' + str(V) + '.csv'
#     file =  open(file_name, 'w', newline='')
#     writer = csv.writer(file)
#     # writer.writerow([ "GROUP_ID", "TERMS"])
#     for (k, terms) in Vsample:
#         writer.writerow(terms)
#
#     print ('finished exporting for ', V)
#
#
# step 2:
sample_size = 10
# Generate the VM group
# sameAs_dic
# for V in range (10): # 0 - 99999, 10 groups
collect_data_VM = []
count = 0

with open(path) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=' ')
    count = 0
    for row in csv_reader:
        index = int(row[0])
        terms = []
        for i in range (len (row)):
            if i > 0:
                # print (index, row[i])
                terms.append(row[i])

        size = len(terms)
        if size > 1000:
            print ('exporting ', index)
            export_filename = 'SB_' + str(index) + '_'  + str(size) +'.csv'
            # file =  open(file_name, 'w', newline='')
            # writer = csv.writer(file)
            # writer.writerow([ "GROUP_ID", "TERMS"])
            # for (k, terms) in Vsample:
            # writer.writerow(terms)
            print ('t0: ', terms [0])
            g = obtain_graph(terms)
            # export the graph
            # nx.write_edgelist(g, export_filename)
            export_graph_csv(export_filename, g)
            # index += 1

            # h = nx.read_edgelist(export_filename)
            h = read_graph_csv(export_filename)

            # print ('G- No. Nodes: ', len(g.nodes))
            # print ('G- No. Edges: ', len(g.edges))
            # print ('H- No. Nodes: ', len(h.nodes))
            # print ('H- No. Edges: ', len(h.edges))
            print ('edges: ', len (g.edges))
            print ('nodes: ', len (g.nodes))
            if len(h.edges) != len(g.edges):
                print ('********* error *************')

    print ('count  = ', count)
