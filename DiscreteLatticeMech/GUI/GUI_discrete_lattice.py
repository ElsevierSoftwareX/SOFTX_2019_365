# GUI Homogenization Lattice 
# 15 Nov 2019

import copy
import json
import math
import os
import sys
import xml.etree.ElementTree as ET

import matplotlib.mathtext as mt
import numpy as np
import wx
import wx.grid
from matplotlib.mathtext import MathTextParser

gui_location = os.path.dirname(os.path.abspath(__file__))
package_location = gui_location + '/../../'
print(package_location)
sys.path.append(package_location)

from DiscreteLatticeMech import Solver, Writer

def rotate_vector(vector, angle):
    """ Rotate a vector according to an angle (rad)"""
    vect1 = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    vect2 = np.matmul(vect1, vector)
    return vect2


def normalize_vector(vector):
    """return norm of vector"""
    vect1 = vector/np.linalg.norm(vector)
    return vect1


class view(object):
    """Deal with coordinates in screen vs world 

    translation_x: x coordinates of stored translation vector world coord 
    translation_y: y coordinates of stored translation vector world coord
    translation_P1x: x coord of first point of current translation additional vector
    translation_P1y: y coord of first point of current translation additional vector
    translation_activate: a current translation additional vector is mouse activated
    Mouse_position: stored actual mouse position
    zoom: zoom factor
    height: height of the graphic window for drawings
    width: width of the graphic window for drawings

    get_translation(): return the current translation additional vector in screen coordinates
    screen_to_world(x_screen,y_screen): convert screen coordinates in world coordinates
    world_to_screen(x_world,y_world): convert world coordinates in screen coordinates
    mathtext_to_wxbitmap(s): return a bitmap from a Latex string 
    """
    def __init__(self, translation_x, translation_y, translation_P1x, translation_P1y, zoom,
                 translation_activate, Mouse_position, height, width):

        self.translation_x = translation_x
        self.translation_y = translation_y
        self.translation_P1x = translation_P1x
        self.translation_P1y = translation_P1y
        self.translation_activate = translation_activate
        self.Mouse_position = Mouse_position
        self.zoom = zoom
        self.height = height
        self.width = width
        #
        self.mathtext_parser = MathTextParser("Bitmap")
        rc = {"font.family": "serif", "mathtext.fontset": "stix"}
        mt.rcParams.update(rc)
        mt.rcParams["font.serif"] = ["Times New Roman"] + mt.rcParams["font.serif"]

    def get_translation(self):
        """return the translation vector in screen coordinates"""

        if self.translation_activate:
            P1 = self.world_to_screen(self.translation_P1x, self.translation_P1y)
            P2 = np.array([self.Mouse_position.x, self.Mouse_position.y])
            trans = P2-P1
        else:
            trans = np.array([0, 0])
        return trans

    def screen_to_world(self, x_screen, y_screen):
        """ Convert screen coordinates in world coordinates

        (x_world,y_world) = (x_screen,y_screen)/zoom-Translation
        """
        pos_x = x_screen/self.zoom-self.translation_x
        pos_y = (self.height-y_screen)/self.zoom-self.translation_y
        return np.array([pos_x, pos_y])

    def world_to_screen(self, x_world, y_world):
        """ Convert world coordinates in screen coordinates

        (x_screen,y_screen) = ((x_world,y_world)+Translation)*zoom
        """
        pos_x = (x_world+self.translation_x)*self.zoom
        pos_y = self.height-(y_world+self.translation_y)*self.zoom
        return np.array([pos_x, pos_y])

    def mathtext_to_wxbitmap(self, s):
        """Convert a Latex string in bitmap """
        ftimage, depth = self.mathtext_parser.parse(s, 150)
        return wx.Bitmap.FromBufferRGBA(
            ftimage.get_width(), ftimage.get_height(),
            ftimage.as_rgba_str())


class periodicity(object):
    """Class for object : periodicity vectors

    x: x value
    y: y value
    length: length
    number: identifier

    draw(dc, view): draw the vector
    """
    def __init__(self, x, y, length, number):
        self.x = x
        self.y = y
        self.length = length
        self.number = number

    def draw(self, dc, view):
        """draw the vector """
        trans = view.get_translation()
        v = np.array([self.x, self.y])*self.length
        P1 = view.world_to_screen(v[0], v[1])+trans
        P0 = view.world_to_screen(0, 0)+trans

        e1 = normalize_vector(v)
        e2 = rotate_vector(e1, 5*np.pi/6)
        e3 = rotate_vector(e1, 7*np.pi/6)

        # La = self.length/10
        P2 = v+e2*self.length/10
        P3 = v+e3*self.length/10
        P2 = view.world_to_screen(P2[0], P2[1])+trans
        P3 = view.world_to_screen(P3[0], P3[1])+trans

        dc.SetPen(wx.Pen("DARK GREEN", 3, style=wx.PENSTYLE_LONG_DASH))

        dc.DrawLine(P0[0], P0[1], P1[0], P1[1])
        dc.DrawLine(P1[0], P1[1], P2[0], P2[1])
        dc.DrawLine(P1[0], P1[1], P3[0], P3[1])

        Pos_text_1 = (P0+P1)/2

        s = str(self.number)

        bitmap = view.mathtext_to_wxbitmap("$\overrightarrow {{Y_"+s+"}} $")

        dc.DrawBitmap(bitmap, Pos_text_1[0]-bitmap.Width-2, Pos_text_1[1]+2, True)


class node(object):
    """Class for object: node

    x: x coordinate
    y: y coordinate
    radius: radius for screen drawing in pixel
    number: identifier
    focused: True in case of mouse motion on it with mode delete or add beam
    delta_1_focus: delta 1 focus value in case with mode add beam P2
    delta_2_focus: delta 2 focus value in case with mode add beam P2

    draw(parent, dc, view): draw node and all periodic nodes around
     """
    def __init__(self, x, y, radius, number):
        self.x = x
        self.y = y
        self.radius = radius
        self.number = number
        self.focused = False
        self.delta_1_focus = 0
        self.delta_2_focus = 0

    def draw(self, parent, dc, view):
        """draw node and all periodic nodes around

        parent: class element parent
        dc: drawing functions class
        view: target graphic window
        """

        pos = np.array([self.x, self.y])

        trans = view.get_translation()

        Y1W = np.array([parent.periods[0].x, parent.periods[0].y])*parent.periods[0].length
        Y2W = np.array([parent.periods[1].x, parent.periods[1].y])*parent.periods[1].length

        pos1 = pos-5*Y1W-5*Y2W

        for i in range(10):
            pos2 = pos1
            for j in range(10):

                dc.SetPen(wx.Pen("GREY", 1))
                dc.SetBrush(wx.Brush("WHITE"))
                pos2_S = view.world_to_screen(pos2[0], pos2[1])+trans

                dc.DrawCircle(pos2_S[0], pos2_S[1], self.radius)

                pos2 = pos2+Y1W

            pos1 = pos1+Y2W

        dc.SetPen(wx.Pen("RED", 1))
        dc.SetBrush(wx.Brush("RED"))

        pos_S = view.world_to_screen(pos[0], pos[1])+trans

        dc.DrawCircle(pos_S[0], pos_S[1], self.radius)

        if self.focused:
            dc.SetPen(wx.Pen("ORANGE", 3))
            dc.SetBrush(wx.Brush("ORANGE"))
            pos1 = pos+self.delta_1_focus*Y1W+self.delta_2_focus*Y2W
            pos1_S = view.world_to_screen(pos1[0], pos1[1])+trans
            dc.DrawCircle(pos1_S[0], pos1_S[1], self.radius*1.5)

        s = str(self.number)
        bitmap = view.mathtext_to_wxbitmap("$n_{"+s+"} $")

        dc.DrawBitmap(bitmap, pos_S[0]-bitmap.Width, pos_S[1]+self.radius+2, True)


