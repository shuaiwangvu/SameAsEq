from mygraph import  MyGraph
from graphSolver import GraphSolver

import kivy
import random

import datetime
import time
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image, AsyncImage
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
import networkx as nx
import tldextract
from functools import partial

# to change the kivy default settings we use this module config
from kivy.config import Config
from kivy.core.window import Window

# 0 being off 1 being on as in true / false
# you can use 0 or 1 && True or False
Config.set('graphics', 'resizable', True)

red = [1,0,0,1]
green = [0,1,0,1]
blue =  [0,0,1,1]
purple = [1,0,1,1]


img_before =  '''
Image:
        source: 'before.png'
        allow_stretch: False
        keep_ratio: True
        size_hint_y: None
        size_hint_x: None
        width: 500
        height: self.width/self.image_ratio
        '''

img_attack = '''
Image:
        source: 'attack.png'
        allow_stretch: False
        keep_ratio: True
        size_hint_y: None
        size_hint_x: None
        width: 500
        height: self.width/self.image_ratio
        '''


img_after = '''
Image:
        source: 'after.png'
        allow_stretch: False
        keep_ratio: True
        size_hint_y: None
        size_hint_x: None
        width: 500
        height: self.width/self.image_ratio
        '''



GENERATE = False
LOAD = True

colors = [red, green, blue, purple]

