# this file is about retrieving the corresponding groups of the mannually annotated
# groups by Al.

# data sent by Joe
import csv
import matplotlib.pyplot as plt
import numpy as np
import random



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

with open(path) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=' ')
    # count = 0
    for row in csv_reader:
        index = int(row[0])
        if index in name_list:
            terms = []
            for i in range (len (row)):
                if i > 0:
                    # print (index, row[i])
                    terms.append(row[i])
                    # export to csv file
                    print (terms)