class beam(object):
    """Class for object: beam

    node_1: identifier of node 1
    node_2: identifier of node 2
    length: length of the beam
    width: width of the beam
    delta_1: delta 1 factor for Y1 translation vector added to node 2 coordinates 
    delta_2: delta 2 factor for Y2 translation vector added to node 2 coordinates
    e_x: value of x beam director
    e_y: value of y beam director
    ka: value of beam axial stiffness
    kb: value of beam bending stiffness
    material_E: Young modulus(GPa) of beam's material
    number: beam identifier
    section: string identifier for beam section type
    focused: True if mouse motion upon beam if case of delete mode

    evaluate_k(parent): evaluate length, director, stiffnesses ka and kb
    draw(parent, dc, view): draw the beam and periodic beams associated
    """
    def __init__(self, node_1, node_2, delta_1, delta_2, section, length, width, e_x, e_y, ka, kb, material_E, number):
        self.node_1 = node_1
        self.node_2 = node_2
        self.length = length
        self.width = width
        self.delta_1 = delta_1
        self.delta_2 = delta_2
        self.e_x = e_x
        self.e_y = e_y
        self.ka = ka
        self.kb = kb
        self.material_E = material_E
        self.number = number
        self.section = section
        self.focused = False

    def evaluate_k(self, parent):
        """evaluate length, director, stiffnesses ka and kb

        parent: class element (parent)
        """

        N1 = parent.index_node(self.node_1)
        N2 = parent.index_node(self.node_2)
        Y1 = parent.periods[0]
        Y2 = parent.periods[1]
        Y1W = np.array([Y1.x, Y1.y])*Y1.length
        Y2W = np.array([Y2.x, Y2.y])*Y2.length

        N1_coord = np.array([N1.x, N1.y])
        N2_coord = np.array([N2.x+self.delta_1*Y1W[0]+self.delta_2*Y2W[0], N2.y+self.delta_1*Y1W[1]+self.delta_2*Y2W[1]])
        E = N2_coord-N1_coord
        self.length = np.linalg.norm(E)
        E_n = E/self.length
        self.e_x = E_n[0]
        self.e_y = E_n[1]

        self.ka = self.material_E*self.width/self.length
        self.kb = self.material_E*(self.width/self.length)**3

    def draw(self, parent, dc, view):
        """draw the beam and periodic beams associated

        parent : class element
        dc: drawing functions
        view: graphic window
        """
        width = view.zoom*self.width

        N1 = parent.index_node(self.node_1)
        N2 = parent.index_node(self.node_2)
        Y1W = np.array([parent.periods[0].x, parent.periods[0].y])*parent.periods[0].length
        Y2W = np.array([parent.periods[1].x, parent.periods[1].y])*parent.periods[1].length

        N1_W = np.array([N1.x, N1.y])
        N2_W = np.array([N2.x, N2.y])+self.delta_1*Y1W+self.delta_2*Y2W

        trans = view.get_translation()

        N1_W1 = N1_W-5*Y1W-5*Y2W
        N2_W1 = N2_W-5*Y1W-5*Y2W

        for i in range(10):
            N1_W2 = N1_W1
            N2_W2 = N2_W1
            for j in range(10):

                dc.SetPen(wx.Pen("LIGHT BLUE", width))
                N1_S2 = view.world_to_screen(N1_W2[0], N1_W2[1])+trans
                N2_S2 = view.world_to_screen(N2_W2[0], N2_W2[1])+trans

                dc.DrawLine(N1_S2[0], N1_S2[1], N2_S2[0], N2_S2[1])
                N1_W2 = N1_W2+Y1W
                N2_W2 = N2_W2+Y1W

            N1_W1 = N1_W1+Y2W
            N2_W1 = N2_W1+Y2W

        N1_S = view.world_to_screen(N1_W[0], N1_W[1])+trans
        N2_S = view.world_to_screen(N2_W[0], N2_W[1])+trans

        if self.focused:
            dc.SetPen(wx.Pen("ORANGE", width*1.5))
            dc.DrawLine(N1_S[0], N1_S[1], N2_S[0], N2_S[1])
        else:
            dc.SetPen(wx.Pen("BLUE", width))
            dc.DrawLine(N1_S[0], N1_S[1], N2_S[0], N2_S[1])

        s = str(self.number)
        bitmap = view.mathtext_to_wxbitmap("$b_{"+s+"} $")

        dc.DrawBitmap(bitmap, (N1_S[0]+N2_S[0])/2+width/2+2, (N1_S[1]+N2_S[1])/2+width/2+2, True)


class elements(object):
    """Arrays of basic elements of lattice

    nodes[]: array of nodes
    beams[]: array of beams
    periods[]: array of periodicity vectors
    Mode: actual mode 
    P1_acquired: point 1 node for mode ADD BEAM P1
    P1_acquired_bool: True if a Point 1 node is yet acquired 

    draw(dc,view): draw all objects : nodes, beams, periodicity vectors
    index_node(node): return the index of an node based on identifier value

    """
    def __init__(self):
        self.nodes = []
        self.beams = []
        self.periods = []
        self.Mode = "ADD_POINT"
        self.P1_acquired = node(0, 0, 5, 0)
        self.P1_acquired_bool = False

        self.P1_acquired.focused = False

    def draw(self, dc, view):
        """draw all objects : nodes, beams, periodicity vectors

        dc: drawing functions
        view: graphic window
        """
        for i in self.beams:
            i.draw(self, dc, view)
        for i in self.nodes:
            i.draw(self, dc, view)

        if self.P1_acquired.focused:
            self.P1_acquired.draw(self, dc, view)

        for i in self.periods:
            i.draw(dc, view)

    def index_node(self, node):
        """return the index of an node based on identifier value

        node: identifier value
        """
        for i in self.nodes:
            if i.number == node:
                return i