########################################################################
class NestedLayoutExample(App):
    """
    An example of nesting three horizontally oriented BoxLayouts inside
    of one vertically oriented BoxLayout
    """
    #----------------------------------------------------------------------

    def build(self): # this is kind of like the init function
        """
        Horizontal BoxLayout example
        """


        self.solver = None
        self.pos = None
        self.labels = None

        self.num_graph = 0
        self.graphs = []
        self.graph_solvers = []

        # first, define a parameter manager
        self.path_to_dataset = ''
        self.C = 0 # number of concepts
        self.N = 0 # for the generation of graphs
        self.M = 0 # for the generation of graphs
        self.alpha = 0 # how many edges in between each pair
        self.beta = 0 # how many pairs chosen
        # parameters in the second column
        self.ratio_additional_edges = 1.0

        self.path = None

        self.count_TN = 0.0
        self.count_FN = 0.0
        self.count_FP = 0.0
        self.count_TP = 0.0

        self.precision = 0.0
        self.recall = 0.0
        self.accuracy = 0.0

        self.num_removed = 0
        self.num_subgraphs = 0
        self.num_total_edges = 0
        self.num_attacking_edges = 0

        self.one_time = "TBA"
        self.all_time = "TBA"

        # main_layout = BoxLayout(padding=10, orientation="horizontal")
        main_layout = GridLayout(cols=2)

        # First Column
        first_ver_layout = BoxLayout(orientation='vertical')
        self.before_img = Builder.load_string((img_before))
        first_ver_layout.add_widget(self.before_img)
        # first row:
        # N
        box_Path = BoxLayout(orientation='horizontal', spacing=10)
        box_Path.add_widget(Label(text='Path to file', halign='left', size_hint=(.1,.1), markup=True))
        self.Path_input = TextInput(hint_text='100', size_hint=(.1,.2))
        self.Path_input.text = './obama-links-error-degree.csv'
        box_Path.add_widget(self.Path_input)
        first_ver_layout.add_widget(box_Path)
        # # M
        # box_M = BoxLayout(orientation='horizontal')
        # box_M.add_widget(Label(text='M', halign='left', size_hint=(None,.4), markup=True))
        # self.M_input = TextInput(hint_text='5', size_hint=(.5,.4))
        # self.M_input.text = '5'
        # box_M.add_widget(self.M_input)
        # first_ver_layout.add_widget(box_M)
        # # concepts_size
        # box_C = BoxLayout(orientation='horizontal')
        # box_C.add_widget(Label(text='C', halign='left', size_hint=(None,.4), markup=True))
        # self.C_input = TextInput(hint_text='5', size_hint=(.5,.4))
        # self.C_input.text = '10'
        # box_C.add_widget(self.C_input)
        # first_ver_layout.add_widget(box_C)
        # # alpha
        # box_alpha = BoxLayout(orientation='horizontal', spacing=20)
        # box_alpha.add_widget(Label(text='alpha', halign='left', size_hint=(None,.4), markup=True))
        # self.alpha_input = TextInput(hint_text='0.1', size_hint=(.5,.4))
        # self.alpha_input.text = '0.1'
        # box_alpha.add_widget(self.alpha_input)
        # first_ver_layout.add_widget(box_alpha)
        # # beta
        # box_beta = BoxLayout(orientation='horizontal', spacing=20)
        # box_beta.add_widget(Label(text='beta', halign='left', size_hint=(None,.4), markup=True))
        # self.beta_input = TextInput(hint_text='2.5', size_hint=(.5,.4))
        # self.beta_input.text = '2.0'
        # box_beta.add_widget(self.beta_input)
        # first_ver_layout.add_widget(box_beta)
        # finally, a button to update the parameters
        box = BoxLayout(orientation='horizontal', spacing=20)
        btn = Button(text='Load', on_press= self.load_graph, size_hint=(.1,.2))
        box.add_widget(btn)
        first_ver_layout.add_widget(box)


        # second row:

        # finally
        main_layout.add_widget(first_ver_layout)

        # Second Column
        second_ver_layout = BoxLayout(orientation='vertical')
        # attack
        self.attack_img = Builder.load_string((img_attack))
        second_ver_layout.add_widget(self.attack_img)

        box_TE = BoxLayout(orientation='horizontal', spacing=20)
        self.TE_label = Label(text='Total Edges = ' + str(self.num_total_edges), halign='left', size_hint=(.1,.2), markup=True)
        box_TE.add_widget(self.TE_label)
        second_ver_layout.add_widget(box_TE)

        box_AE = BoxLayout(orientation='horizontal', spacing=20)
        self.AE_label = Label(text='Attacking Edges = ' + str(self.num_attacking_edges), halign='left', size_hint=(.1,.2), markup=True)
        box_AE.add_widget(self.AE_label)
        second_ver_layout.add_widget(box_AE)


        # after
        self.after_img = Builder.load_string((img_after))
        second_ver_layout.add_widget(self.after_img)
        # first row:
        # number of edges in between: num_edges_between
        box_A = BoxLayout(orientation='horizontal', spacing=20)
        box_A.add_widget(Label(text='Ratio. Add\'Edges', halign='left', size_hint=(.5,.4), markup=True))
        self.A_input = TextInput(hint_text='1.4', size_hint=(.1,.2))
        self.A_input.text = '1.4'
        box_A.add_widget(self.A_input)
        # second_ver_layout.add_widget(box_A)

        # display the evaluation result
        box_T = BoxLayout(orientation='horizontal', spacing=20)
        self.TP_label = Label(text='TP = ' + str(self.count_TP), halign='left', size_hint=(.1,.4), markup=True)
        box_T.add_widget(self.TP_label)
        # second_ver_layout.add_widget(box_TP)
        self.TN_label = Label(text='TN = ' + str(self.count_TN), halign='left', size_hint=(.1,.4), markup=True)
        box_T.add_widget(self.TN_label)
        # second_ver_layout.add_widget(box_T)


        box_F = BoxLayout(orientation='horizontal', spacing=20)
        self.FP_label = Label(text='FP = ' + str(self.count_FP), halign='left', size_hint=(.1,.4), markup=True)
        box_F.add_widget(self.FP_label)
        # second_ver_layout.add_widget(box_TP)
        self.FN_label = Label(text='FN = ' + str(self.count_FN), halign='left', size_hint=(.1,.4), markup=True)
        box_F.add_widget(self.FN_label)
        # second_ver_layout.add_widget(box_F)


        box_X = BoxLayout(orientation='horizontal', spacing=20)
        self.precision_label = Label(text='precision = ' + str(self.precision), halign='left', size_hint=(.1,.4), markup=True)
        box_X.add_widget(self.precision_label)
        # second_ver_layout.add_widget(box_TP)
        self.recall_label = Label(text='recall = ' + str(self.recall), halign='left', size_hint=(.1,.4), markup=True)
        box_X.add_widget(self.recall_label)
        self.accuracy_label = Label(text='accuracy = ' + str(self.accuracy), halign='left', size_hint=(.1,.4), markup=True)
        box_X.add_widget(self.accuracy_label)
        # second_ver_layout.add_widget(box_X)

        box_NUM = BoxLayout(orientation='horizontal', spacing=20)
        self.num_removed_label = Label(text='No.removed edges = ' + str(self.num_removed), halign='left', size_hint=(.1,.9), markup=False)
        box_NUM.add_widget(self.num_removed_label)
        second_ver_layout.add_widget(box_NUM)

        box_NUM_SUM = BoxLayout(orientation='horizontal', spacing=20)
        self.num_subgraphs_label = Label(text='No.subgraphs = ' + str(self.num_subgraphs), halign='left', size_hint=(.1,.9), markup=False)
        box_NUM_SUM.add_widget(self.num_subgraphs_label)
        second_ver_layout.add_widget(box_NUM_SUM)

        box_Y = BoxLayout(orientation='horizontal', spacing=20)
        self.one_time_label = Label(text='Time = ' + str(self.one_time), halign='left', size_hint=(.1,.2), markup=False)
        box_Y.add_widget(self.one_time_label)
        second_ver_layout.add_widget(box_Y)

        # second_ver_layout.add_widget(box_TP)
        # box_X.add_widget(Label(text='recall = ' + str(self.recall), halign='left', size_hint=(None,.4), markup=True))
        # box_X.add_widget(Label(text='accuracy = ' + str(self.accuracy), halign='left', size_hint=(None,.4), markup=True))
        # second_ver_layout.add_widget(box_Y)


        # finally, a button to update the parameters
        # box = BoxLayout(orientation='horizontal', spacing=20)
        # btn = Button(text='Go', on_press= self.go, size_hint=(.1,.2))
        # box.add_widget(btn)
        # second_ver_layout.add_widget(box)

        box2 = BoxLayout(orientation='horizontal', spacing=20)
        btn2 = Button(text='Go', on_press= self.go, size_hint=(.5,.8))
        box2.add_widget(btn2)
        second_ver_layout.add_widget(box2)

        # finally
        main_layout.add_widget(second_ver_layout)

        # h_layout2 = BoxLayout(padding=20)
        # im = Image(source = 'before.png')
        # -- do something --
        # im.reload()
        # main_layout.add_widget(s)
        # FNTSIZE =  11
        # filterin = TextInput(text='input file', multiline=False, font_size=FNTSIZE)
        # t = Widget()
        # t.add_widget(filterin)
        # h_layout2.add_widget(t)
        # main_layout.add_widget(t)

        Window.size = (1400, 1000)

        # for i in range(100, 0, -1):
        #     Clock.schedule_once(partial(self.before_img.update, str(i)), 10-i)

        return main_layout

    def load_graph(self, instance):
        # print ('clear all the graphs and load the graph at path')
        # self.path = self.Path_input.text
        # # print ('path is at ', self.path)
        # h = nx.read_edgelist(self.path)
        # g = MyGraph()
        # g.G =  h
        # self.graphs = []
        # self.graphs.append(g)
        # colors = ['b', 'g', 'r'] * len(h.edges)
        # self.graphs[0].save_graph('before.png')
        self.solver = GraphSolver()
        self.solver.G.load_graph_with_error_degree(self.Path_input.text)

        # print ('graph loaded and the No. nodes are', len (self.graphs[0].G.nodes))
        # print ('graph loaded and the No. edges are', len (self.graphs[0].G.edges))

        self.pos, self.labels = self.solver.G.save_graph(file_name = 'before')

        self.refresh_UI()

    def go (self, instance):
        print ('update the parameter')
        # self.update_parameter()
        # self.create_graphs()
        self.solve_graphs()
        # self.save_to_png()
        self.refresh_UI()
    #
    #
    # def update_parameter(self):
    #     print ('C = ', self.C_input.text)
    #     # column 1
    #     self.C = int(self.C_input.text)
    #     self.N = int(self.N_input.text)
    #     self.M = int(self.M_input.text)
    #     self.alpha = float(self.alpha_input.text)
    #     self.beta = float(self.beta_input.text)
    #     # column 2
    #     self.ratio_additional_edges = float (self.A_input.text)
    #     # column 3
    #     # self.num_graph = int(self.A_input.text)
    #
    #
    #
    # # def __init__(self, num_graph):
    # #     print ('start the system')
    # #     self.num_graph = num_graph
    # #     self.graphs = []
    # #     self.solvers = []
    # #
    # #     self.app = NestedLayoutExample()
    # #
    # def create_graphs(self):
    #     self.graphs = []
    #     self.graph_solvers = []
    #     self.num_graph = 1
    #     for i in range (self.num_graph):
    #         mg = MyGraph(concepts_size = self.C, N = self.N, M = self.M, alpha = self.alpha, beta = self.beta)
    #         mg.create_graph()
    #         # mg.show_graph()
    #         print ('how many nodes are there? ', len(mg.G.nodes))
    #         self.graphs.append(mg)

    def solve_graphs(self):
        round_start = time.time()
        # ====
        self.solver.encode()
        print ('now solve')
        self.solver.G.save_graph(file_name = 'attack', pos = self.pos, attacking_edges = self.solver.additional_attacking_edges)
        self.num_total_edges = len(self.solver.G.subgraphs[0].edges)
        self.num_attacking_edges = len(self.solver.additional_attacking_edges)
        self.solver.solve()
        print ('now decode')
        self.solver.decode()
        self.num_removed = len(self.solver.removed_edges)
        self.num_subgraphs = self.solver.num_subgraphs

        self.solver.H.save_graph(file_name = 'after',  pos= self.pos, labels = self.labels)

        for (l, r) in self.solver.removed_edges:
            if (l, r) in self.solver.G.error_degree.keys():
                print ('the error degree is :', self.solver.G.error_degree[(l,r)])
                print ('\t\t (', l, ', ', r, ' )')
            elif (r, l) in self.solver.G.error_degree.keys():
                print ('the error degree is :', self.solver.G.error_degree[(r,l)])
                print ('\t\t (', l, ', ', r, ' )')
            else:
                print ('*not in the keys: ', l, r)

        print ('# TOTAL REMOVED EDGES: ', len (self.solver.removed_edges))

        # ==
        round_end = time.time()
        hours, rem = divmod(round_end - round_start, 3600)
        minutes, seconds = divmod(rem, 60)
        self.one_time = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)

    def save_to_png(self):
        print ('save_to_png: before and after')
        colors = ['b', 'g', 'r'] * self.graphs[0].N
        before_pos = self.graphs[0].save_graph('before.png', colors = colors)
        self.graph_solvers[0].save_graph('after.png', pos = before_pos, colors = colors)


    def refresh_UI(self):

        self.before_img.reload()
        self.after_img.reload()
        self.attack_img.reload()
        self.TP_label.text = '*TP = '+str(self.count_TP)
        self.TN_label.text = '*TN = '+str(self.count_TN)
        self.FP_label.text = '*FP = '+str(self.count_FP)
        self.FN_label.text = '*FN = '+str(self.count_FN)
        self.precision_label.text = '*precision = %.2f'%self.precision
        self.recall_label.text = '*recall = %.2f'%self.recall
        self.accuracy_label.text = '*accuracy = %.2f'%self.accuracy
        self.one_time_label.text = 'Time = '+str(self.one_time)
        self.num_removed_label.text = 'No.removed edges = ' + str(self.num_removed)
        self.num_subgraphs_label.text = 'No.subgraphs = ' + str(self.num_subgraphs)
        self.TE_label.text = 'No. Total Edges = '+ str(self.num_total_edges)
        self.AE_label.text = 'No. Attackign Edges (red) = '+ str(self.num_attacking_edges)


