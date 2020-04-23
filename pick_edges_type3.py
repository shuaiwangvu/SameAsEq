# for all the files in the /generate_data/MyType3 directory, find those who has
# edges that are linking two clusters of obvious differnt concepts.
# the resulting data can be further processed as that of Type 2


from mygraph import *



if __name__ == "__main__":
    n = MyGraph()
    n.load_graph('./generate_data/MyType3/SA4_0.csv')
    g = n.subgraphs[0]
    n.save_graph(file_name = 'SA4_0')
    # N = 2 # related to pokemon or the person
    # collect_person_nodes = []
    # for e in g.edges:
    #     (l, r) = e
    #     if l == 'http://rdf.freebase.com/ns/m.07f_3m':
    #         print ('right  = ', r)
    #     if r == 'http://rdf.freebase.com/ns/m.07f_3m':
    #         print ('left  = ', l)
    #
    # NOW Export the nodes
    # file_name = './generate_data/MYType3/SA4_0_nodes.csv'
    # file =  open(file_name, 'w', newline='')
    # writer = csv.writer(file)
    # writer.writerow(['Node','Label'])
    # for n in g.nodes:
    #     writer.writerow([n, '?'])

    # read the file and see what the potential edges errornous edges are about
    file_name = open('./generate_data/MyType3/SA4_0_nodes.csv', 'r')
    reader = csv.DictReader(file_name)
    label_dict = {}
    for row in reader:
        n = row["Node"]
        l = row["Label"]
        label_dict[n] = l

    for e in g.edges:
        (l, r) = e
        if label_dict[l] != label_dict[r] and label_dict[l] != '?'  and label_dict[r]!= '?':
            print ('l (', label_dict[l], ') = ', l)
            print ('r (', label_dict[r], ') = ', r)

    # collect_u = []
    # collect_m = []
    # collect_x = []
    #
    # for n in g.nodes:
    #     print (n, flush=True)
    #     c = input()
    #     if c == 'u':
    #         collect_u.append(n)
    #     elif c == 'm' :
    #         collect_m.append(n)
    #     elif c == 'x':
    #         collect_x.append(n)
    #     elif c == 'n':
    #         collect_x.append(n)
    #
    # print (n)
    # for e in g.edges:
    #     (l, r) = e
    #     if (l in collect_u and r not in collect_u) or (l not in collect_u and r in collect_u):
    #         print ('this may be a wrong edge for u: ', e)
    #     if (l in collect_m and r not in collect_m) or (l not in collect_m and r in collect_m):
    #         print ('this may be a wrong edge for m: ', e)
    #     if (l in collect_x and r not in collect_x) or (l not in collect_x and r in collect_x):
    #         print ('this may be a wrong edge for x: ', e)
    #     if (l in collect_n and r not in collect_n) or (l not in collect_n and r in collect_n):
    #         print ('this may be a wrong edge for n: ', e)
    #
    #