class Graph_window(wx.Window):
    """Class wx.window for the graphic window


    view_1: embed functions for dealing with screen vs world coordinates
    EL: all elements objects (nodes, beams, periodicity vectors)
    Gd_pere: Initial window, necessary function for accessing tree_ctrl
    parent: sub window in initial window defining the limits of graphic window
    last_pos: last mouse position

    reassign_EL(EL): Replace the instance of elements passed in argument
    on_size(event): modify attributes on event SIZE
    on_paint(event): redraw all graphic components on event PAINT
    draw_x(dc, x, y, line_width): draw a cross on mouse position
    update_drawing(): force redrawing
    on_motion(event): update attributes focus on mouse move in mode DELETE ELEMENT,
                        ADD BEAM  
    def on_left_down(event): functions linked to left button according to current mode
    on_right_down(event): Activation of additional translation vector
    on_right_up(event): Add current translation vector to general one
    on_wheel(event): Wheel mouse management of zoom 
    key_zoom(code_zoom): Zoom in / out calculation according to code_zoom 
    Get_world_pos(): give world coordinates of current mouse position

     """
    def __init__(self, parent, Gd_pere, elements):
        wx.Window.__init__(self, parent)
        self.view_1 = view(1, 1, 0, 0, 100, False, 0, 280, 400)

        self.EL = elements
        self.Gd_pere = Gd_pere
        self.parent = parent

        self.last_pos = self.ScreenToClient(wx.GetMousePosition())
        self.buffer = wx.BufferedDC()

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour("WHITE")

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_wheel)

    def save_bmp(self):
        myImage = self.buffer
        myImage.SaveFile("image.bmp", wx.BITMAP_TYPE_BMP)

    def reassign_EL(self, EL):
        """Replace the instance of elements passed in argument"""
        self.EL = EL

    def on_size(self, event):
        """Modify attributes on event SIZE"""
        width, height = self.GetClientSize()
        self._buffer = wx.Bitmap(width, height)
        self.view_1.width = width
        self.view_1.height = height
        self.update_drawing()
        event.Skip()

    def on_paint(self, event):
        """Redraw all graphic components on event PAINT"""
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        Mouse_position = self.ScreenToClient(wx.GetMousePosition())
        self.view_1.Mouse_position = Mouse_position
        #
        #
        if self.view_1.translation_activate:
            dc.SetPen(wx.Pen("BLUE", 2, wx.PENSTYLE_DOT_DASH))
            Pos = self.view_1.world_to_screen(self.view_1.translation_P1x, self.view_1.translation_P1y)
            dc.DrawLine(Pos[0], Pos[1], Mouse_position.x, Mouse_position.y)

        self.draw_x(dc, Mouse_position.x, Mouse_position.y, 1)
        self.EL.draw(dc, self.view_1)

        # size = self.Size
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.LIGHT) 
        dc.SetTextForeground((0, 0, 0))
        dc.SetFont(font)
        if self.Gd_pere.File_saved:
            str1 = "(Saved)"
        else:
            str1 = "(**NOT Saved**)"
        str2 = "Mode :" + self.EL.Mode + " Zoom : %4.2f "+str1
        dc.DrawText(str2 % self.view_1.zoom, 10, 10)
        self.buffer = dc.GetAsBitmap()
        event.Skip()

    def draw_x(self, dc, x, y, line_width):
        """Draw_x(dc, x, y, line_width): draw a cross on mouse position"""
        dc.SetPen(wx.Pen("RED", line_width))
        dc.DrawLine(x-10, y-10, x+10, y+10)  # \
        dc.DrawLine(x-10, y+10, x+10, y-10)  # /

    def update_drawing(self):
        """Force redrawing"""
        self.Refresh(False) 

    def on_motion(self, event):
        """update attributes focus on mouse move in mode DELETE ELEMENT, ADD BEAM"""
        self.view_1.Mouse_position = event.GetPosition()
        pos_mouse = np.array([self.view_1.Mouse_position.x, self.view_1.Mouse_position.y])
        if self.EL.Mode == "DELETE_ELEMENT":
            for i in self.EL.nodes:
                pos_node = self.view_1.world_to_screen(i.x, i.y)
                d = np.linalg.norm(pos_node-pos_mouse)
                i.delta_1_focus = 0
                i.delta_2_focus = 0
                if d < 7:
                    i.focused = True
                    break
                else:
                    i.focused = False
            for i in self.EL.beams:
                N1 = self.EL.index_node(i.node_1)
                N2 = self.EL.index_node(i.node_2)
                Y1 = self.EL.periods[0]
                Y2 = self.EL.periods[1]
                Y1W = np.array([Y1.x, Y1.y])*Y1.length
                Y2W = np.array([Y2.x, Y2.y])*Y2.length

                N1_coord = np.array([N1.x, N1.y])
                N2_coord = np.array([N2.x+i.delta_1*Y1W[0]+i.delta_2*Y2W[0], N2.y+i.delta_1*Y1W[1]+i.delta_2*Y2W[1]])

                PS1 = self.view_1.world_to_screen(N1_coord[0], N1_coord[1])
                PS2 = self.view_1.world_to_screen(N2_coord[0], N2_coord[1])

                A = PS2-PS1
                B = pos_mouse-PS1
                L = np.linalg.norm(A)
                N = A/L
                H = np.dot(B, N)
                d = math.sqrt(np.linalg.norm(B)**2-H**2)
                if d < i.width*self.view_1.zoom and H > 10 and H < (L-10):
                    i.focused = True
                    break
                else:
                    i.focused = False

        if self.EL.Mode == "ADD_BEAM_P1":
            for i in self.EL.nodes:
                pos_node = self.view_1.world_to_screen(i.x, i.y)
                d = np.linalg.norm(pos_node-pos_mouse)
                i.delta_1_focus = 0
                i.delta_2_focus = 0
                if d < 7:
                    i.focused = True

                    break
                else:
                    i.focused = False

        if self.EL.Mode == "ADD_BEAM_P2":

            Y1W = np.array([self.EL.periods[0].x, self.EL.periods[0].y])*self.EL.periods[0].length
            Y2W = np.array([self.EL.periods[1].x, self.EL.periods[1].y])*self.EL.periods[1].length

            for i in self.EL.nodes:
                pos_node_iW = np.array([i.x, i.y])
                i.focused = False
                i.delta_1_focus = 0
                i.delta_2_focus = 0

                for delta_1 in range(-1, 2):
                    for delta_2 in range(-1, 2):
                        pos_node_W = pos_node_iW+delta_1*Y1W+delta_2*Y2W
                        pos_node_S = self.view_1.world_to_screen(pos_node_W[0], pos_node_W[1])
                        d = np.linalg.norm(pos_node_S-pos_mouse)
                        if d < 7:
                            if ((delta_1 == 0 and delta_2 == 0) and i.number != self.EL.P1_acquired.number) \
                                    or delta_1 != 0 or delta_2 != 0:
                                i.focused = True
                                i.delta_1_focus = delta_1
                                i.delta_2_focus = delta_2

        self.Refresh(False)
        event.Skip()

    def on_left_down(self, event):
        """Functions linked to left button according to current mode"""
        Pos_screen = event.GetPosition()

        Pos_world = self.view_1.screen_to_world(Pos_screen.x, Pos_screen.y)

        if self.EL.Mode == "DELETE_ELEMENT":
            for i in self.EL.nodes:
                if i.focused is True and len(self.EL.nodes) > 1:
                    numero = i.number
                    self.EL.nodes.remove(i)
                    self.Gd_pere.File_saved = False
                    Item1 = self.Gd_pere.Search_item_tree_ctrl_perso("Nodes", numero)
                    if Item1[0] == 1:
                        self.Gd_pere.tree_ctrl_1.Delete(Item1[1])
                    else:
                        print("Point not found in the tree")
                    for j in self.EL.beams:
                        if numero == j.node_1 or numero == j.node_2:
                            self.EL.beams.remove(j)
                            Item1 = self.Gd_pere.Search_item_tree_ctrl_perso("Beams", numero)
                            if Item1[0] == 1:
                                self.Gd_pere.tree_ctrl_1.Delete(Item1[1])
                            else:
                                print("Element not found in the tree")
            for i in self.EL.beams:
                if i.focused:
                    numero = i.number
                    self.EL.beams.remove(i)
                    self.Gd_pere.File_saved = False
                    Item1 = self.Gd_pere.Search_item_tree_ctrl_perso("Beams", numero)
                    if Item1[0] == 1:
                        self.Gd_pere.tree_ctrl_1.Delete(Item1[1])
                    else:
                        print("Element not found in the tree")
                    break

        if self.EL.Mode == "ADD_POINT":
            resultat = self.Gd_pere.Search_branch_tree_ctrl_perso("Nodes")
            print(resultat)
            if resultat[0] == -1:
                self.Gd_pere.Message_perso("Error: no branch of Node inputs", wx.ICON_ERROR)
            str1 = self.Gd_pere.tree_ctrl_1.GetItemText(resultat[2])
            str2 = str1.split(':')
            str3 = str2[0].split('.')
            numero = int(str3[1])
            numero = numero+1

            str_tree = "N.%i:(%5.2f,%5.2f)" % (numero, Pos_world[0], Pos_world[1])

            self.Gd_pere.tree_ctrl_1.AppendItem(resultat[1], str_tree)
            self.EL.nodes.append(node(Pos_world[0], Pos_world[1], 5, numero))
            self.Gd_pere.File_saved = False

        if self.EL.Mode == "ADD_BEAM_P1":
            for i in self.EL.nodes:
                if i.focused:
                    self.EL.P1_acquired = copy.deepcopy(i)
                    self.EL.Mode = "ADD_BEAM_P2"
                    i.focused = False
                    self.EL.P1_acquired_bool = True
                    break

        if self.EL.Mode == "ADD_BEAM_P2":
            for i in self.EL.nodes:
                if i.focused:
                    self.EL.Mode = "ADD_BEAM_P1"
                    resultat = self.Gd_pere.Search_branch_tree_ctrl_perso("Beams")
                    if resultat[0] == -1:
                        self.Gd_pere.Message_perso("Error: No branch of beam inputs", wx.ICON_ERROR)
                    if resultat[0] == 1:
                        str1 = self.Gd_pere.tree_ctrl_1.GetItemText(resultat[2])
                        str2 = str1.split(':')
                        str3 = str2[0].split('.')
                        str4 = str2[1].split(',')
                        numero = int(str3[1])
                        numero = numero+1
                    if resultat[0] == -2:
                        numero = 1
                        str4 = [0, 0, 0, 0, 0, 0.1]

                    str_tree = "beam.%i:(%i,%i),(%i,%i),rect,%5.2f" % (numero, self.EL.P1_acquired.number, i.number,
                                                                       i.delta_1_focus, i.delta_2_focus, float(str4[5]))

                    self.Gd_pere.tree_ctrl_1.AppendItem(resultat[1], str_tree)

                    self.EL.P1_acquired.focused = False
                    self.EL.P1_acquired_bool = False

                    resultat = self.Gd_pere.Search_branch_tree_ctrl_perso("Material")
                    if resultat[0] == -1:
                        self.Gd_pere.Message_perso("Error: no branch of material inputs", wx.ICON_ERROR)
                    str5 = self.Gd_pere.tree_ctrl_1.GetItemText(resultat[2])
                    str6 = str5.split(':')
                    str7 = str6[1].split(',')
                    self.EL.beams.append(beam(self.EL.P1_acquired.number, i.number, i.delta_1_focus, i.delta_2_focus,
                                              "rect", 0, float(str4[5]), 0, 0, 0, 0, float(str7[0]), numero))
                    self.EL.beams[len(self.EL.beams)-1].evaluate_k(self.EL)
                    self.Gd_pere.File_saved = False
                    break

        self.Refresh()
        event.Skip()

    def on_right_down(self, event):
        """Activation of additional translation vector"""
        Pos_screen = event.GetPosition()
        Pos_world = self.view_1.screen_to_world(Pos_screen.x, Pos_screen.y)
        self.view_1.translation_P1x = Pos_world[0]
        self.view_1.translation_P1y = Pos_world[1]

        self.view_1.translation_activate = True
        self.Refresh(False)
        event.Skip()

    def on_right_up(self, event):
        """Add current translation vector to general one"""
        Pos_screen = event.GetPosition()
        Pos_world = self.view_1.screen_to_world(Pos_screen.x, Pos_screen.y)
        self.view_1.translation_activate = False
        self.view_1.translation_x = self.view_1.translation_x+Pos_world[0]-self.view_1.translation_P1x
        self.view_1.translation_y = self.view_1.translation_y+Pos_world[1]-self.view_1.translation_P1y

        self.Refresh(False)
        event.Skip()

    def on_wheel(self, event):
        """Wheel mouse management of zoom """
        wheel = event.GetWheelRotation()
        Pos_mouse_screen = event.GetPosition()
        Pos_mouse_world = self.view_1.screen_to_world(Pos_mouse_screen.x, Pos_mouse_screen.y)
        if wheel > 0 and self.view_1.zoom < 1000:
            self.view_1.zoom = self.view_1.zoom*1.1

        if wheel < 0 and self.view_1.zoom > 1:
            self.view_1.zoom = self.view_1.zoom*0.9

        self.view_1.translation_x = (Pos_mouse_screen.x-Pos_mouse_world[0]*self.view_1.zoom)/self.view_1.zoom
        self.view_1.translation_y = (self.view_1.height-Pos_mouse_screen.y)/self.view_1.zoom-Pos_mouse_world[1]

        self.Refresh(False)
        event.Skip()

    def key_zoom(self, code_zoom):
        """Zoom in / out calculation according to code_zoom """
        Pos_mouse_screen = self.view_1.Mouse_position
        Pos_mouse_world = self.view_1.screen_to_world(Pos_mouse_screen.x, Pos_mouse_screen.y)

        if code_zoom == 1 and self.view_1.zoom < 1000:
            self.view_1.zoom = self.view_1.zoom*1.1

        if code_zoom == 2 and self.view_1.zoom > 1:
            self.view_1.zoom = self.view_1.zoom*0.9

        self.view_1.translation_x = (Pos_mouse_screen.x-Pos_mouse_world[0]*self.view_1.zoom)/self.view_1.zoom
        self.view_1.translation_y = (self.view_1.height-Pos_mouse_screen.y)/self.view_1.zoom-Pos_mouse_world[1]

        self.Refresh(False)

    def Get_world_pos(self):
        pos_world = self.view_1.screen_to_world(self.view_1.Mouse_position.x, self.view_1.Mouse_position.y)
        return pos_world