if __name__ == "__main__":
    n = NestedLayoutExample()

    n.run()








        # for i in range(3):
        #     h_layout = BoxLayout(padding=10)
        #     for i in range(5):
        #         btn = Button(text="Button #%s" % (i+1),
        #                      background_color=random.choice(colors)
        #                      )
        #
        #         h_layout.add_widget(btn)
        #     main_layout.add_widget(h_layout)

        # main_layout.add_widget(Button(text='Hello 1'))


        # h_layout = BoxLayout(padding=10)
        # img = Image(source ='before.png', allow_stretch=True)

        # By default, the image is centered and fits
        # inside the widget bounding box.
        # If you don’t want that,
        # you can set allow_stretch to
        # True and keep_ratio to False.
        # img.allow_stretch = True
        # img.keep_ratio = False

        # Providing Size to the image
        # it varies from 0 to 1
        # img.size_hint_x = 1
        # img.size_hint_y = 1

        # Position set
        # img.pos = (100, 100)

        # Opacity adjust the fadeness of the image if
        # 0 then it is complete black
        # 1 then original
        # it varies from 0 to 1
        # img.opacity = 1
        # s = Widget()
        # s.add_widget(img)





# g = MyGraph(concepts_size = 15, N =100, M = 5, alpha = 0.05, beta = 3)
# g.create_graph()
# # g.show_graph()
#
# ratio_additional_edges = 60
# s = GraphSolver(g, ratio_additional_edges)
# s.solve()
# s.obtain_statistics_and_graph()
# s.print_info()






#
# kvWidget_after = """
#
# MyWidget:
#
#     orientation: 'vertical'
#
#     canvas:
#
#         Rectangle:
#
#             size: self.size
#
#             pos: self.pos
#
#             source: 'after.png'
#
# """
