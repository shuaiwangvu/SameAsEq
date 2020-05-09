#test sameAs data
# read and analysis the data
import csv
import matplotlib.pyplot as plt
import numpy as np
import random

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
    count = 0
    for row in csv_reader:
        index = int(row[0])
        terms = []
        for i in range (len (row)):
            if i > 0:
                # print (index, row[i])
                terms.append(row[i])
        sameAs_dic[index] = terms
        # print ('\n')
        count += 1
        if count % 100000 == 0:
            print (count)

max = 0
for k in sameAs_dic.keys():
    l = len (sameAs_dic[k])
    if l > max:
        max = l

print('max = ', max)

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
sample_size = 20
# Generate the VM group
# sameAs_dic
for V in range (10): # 0 - 9999, 10 groups
    collect_data_VM = []
    for k in sameAs_dic.keys():
        terms = sameAs_dic[k] # k = group_id
        VM_id = int(len(terms) / 1000) # an VM id
        if VM_id == V:
            collect_data_VM.append((k,sameAs_dic[k]))
    # select 100 randomly from them # size
    print ('size = ', len (collect_data_VM))

    Vsample = random.sample(collect_data_VM, sample_size)
    # export these 100 to a file
    file_name = 'SB' + str(V) + '.csv'
    file =  open(file_name, 'w', newline='')
    writer = csv.writer(file)
    # writer.writerow([ "GROUP_ID", "TERMS"])
    for (k, terms) in Vsample:
        writer.writerow(terms)

    print ('finished exporting for ', V)