class MyFrame(wx.Frame):
    """Main window class (wx library) 

    frame_menubar: Menu bar definition
    frame_toolbar: icons tool for rapid access functions
    tree_ctrl_1 : browser of elements (embedded in window_1)
    panel_1: graphic window to show and interact with user(embedded in window_2) 
    grid_1: to modify attributes of elements (in panel_2 in window_2)
    button_2 : button ok
    button_3 : button cancel

    on_char(event): zoom in / out while char +/- is typed
    on_close(event): When window close
    Message_perso(msg_1,categorie): Show msg_1 associated win an icon category
    Set_grid_perso(col,row,labels_col,labels_row): Redraw grid and modify labels 
    __set_properties(): define initial properties of window elements (wx)
    __do_layout(): as its name (wx)
    File_open(event): menu file open
    File_save(event): menu file save
    File_save_as(event): menu file save as
    File_generate_txt(event): menu generate txt : 
        generate the text code file for topology lattice 
    File_close(event): menu file close
    Edit_delete(event): menu delete : enable delete mode
    Tools_add_point(event): menu tool activation mode add point
    Tools_add_beam(event):: menu tool activation mode add beam
    Icone_add_beam(event): icon tool activation mode add beam
    Icone_add_point(event): icon activation mode add point
    Icone_delete(sevent):icon activation mode delete
    Search_branch_tree_ctrl_perso(nom): Search in tree ctrl for branch "nom"
    Search_item_tree_ctrl_perso(nom,numero): Search an item in branch named "nom" 
                with identifier "numero"
    selection_item(event): Modify values in tree ctrl from grid
    """
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((1024, 700))
        self.Filename = ""
        self.Filename_defined = False
        self.File_saved = False
        # menu bar
        self.frame_menubar = wx.MenuBar()
        self.Fichier = wx.Menu()
        self.frame_menubar.Ouvrir = self.Fichier.Append(wx.ID_ANY, "Open", "")
        self.Bind(wx.EVT_MENU, self.File_open, id=self.frame_menubar.Ouvrir.GetId())
        self.frame_menubar.Enregistrer = self.Fichier.Append(wx.ID_ANY, "Save", "")
        self.Bind(wx.EVT_MENU, self.File_save, id=self.frame_menubar.Enregistrer.GetId())
        self.frame_menubar.Energister_sous = self.Fichier.Append(wx.ID_ANY, "Save as", "")
        self.Bind(wx.EVT_MENU, self.File_save_as, id=self.frame_menubar.Energister_sous.GetId())
        self.frame_menubar.Generation_TXT = self.Fichier.Append(wx.ID_ANY, "Generate .TXT", "")
        self.Bind(wx.EVT_MENU, self.File_generate_txt, id=self.frame_menubar.Generation_TXT.GetId())
        self.frame_menubar.Save_bmp = self.Fichier.Append(wx.ID_ANY, "Save .bmp", "")
        self.Bind(wx.EVT_MENU, self.File_save_bmp, id=self.frame_menubar.Save_bmp.GetId())
        self.frame_menubar.Fermer = self.Fichier.Append(wx.ID_ANY, "Close", "")
        self.Bind(wx.EVT_MENU, self.File_close, id=self.frame_menubar.Fermer.GetId())
        self.frame_menubar.Append(self.Fichier, "File")
        self.Edition = wx.Menu()
        self.frame_menubar.Supprimer = self.Edition.Append(wx.ID_ANY, "Delete", "")
        self.Bind(wx.EVT_MENU, self.Edit_delete, id=self.frame_menubar.Supprimer.GetId())
        self.frame_menubar.Append(self.Edition, "Edition")
        self.Calculs = wx.Menu()
        self.frame_menubar.Letsdoit = self.Calculs.Append(wx.ID_ANY, "Let's do it!", "")
        self.Bind(wx.EVT_MENU, self.Calculation_letsdoit, id=self.frame_menubar.Letsdoit.GetId())
        self.frame_menubar.Append(self.Calculs, "Calculations")
        self.Outils = wx.Menu()
        self.frame_menubar.Add_point = self.Outils.Append(wx.ID_ANY, "Add node", "")
        self.Bind(wx.EVT_MENU, self.Tools_add_point, id=self.frame_menubar.Add_point.GetId())
        self.frame_menubar.Add_beam = self.Outils.Append(wx.ID_ANY, "Add beam", "")
        self.Bind(wx.EVT_MENU, self.Tools_add_beam, id=self.frame_menubar.Add_beam.GetId())
        self.frame_menubar.Append(self.Outils, "Tools")
        self.SetMenuBar(self.frame_menubar)
        # Menu Bar end
        # Tool Bar
        self.frame_toolbar = wx.ToolBar(self, -1)
        self.SetToolBar(self.frame_toolbar)
        self.tool_1 = self.frame_toolbar.AddTool(wx.ID_ANY, "icone_plus_point", wx.Bitmap(gui_location + "/icone_plus_point.bmp", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "", "")
        self.tool_2 = self.frame_toolbar.AddTool(wx.ID_ANY, "icone_plus_poutre", wx.Bitmap(gui_location + "/icone_plus_poutre.bmp", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "", "")
        self.tool_3 = self.frame_toolbar.AddTool(wx.ID_ANY, "icone_moins", wx.Bitmap(gui_location + "/icone_moins.bmp", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "", "")
        self.Bind(wx.EVT_TOOL, self.Icone_add_point, self.tool_1)
        self.Bind(wx.EVT_TOOL, self.Icone_add_beam, self.tool_2)
        self.Bind(wx.EVT_TOOL, self.Icone_delete, self.tool_3)
        # Tool Bar end
        # windows
        self.panel_3 = wx.Panel(self, wx.ID_ANY)
        self.panel_4 = wx.Panel(self, wx.ID_ANY)
        # self.multiLabel = wx.StaticText(self.panel_4, -1, "Multi-line")
        self.multiText = wx.TextCtrl(self.panel_4, -1, "", size=(200, 150), style=wx.TE_MULTILINE | wx.TE_READONLY)
        font_1 = wx.Font(pointSize=12, family=wx.FONTFAMILY_MODERN, style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL)
        self.multiText.SetFont(font_1)
        self.multiText.write("Init\n")

        self.window_1 = wx.SplitterWindow(self, wx.ID_ANY)
        self.tree_ctrl_1 = wx.TreeCtrl(self.window_1, wx.ID_ANY)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.selection_item, self.tree_ctrl_1)
        self.window_2 = wx.SplitterWindow(self.window_1, wx.ID_ANY, style=0)
        self.EL = elements()
        self.panel_1 = Graph_window(self.window_2, self, self.EL)
        self.panel_2 = wx.Panel(self.window_2, wx.ID_ANY, style=wx.BORDER_SIMPLE)
        self.grid_1 = wx.grid.Grid(self.panel_2, wx.ID_ANY, size=(1, 1))
        self.Bind(wx.grid.EVT_GRID_CMD_CELL_CHANGED, self.cell_changed, self.grid_1)
        self.Bind(wx.grid.EVT_GRID_CMD_SELECT_CELL, self.selection_cell, self.grid_1)
        self.button_2 = wx.Button(self.panel_2, wx.ID_ANY, "Ok")
        self.button_3 = wx.Button(self.panel_2, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.Bouton_ok, self.button_2)
        self.Bind(wx.EVT_BUTTON, self.Bouton_annuler, self.button_3)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char)

        # windows end
        # properties and layout
        self.__set_properties()
        self.__do_layout()

    def on_char(self, event):
        """zoom in / out while char +/- is typed"""
        key = event.GetKeyCode()
        ctrl = event.ControlDown()
        if (key == 388 or key == 61) and ctrl == 1:
            self.panel_1.key_zoom(1)

        if (key == 390 or key == 54) and ctrl == 1:
            self.panel_1.key_zoom(2)
        event.Skip()

    def on_close(self, event):
        """When window close"""
        self.Destroy()

    def Message_perso(self, msg_1, categorie):
        """Show msg_1 associated win an icon category"""
        # categorie = wx.ICON_ERROR ou wx.ICON_WARNING ou wx.ICON_INFORMATION
        msg = wx.MessageDialog(None, message=msg_1, style=wx.OK | categorie)
        msg.ShowModal()
        msg.Destroy()

    def Set_grid_perso(self, col, row, labels_col, labels_row):
        """Set_grid_perso(self,col,row,labels_col,labels_row)"""
        Number_cols = self.grid_1.GetNumberCols()
        Number_rows = self.grid_1.GetNumberRows()
        if Number_cols > col:
            self.grid_1.DeleteCols(col, Number_cols-col)
        if Number_cols < col:
            self.grid_1.AppendCols(col-Number_cols)
        if Number_rows > row:
            self.grid_1.DeleteRows(row, Number_rows-row)
        if Number_rows < row:
            self.grid_1.AppendRows(row-Number_rows)
        for i in range(col):
            self.grid_1.SetColLabelValue(i, labels_col[i])
        for i in range(row):
            self.grid_1.SetRowLabelValue(i, labels_row)

    def __set_properties(self):
        """define initial properties of window elements (wx)"""
        self.SetTitle("Homogenenization lattice")
        self.frame_toolbar.Realize()
        self.grid_1.CreateGrid(10, 3)
        self.grid_1.SetColLabelValue(0, "X")
        self.grid_1.SetColLabelValue(1, "Y")
        self.grid_1.SetColLabelValue(2, "Z")
        self.window_2.SetMinimumPaneSize(20)
        self.window_1.SetMinimumPaneSize(20)
        Tree_Lattice_Id = self.tree_ctrl_1.AddRoot("Lattice")
        materialId = self.tree_ctrl_1.AppendItem(Tree_Lattice_Id, "Material:")
        basisId = self.tree_ctrl_1.AppendItem(Tree_Lattice_Id, "Basis:")
        NodesId = self.tree_ctrl_1.AppendItem(Tree_Lattice_Id, "Nodes:")
        beamsId = self.tree_ctrl_1.AppendItem(Tree_Lattice_Id, "Beams:")
        self.tree_ctrl_1.AppendItem(basisId, "Y.1:(1,0)")
        self.tree_ctrl_1.AppendItem(basisId, "Y.2:(0,1)")
        self.tree_ctrl_1.AppendItem(NodesId, "N.1:(0,0)")

        self.tree_ctrl_1.AppendItem(materialId, "modulus(GPa):210")

        self.tree_ctrl_1.ExpandAll()
        self.Set_grid_perso(2, 1, ["Y.1", "Y.2"], "1")
        self.grid_1.SetCellValue(0, 0, "1")
        self.grid_1.SetCellValue(0, 1, "0")
        self.EL.periods.append(periodicity(1, 0, 1, 1))
        self.EL.periods.append(periodicity(0, 1, 1, 2))
        self.EL.nodes.append(node(0, 0, 5, 1))

    def __do_layout(self):
        """as its name (wx)"""
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        self.panel_3.SetSizer(sizer_3)
        self.panel_4.SetSizer(sizer_5)
        sizer_1.Add(self.panel_3, 0, 0, 0)
        sizer_2.Add(self.grid_1, 1, wx.ALIGN_BOTTOM | wx.ALL | wx.EXPAND, 1)
        sizer_4.Add(self.button_2, 1, wx.ALIGN_BOTTOM | wx.ALL, 1)
        sizer_4.Add(self.button_3, 1, wx.ALIGN_BOTTOM | wx.ALL, 1)
        sizer_5.Add(self.multiText, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_4, 0, wx.ALL, 0)
        self.panel_2.SetSizer(sizer_2)
        self.window_2.SplitHorizontally(self.panel_1, self.panel_2)
        self.window_1.SplitVertically(self.tree_ctrl_1, self.window_2)
        sizer_1.Add(self.window_1, 1, wx.EXPAND, 0)
        sizer_1.Add(self.panel_4, 0, wx.EXPAND, 1)
        self.SetSizer(sizer_1)
        self.Layout()
        self.panel_1.Refresh(False)

    def Open_file(self):
        Material_E = 0
        """Open the xml file -> create tree ctrl and elements""" 
        if not self.File_saved:
            if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm", wx.ICON_QUESTION | wx.YES_NO, self) == wx.YES:
                self.Save_file()

        with wx.FileDialog(self, "Open XML file", wildcard="xml files (*.xml)|*.xml", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            self.Filename = fileDialog.GetPath()
            try:
                myfile = open(self.Filename, 'r')
            except IOError:
                wx.LogError("Cannot open file '%s'." % self.Filename)
                return -1
        try:
            tree = ET.parse(myfile)
        except Exception as exc:
            self.Message_perso("Unable to parse file ({})".format(str(exc)), wx.ICON_ERROR)
            myfile.close()
            return
        root = tree.getroot()
        self.tree_ctrl_1.DeleteAllItems()
        self.EL = elements()
        Item1 = self.tree_ctrl_1.AddRoot(root.text)
        for child1 in root:
            Item2 = self.tree_ctrl_1.AppendItem(Item1, child1.text)
            for child2 in child1:
                self.tree_ctrl_1.AppendItem(Item2, child2.text)
                str0 = child2.text
                str0 = str0.replace('(', '').replace(')', '')
                str1 = str0.split(':')
                str10 = str1[0].split('.')
                str11 = str1[1].split(',')

                if str10[0] == "modulus(GPa)":
                    Material_E = float(str11[0])
                if str10[0] == "Y":
                    x = float(str11[0])
                    y = float(str11[1])
                    vect = np.array([x, y])
                    vect1 = normalize_vector(vect)
                    L = np.linalg.norm(vect)
                    self.EL.periods.append(periodicity(vect1[0], vect1[1], L, int(str10[1])))
                if str10[0] == "N":
                    x = float(str11[0])
                    y = float(str11[1])
                    self.EL.nodes.append(node(x, y, 5, int(str10[1])))
                if str10[0] == "beam":
                    node_1 = int(str11[0])
                    node_2 = int(str11[1])
                    delta_1 = int(str11[2])
                    delta_2 = int(str11[3])
                    width = float(str11[5])
                    number = int(str10[1])
                    self.EL.beams.append(beam(node_1, node_2, delta_1, delta_2, str11[4], 0, width, 0, 0, 0, 0, Material_E, number))
                    a = self.EL.beams[len(self.EL.beams)-1]
                    a.evaluate_k(self.EL)
        self.tree_ctrl_1.ExpandAll()
        self.panel_1.reassign_EL(self.EL)
        self.File_saved = True
        self.Filename_defined = True
        myfile.close()

    def File_open(self, event):  # from menu
        """menu file open"""
        self.Open_file()
        event.Skip()

    def Define_filename(self):
        with wx.FileDialog(self, "Save XML file", wildcard="xml files (*.xml)|*.xml", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return ""

            # save the current contents in the file
            file = fileDialog.GetPath()
            self.Filename_defined = True
            self.Filename = file
            return file

    def Save_file(self):
        """Save the current project in xml"""
        if not self.Filename_defined:
            file = self.Define_filename()
            if file == "":
                return -1
            else:
                self.Filesaved = True
        else:
            file = self.Filename
        tree_root = self.tree_ctrl_1.GetRootItem()
        str1 = self.tree_ctrl_1.GetItemText(tree_root)
        xml_root = ET.Element("root")
        xml_root.text = str1
        item_child1 = self.tree_ctrl_1.GetFirstChild(tree_root)
        while True:
            xml_child1 = ET.SubElement(xml_root, "child1")
            str1 = self.tree_ctrl_1.GetItemText(item_child1[0])
            xml_child1.text = str1
            item_child2 = self.tree_ctrl_1.GetFirstChild(item_child1[0])
            if item_child2[0].IsOk():
                while True:
                    str1 = self.tree_ctrl_1.GetItemText(item_child2[0])
                    xml_child2 = ET.SubElement(xml_child1, "child2")
                    xml_child2.text = str1
                    item_child2 = self.tree_ctrl_1.GetNextChild(item_child2[0], item_child2[1])
                    if not(item_child2[0].IsOk()):
                        break
            item_child1 = self.tree_ctrl_1.GetNextChild(item_child1[0], item_child1[1])
            if not(item_child1[0].IsOk()):
                break
        mydata = ET.tostring(xml_root, encoding='unicode', method='xml')
        try:
            myfile = open(file, 'w')
            myfile.write(mydata)
            myfile.close()
        except IOError:
            self.Message_perso("IOError", wx.ICON_ERROR)
        self.File_saved = True

    def File_save(self, event):
        """menu file save"""
        self.Save_file()
        event.Skip()

    def File_save_as(self, event):
        """menu file save as"""
        self.Define_filename()
        self.Save_file()
        event.Skip()

    def Generate_json(self, file):
        myfile = open(file, "w+")
        myfile.write("{\n")
        # Write number of elements
        myfile.write("\"comment1\": \"Define the number of elements\",\n")
        Number_beams = len(self.EL.beams)
        if Number_beams < 1:
            self.Message_perso("Error:There's no beam", wx.ICON_ERROR)
            myfile.close()
            return -1
        myfile.write("\"NumberElements\": %i,\n" % Number_beams)
        # Write the direction vectors of each element
        myfile.write("\"comment2\": \"Define the direction vectors of each element\",\n")
        for i in self.EL.beams:
            myfile.write("\"e_%i\":[%6.4f,%6.4f],\n" % (i.number, i.e_x, i.e_y))
        # Write basis periodicity vectors
        myfile.write("\"comment3\": \"define the global periodicity vectors\",\n")
        for i in self.EL.periods:
            myfile.write("\"Y_%i\":[%6.4f,%6.4f],\n" % (i.number, i.x, i.y))
        # Write number node
        myfile.write("\"comment4\": \"number of inner nodes\",\n")
        Number_nodes = len(self.EL.nodes)
        myfile.write("\"NumberNodes\": %i,\n" % Number_nodes)
        # Write List of origin and end points along with delta
        myfile.write("\"comment5\": \"List of origin and end points along with delta\",\n")
        str_Ob = "\"Ob\": ["
        str_Eb = "\"Eb\": ["
        str_Delta1 = "\"Delta1\": ["
        str_Delta2 = "\"Delta2\": ["
        for i in self.EL.beams:
            str_Ob = str_Ob+str(i.node_1)+','
            str_Eb = str_Eb+str(i.node_2)+','
            str_Delta1 = str_Delta1+str(i.delta_1)+','
            str_Delta2 = str_Delta2+str(i.delta_2)+','
        str_Ob = str_Ob[0:len(str_Ob)-1]+"],\n"
        str_Eb = str_Eb[0:len(str_Eb)-1]+"],\n"
        str_Delta1 = str_Delta1[0:len(str_Delta1)-1]+"],\n"
        str_Delta2 = str_Delta2[0:len(str_Delta2)-1]+"],\n"
        myfile.write(str_Ob)
        myfile.write(str_Eb)
        myfile.write(str_Delta1)
        myfile.write(str_Delta2)
        # Write list of element axial and bending stiffness
        myfile.write("\"commentt6\": \"List of element axial and bending stiffness\",\n")
        str_Ka = "\"Ka\": ["
        str_Kb = "\"Kb\": ["
        for i in self.EL.beams:
            str_Ka = str_Ka+str(i.ka)+','
            str_Kb = str_Kb+str(i.kb)+','
        str_Ka = str_Ka[0:len(str_Ka)-1]+"],\n"
        str_Kb = str_Kb[0:len(str_Kb)-1]+"],\n"
        myfile.write(str_Ka)
        myfile.write(str_Kb)
        # Write list of element lengths and volumes
        myfile.write("\"comment7\": \"List of element lengths and volumes\",\n")
        str_Lb = "\"Lb\": ["
        str_tb = "\"tb\": ["
        for i in self.EL.beams:
            str_Lb = str_Lb+str(i.length)+','
            str_tb = str_tb+str(i.width)+','
        str_Lb = str_Lb[0:len(str_Lb)-1]+"],\n"
        str_tb = str_tb[0:len(str_tb)-1]+"],\n"
        myfile.write(str_Lb)
        myfile.write(str_tb)
        # Write norme of the periodicity vectors
        myfile.write("\"comment8\": \"Norme of the periodicity vectors\",\n")
        str1 = ""
        for i in self.EL.periods:
            str1 = str1+"\"L%i\":%6.4f,\n" % (i.number, i.length)
        str1 = str1[0:len(str1)-2]+"\n"
        myfile.write(str1)
        myfile.write("}\n")
        myfile.close()
        return 0

    def Generate_txt(self, file):
        myfile = open(file, "w+")
        # Write number of elements
        myfile.write("# Define the number of elements\n")
        Number_beams = len(self.EL.beams)
        if Number_beams < 1:
            self.Message_perso("Error:There's no beam", wx.ICON_ERROR)
            myfile.close()
            return -1
        myfile.write("NumberElements= %i\n" % Number_beams)
        # Write the direction vectors of each element
        myfile.write("# Define the direction vectors of each element\n")
        for i in self.EL.beams:
            myfile.write("e_%i=[%6.4f,%6.4f]\n" % (i.number, i.e_x, i.e_y))
        # Write basis periodicity vectors
        myfile.write("# define the global periodicity vectors\n")
        for i in self.EL.periods:
            myfile.write("Y_%i=[%6.4f,%6.4f]\n" % (i.number, i.x, i.y))
        # Write number node
        myfile.write("# number of inner nodes\n")
        Number_nodes = len(self.EL.nodes)
        myfile.write("NumberNodes= %i\n" % Number_nodes)
        # Write List of origin and end points along with delta
        myfile.write("# List of origin and end points along with delta\n")
        str_Ob = "Ob = ["
        str_Eb = "Eb = ["
        str_Delta1 = "Delta1 = ["
        str_Delta2 = "Delta2 = ["
        for i in self.EL.beams:
            str_Ob = str_Ob+str(i.node_1)+','
            str_Eb = str_Eb+str(i.node_2)+','
            str_Delta1 = str_Delta1+str(i.delta_1)+','
            str_Delta2 = str_Delta2+str(i.delta_2)+','
        str_Ob = str_Ob[0:len(str_Ob)-1]+"]\n"
        str_Eb = str_Eb[0:len(str_Eb)-1]+"]\n"
        str_Delta1 = str_Delta1[0:len(str_Delta1)-1]+"]\n"
        str_Delta2 = str_Delta2[0:len(str_Delta2)-1]+"]\n"
        myfile.write(str_Ob)
        myfile.write(str_Eb)
        myfile.write(str_Delta1)
        myfile.write(str_Delta2)
        # Write list of element axial and bending stiffness
        myfile.write("# List of element axial and bending stiffness\n")
        str_Ka = "Ka=["
        str_Kb = "Kb=["
        for i in self.EL.beams:
            str_Ka = str_Ka+str(i.ka)+','
            str_Kb = str_Kb+str(i.kb)+','
        str_Ka = str_Ka[0:len(str_Ka)-1]+"]\n"
        str_Kb = str_Kb[0:len(str_Kb)-1]+"]\n"
        myfile.write(str_Ka)
        myfile.write(str_Kb)
        # Write list of element lengths and volumes
        myfile.write("# List of element lengths and volumes\n")
        str_Lb = "Lb=["
        str_tb = "tb=["
        for i in self.EL.beams:
            str_Lb = str_Lb+str(i.length)+','
            str_tb = str_tb+str(i.width)+','
        str_Lb = str_Lb[0:len(str_Lb)-1]+"]\n"
        str_tb = str_tb[0:len(str_tb)-1]+"]\n"
        myfile.write(str_Lb)
        myfile.write(str_tb)
        # Write norme of the periodicity vectors
        myfile.write("# Norme of the periodicity vectors\n")
        for i in self.EL.periods:
            myfile.write("L%i=%6.4f\n" % (i.number, i.length))
        myfile.close()
        return 0

    def File_generate_txt(self, event):
        """File_generate_txt(event): menu generate txt :
        generate the text code file for topology lattice """
        with wx.FileDialog(self, "Save data txt file", wildcard="txt files (*.txt)|*.txt",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return -1
                # event.Skip()

            # save the current contents in the file
            file = fileDialog.GetPath()
        self.Generate_txt(file)
        event.Skip()

    def File_save_bmp(self, event):
        self.panel_1.save_bmp()
        self.panel_1.GetCapture()
        event.Skip()

    def File_close(self, event):  
        """menu file close"""
        exit(0)
        event.Skip()

    def Edit_delete(self, event):
        """menu delete : enable delete mode"""
        self.EL.Mode = "DELETE_ELEMENT"
        self.panel_1.Refresh(False)
        event.Skip()

    def Calculations(self, writer):
        """Call calculations modules"""
        solver = Solver()
        try:
            with open("input_data.json", 'r') as f:
                data = json.load(f)
        except IOError as error:
            self.Message_perso("could not open input file input_data.json", wx.ICON_ERROR)

        solver.solve(data)

        # Write to file

        writer.WriteTensorsToFile(None, solver.CMatTensor, solver.FlexMatTensor)
        writer.WriteEffectivePropertiesToFile(solver.Bulk, solver.Ex, solver.Ey, solver.Poissonyx, solver.Poissonxy, solver.G, solver.rho)
        writer.PlotEffectiveProperties(solver.Bulk, solver.Ex, solver.Ey, solver.Poissonyx, solver.Poissonxy, solver.G)

    def Calculation_letsdoit(self, event):
        """Calculations Go"""
        self.Generate_json("input_data.json")
        self.multiText.Clear()
        try:
            writer = Writer()
            self.Calculations(writer)
            path = writer.folder
            self.multiText.write("Path of results files : "+str(path)+"\n")
            result_file = open(path+"/CMatrix.txt", "r")
            self.multiText.write("Stiffness Matrix:\n")
            self.multiText.write(result_file.read())
            result_file.close()
            Eff_file = open(path+"/EffectProperties.txt", "r")
            self.multiText.write("Effective properties:\n")
            self.multiText.write(Eff_file.read())
            Eff_file.close()
            Flex_file = open(path+"/FlexMatrix.txt", "r")
            self.multiText.write("Flexibility Matrix:\n")
            self.multiText.write(Flex_file.read())
            Eff_file.close()
        except Exception as exc:
            self.multiText.write("Something wrong! Unable to do calculations {}\n".format(str(exc)))
        event.Skip()

    def Tools_add_point(self, event):
        """menu tool activation mode add point"""
        self.EL.Mode = "ADD_POINT"
        event.Skip()

    def Tools_add_beam(self, event):
        """menu tool activation mode add beam"""
        self.EL.Mode = "ADD_BEAM_P1"
        event.Skip()

    def Icone_add_beam(self, event):
        self.EL.Mode = "ADD_BEAM_P1"
        event.Skip()

    def Icone_add_point(self, event):
        """icon activation mode add point"""
        self.EL.Mode = "ADD_POINT"
        self.panel_1.Refresh(False)
        event.Skip()

    def Icone_delete(self, event):
        """icon activation mode delete"""
        self.EL.Mode = "DELETE_ELEMENT"
        self.panel_1.Refresh(False)
        event.Skip()

    def Search_branch_tree_ctrl_perso(self, nom):
        """Search in tree ctrl for branch "nom"
        return -1,0,0 if no branch "nom" is found
        return -2,item branch,0 if branch "nom" is found without child
        return 1, item branch, item last child if branch "nom" is found and have childs
        """
        item1 = self.tree_ctrl_1.GetRootItem()
        item2 = self.tree_ctrl_1.GetFirstChild(item1)
        f = True
        while f:
            str1 = self.tree_ctrl_1.GetItemText(item2[0])
            str2 = str1.replace(':', '')
            if str2 == nom:
                break
            item2 = self.tree_ctrl_1.GetNextChild(item2[0], item2[1])
            f = item2[0].IsOk()
            if f is False:
                return -1, 0, 0
        item3 = self.tree_ctrl_1.GetFirstChild(item2[0])
        f = item3[0].IsOk()
        if f is False:
            return -2, item2[0], 0
        while f:
            item4 = self.tree_ctrl_1.GetNextChild(item3[0], item3[1])
            f = item4[0].IsOk()
            if f is False:
                break 
            item3 = item4
        return 1, item2[0], item3[0]

    def Search_item_tree_ctrl_perso(self, nom, numero):
        """    Search_item_tree_ctrl_perso(nom,numero): Search an item in child named "nom" 
                with identifier "numero"

                "nom" must be 'Nodes' for node, 'Basis' for periodicity vector, 'Beams' for beam
                return -1,0 if the branch with name "nom" not found 
                            or if none child have identifier "numero"
                return -2,0 if there's no child in branch
                return 1, item if item found
                """
        item1 = self.tree_ctrl_1.GetRootItem()

        item2 = self.tree_ctrl_1.GetFirstChild(item1)
        str1 = self.tree_ctrl_1.GetItemText(item2[0])
        f = True
        while f:
            str2 = str1.replace(':', '')
            if str2 == nom:
                break
            item2 = self.tree_ctrl_1.GetNextChild(item2[0], item2[1])
            f = item2[0].IsOk()
            if f is False:
                return -1, 0
            str1 = self.tree_ctrl_1.GetItemText(item2[0])

        item2 = self.tree_ctrl_1.GetFirstChild(item2[0])
        f = item2[0].IsOk()
        if f is False:
            return -2, 0
        f = True
        while f:
            str1 = self.tree_ctrl_1.GetItemText(item2[0])
            str2 = str1.split(':')
            str3 = str2[0].split('.')
            if int(str3[1]) == numero:
                return 1, item2[0]
            item2 = self.tree_ctrl_1.GetNextChild(item2[0], item2[1])
            f = item2[0].IsOk()
            if f is False:
                break
        return -1, 0

    def selection_item(self, event):
        """Copy values of item in tree ctrl to grid"""
        item_1 = event.Item
        str_2 = self.tree_ctrl_1.GetItemText(item_1)
        str_3 = str_2.split(':')
        str_4 = str_3[0].split('.')

        if str_4[0] == "modulus(GPa)":
            self.Set_grid_perso(1, 1, ["Elastic"], "modulus(GPa)")
            str_5 = str_3[1].split(',')
            self.grid_1.SetCellValue(0, 0, str_5[0])

        if str_4[0].strip() == "Y":
            self.Set_grid_perso(2, 1, ["Y. .X", "Y. .Y"], str_4[1])
            str_5 = str_3[1].split(',')
            str_5[0] = str_5[0].replace('(', '').replace(')', '')
            str_5[1] = str_5[1].replace('(', '').replace(')', '')
            self.grid_1.SetCellValue(0, 0, str_5[0])
            self.grid_1.SetCellValue(0, 1, str_5[1])

        if str_4[0].strip() == "N":
            self.Set_grid_perso(2, 1, ["N. .X", "N. .Y"], str_4[1])
            str_5 = str_3[1].split(',')
            str_5[0] = str_5[0].replace('(', '').replace(')', '')
            str_5[1] = str_5[1].replace('(', '').replace(')', '')
            self.grid_1.SetCellValue(0, 0, str_5[0])
            self.grid_1.SetCellValue(0, 1, str_5[1])

        if str_4[0].strip() == "beam":
            self.Set_grid_perso(6, 1, ["beam. .Node 1", "beam. .node 2", "delta 1", "delta 2", "Section type", "Section dim."], str_4[1])
            str_5 = str_3[1].split(',')
            str_5[0] = str_5[0].replace('(', '').replace(')', '')
            str_5[1] = str_5[1].replace('(', '').replace(')', '')
            self.grid_1.SetCellValue(0, 0, str_5[0])
            self.grid_1.SetCellValue(0, 1, str_5[1])
            str_5[2] = str_5[2].replace('(', '').replace(')', '')
            str_5[3] = str_5[3].replace('(', '').replace(')', '')
            self.grid_1.SetCellValue(0, 2, str_5[2])
            self.grid_1.SetCellValue(0, 3, str_5[3])
            self.grid_1.SetCellValue(0, 4, str_5[4])
            self.grid_1.SetCellValue(0, 5, str_5[5])
        event.Skip()

    def selection_cell(self, event):
        event.Skip()

    def cell_changed(self, event):
        event.Skip()

    def Bouton_ok(self, event):
        """Modify values in tree ctrl from grid"""
        self.File_saved = False
        str1 = self.grid_1.GetColLabelValue(0)
        str2 = str1.split('.')
        RowLabel = self.grid_1.GetRowLabelValue(0)
        if RowLabel == "modulus(GPa)":
            str3 = "Material"
            val1 = self.grid_1.GetCellValue(0, 0)
            str_tree = "modulus(GPa):"+str(val1)
            resultat = self.Search_branch_tree_ctrl_perso(str3)
            if resultat[0] == 1:
                self.tree_ctrl_1.SetItemText(resultat[2], str_tree)
            else:
                self.Message_perso("None entry found in tree ctrl", wx.ICON_ERROR)
        else:
            numero = int(self.grid_1.GetRowLabelValue(0))
            if str2[0] == "N":
                str3 = "Nodes"
                val1 = self.grid_1.GetCellValue(0, 0)
                val2 = self.grid_1.GetCellValue(0, 1)
                str_tree = 'N'+'.'+str(numero)+':'+'('+val1+','+val2+')'
                f = 0
                for i in self.EL.nodes:
                    if i.number == numero:
                        i.x = float(val1)
                        i.y = float(val2)
                        f = 1
                        break
                if f == 0:
                    print("node not found")
            if str2[0] == "Y":
                str3 = "Basis"
                val1 = self.grid_1.GetCellValue(0, 0)
                val2 = self.grid_1.GetCellValue(0, 1)
                str_tree = 'Y'+'.'+str(numero)+':'+'('+val1+','+val2+')'
                f = 0
                for i in self.EL.periods:
                    if i.number == numero:
                        vect = np.array([float(val1), float(val2)])
                        i.length = np.linalg.norm(vect)
                        vect2 = normalize_vector(vect)
                        i.x = vect2[0]
                        i.y = vect2[1]
                        f = 1
                        break
                if f == 0:
                    print("period vector not found")

            if str2[0] == "beam":
                str3 = "Beams"
                val1 = self.grid_1.GetCellValue(0, 0)
                val2 = self.grid_1.GetCellValue(0, 1)
                val3 = self.grid_1.GetCellValue(0, 2)
                val4 = self.grid_1.GetCellValue(0, 3)
                val5 = self.grid_1.GetCellValue(0, 4)
                val6 = self.grid_1.GetCellValue(0, 5)
                str_tree = 'beam'+'.'+str(numero)+':'+'('+val1+','+val2+')'+',('+val3+','+val4+')'+','+val5+','+val6
                f = 0
                for i in self.EL.beams:
                    if i.number == numero:
                        i.node_1 = int(val1)
                        i.node_2 = int(val2)
                        i.delta_1 = int(val3)
                        i.delta_2 = int(val4)
                        i.section = val5
                        i.width = float(val6)
                        i.evaluate_k(self.EL)
                        f = 1
                        break
                if f == 0:
                    print("period vector not found")

            resultat = self.Search_item_tree_ctrl_perso(str3, numero)
            if resultat[0] == 1:
                self.tree_ctrl_1.SetItemText(resultat[1], str_tree)
            else:
                self.Message_perso("None entry found in tree ctrl", wx.ICON_ERROR)

        self.panel_1.Refresh()
        event.Skip()

    def Bouton_annuler(self, event):
        event.Skip()


class Hom_lattice_8(wx.App):
    def OnInit(self):
        self.GUI = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.GUI)
        self.GUI.Show()
        return True


if __name__ == "__main__":
    app = Hom_lattice_8(0)
    app.MainLoop()
