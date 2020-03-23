#test sameAs data
# read and analysis the data
import csv
import matplotlib.pyplot as plt
import numpy as np


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

with open(path) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=' ')
    # count = 0
    for row in csv_reader:
        index = int(row[0])
        terms = []
        for i in range (len (row)):
            if i > 0:
                # print (index, row[i])
                terms.append(row[i])
        sameAs_dic[index] = terms
        # print ('\n')
        # count += 1
        # if count > 1000000:
        #     break

max = 0
for k in sameAs_dic.keys():
    l = len (sameAs_dic[k])
    if l > max:
        max = l

print('max = ', max)

X = list (range(max + 1))
Y = [0] * len(range(max + 1))

for k in sameAs_dic.keys():
    l = len (sameAs_dic[k])
    # print ('l = ',l)
    Y[l] += 1


for x in range(max):
    print (X[x], ' ', Y[x])

plt.plot(X, Y, 'bo')

plt.show()
