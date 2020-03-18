from mygraph import GraphSolver, MyGraph
import kivy
import random
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

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


img_before = '''
Image:
        source: 'before.png'
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

class MyWidget(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


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
        self.num_additional_edges = 1

        self.count_TN = 0.0
        self.count_FN = 0.0
        self.count_FP = 0.0
        self.count_TP = 0.0

        self.precision = 0.0
        self.recall = 0.0
        self.accuracy = 0.0

        self.one_time = 0.0
        self.all_time = 0.0

        # main_layout = BoxLayout(padding=10, orientation="horizontal")
        main_layout = GridLayout(cols=3)

        # First Column
        first_ver_layout = BoxLayout(orientation='vertical')
        first_ver_layout.add_widget(Builder.load_string((img_before)))
        # first row:
        # N
        box_N = BoxLayout(orientation='horizontal', spacing=20)
        box_N.add_widget(Label(text='N', halign='left', size_hint=(None,.4), markup=True))
        self.N_input = TextInput(hint_text='100', size_hint=(.5,.4))
        self.N_input.text = '100'
        box_N.add_widget(self.N_input)
        first_ver_layout.add_widget(box_N)
        # M
        box_M = BoxLayout(orientation='horizontal')
        box_M.add_widget(Label(text='M', halign='left', size_hint=(None,.4), markup=True))
        self.M_input = TextInput(hint_text='5', size_hint=(.5,.4))
        self.M_input.text = '5'
        box_M.add_widget(self.M_input)
        first_ver_layout.add_widget(box_M)
        # concepts_size
        box_C = BoxLayout(orientation='horizontal')
        box_C.add_widget(Label(text='C', halign='left', size_hint=(None,.4), markup=True))
        self.C_input = TextInput(hint_text='5', size_hint=(.5,.4))
        self.C_input.text = '5'
        box_C.add_widget(self.C_input)
        first_ver_layout.add_widget(box_C)
        # alpha
        box_alpha = BoxLayout(orientation='horizontal', spacing=20)
        box_alpha.add_widget(Label(text='alpha', halign='left', size_hint=(None,.4), markup=True))
        self.alpha_input = TextInput(hint_text='1.5', size_hint=(.5,.4))
        self.alpha_input.text = '1.5'
        box_alpha.add_widget(self.alpha_input)
        first_ver_layout.add_widget(box_alpha)
        # beta
        box_beta = BoxLayout(orientation='horizontal', spacing=20)
        box_beta.add_widget(Label(text='beta', halign='left', size_hint=(None,.4), markup=True))
        self.beta_input = TextInput(hint_text='1.0', size_hint=(.5,.4))
        self.beta_input.text = '1.0'
        box_beta.add_widget(self.beta_input)
        first_ver_layout.add_widget(box_beta)


        # second row:

        # finally
        main_layout.add_widget(first_ver_layout)

        # Second Column
        second_ver_layout = BoxLayout(orientation='vertical')
        second_ver_layout.add_widget(Builder.load_string((img_after)))
        # first row:
        # number of edges in between: num_edges_between
        box_N = BoxLayout(orientation='horizontal', spacing=20)
        box_N.add_widget(Label(text='No. Add\'Edges', halign='left', size_hint=(.5,.4), markup=True))
        self.N_input = TextInput(hint_text='60', size_hint=(.5,.4))
        self.N_input.text = '100'
        box_N.add_widget(self.N_input)
        second_ver_layout.add_widget(box_N)

        # display the evaluation result
        box_T = BoxLayout(orientation='horizontal', spacing=20)
        box_T.add_widget(Label(text='TP = ' + str(self.count_TP), halign='left', size_hint=(None,.4), markup=True))
        # second_ver_layout.add_widget(box_TP)
        box_T.add_widget(Label(text='TN = ' + str(self.count_TN), halign='left', size_hint=(None,.4), markup=True))
        second_ver_layout.add_widget(box_T)


        box_F = BoxLayout(orientation='horizontal', spacing=20)
        box_F.add_widget(Label(text='FP = ' + str(self.count_FP), halign='left', size_hint=(None,.4), markup=True))
        # second_ver_layout.add_widget(box_TP)
        box_F.add_widget(Label(text='FN = ' + str(self.count_FN), halign='left', size_hint=(None,.4), markup=True))
        second_ver_layout.add_widget(box_F)


        box_X = BoxLayout(orientation='horizontal', spacing=20)
        box_X.add_widget(Label(text='precision = ' + str(self.precision), halign='left', size_hint=(None,.4), markup=True))
        # second_ver_layout.add_widget(box_TP)
        box_X.add_widget(Label(text='recall = ' + str(self.recall), halign='left', size_hint=(None,.4), markup=True))
        box_X.add_widget(Label(text='accuracy = ' + str(self.accuracy), halign='left', size_hint=(None,.4), markup=True))
        second_ver_layout.add_widget(box_X)

        box_Y = BoxLayout(orientation='horizontal', spacing=20)
        box_Y.add_widget(Label(text='time4it = ' + str(self.one_time), halign='left', size_hint=(None,.9), markup=False))
        # second_ver_layout.add_widget(box_TP)
        # box_X.add_widget(Label(text='recall = ' + str(self.recall), halign='left', size_hint=(None,.4), markup=True))
        # box_X.add_widget(Label(text='accuracy = ' + str(self.accuracy), halign='left', size_hint=(None,.4), markup=True))
        second_ver_layout.add_widget(box_Y)


        # finally, a button to update the parameters
        box = BoxLayout(orientation='horizontal', spacing=20)
        btn = Button(text='Go', on_press= self.update_parameter, size_hint=(.1,.2))
        box.add_widget(btn)
        second_ver_layout.add_widget(box)

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

        Window.size = (1000, 1200)

        return main_layout

    def update_parameter(self, instance):
        print ('C = ', self.C_input.text)
        # column 1
        self.C = int(self.C_input.text)
        self.N = int(self.N_input.text)
        self.M = int(self.M_input.text)
        self.alpha = float(self.alpha_input.text)
        self.beta = float(self.beta_input.text)
        # column 2
        self.edges_between = int (self.edges_between_input.text)
        # column 3
        self.num_graph = int(self.num_graph_input.text)



    # def __init__(self, num_graph):
    #     print ('start the system')
    #     self.num_graph = num_graph
    #     self.graphs = []
    #     self.solvers = []
    #
    #     self.app = NestedLayoutExample()
    #
    def create_graphs(self, num_graph):
        for i in range (self.num_graph):
            g = MyGraph(concepts_size = 15, N =100, M = 5, alpha = 0.05, beta = 3)
            self.graphs.append(g)
    #
    def solve_graphs(self):
        for i in range (self.num_graph):
            self.graphs.append(self.num_graph)
    #
    #
    # def show_UI(self):
    #     self.app.run()



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
# num_additional_edges = 60
# s = GraphSolver(g, num_additional_edges)
# s.solve()
# s.obtain_statistics_and_graph()
# s.print_info()




# kvWidget_before = """
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
#             source: 'before.png'
#
#             keep_ratio: True
#
# """


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
