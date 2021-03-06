#!/usr/bin/python
"""
@Author Robert Powell

Anything that the tree needs to know about the GUI should happen here
"""
from Tkinter import *
from ttk import *
import os

def edit_external_file(module_name):
    """ Open system editor on file """

    # TODO Consider relative paths + windows version
    #os.system("open "+module_name+'.clif')
    print 'Will eventually open', module_name

class Visualizer(object):
    """ Create the link between the VisualAborist and GUI """

    def __init__(self, canvas, notebook):

        self.canvas = canvas
        self.notebook = notebook
        self.tabs = {}


    def create_tab(self, node):
        """ Create node tab in GUI notebook """

        if node.name not in self.tabs:
            node_tab = Frame(self.notebook)
            node_scrollbar = Scrollbar(node_tab)
            node_scrollbar.pack(side=RIGHT, fill=Y)

            self.notebook.add(node_tab, text=node.name)
            self.tabs[node.name] = node_tab
            self.fill_node_tab(node_tab, node)
        else:
            tab = self.tabs[node.name]
            self.notebook.add(tab, text=node.name)

    def fill_node_tab(self, node_tab, node):
        """ Extract info about a node """

        node_info = Text(node_tab, wrap=WORD)
        node_info.tag_add("justified", "1.0", "end")
        node_info.tag_config("justified", justify=LEFT)
        node_info.insert(END, "", 'justified')
        node_info.pack(fill=BOTH, expand=1)

        hyperlink = HyperLink(node_info)

        node_info.insert(INSERT, 'Name: ')
        node_info.insert(INSERT, node.name + '\n', \
                hyperlink.add(lambda:edit_external_file(node.name)))
        node_info.insert(INSERT, 'Depth: ' + str(node.depth) + '\n')
        node_info.insert(INSERT, 'Parent: ' + node.visual_parent.name + '\n')
        node_info.insert(INSERT, '\n\n')

        node_info.insert(INSERT, 'All Parents: ')

        for parent in node.parents:
            node_info.insert(INSERT, parent.name, \
                             hyperlink.add(edit_external_file))
            node_info.insert(INSERT, ' ')

        node_info.insert(INSERT, '\n')

class HyperLink(object):
    """ Hyperlinks in TKinter! """

    def __init__(self, text):
        """ Create a text widget with hyperlink functionality """

        self.text = text
        self.text.tag_config('hyper', foreground='blue', underline=1)
        self.text.tag_bind('hyper', '<Enter>', self._enter)
        self.text.tag_bind('hyper', '<Leave>', self._leave)
        self.text.tag_bind('hyper', '<Button-1>', self._click)
        self.links = {}

    def reset(self):
        """ Clear all internal links """

        self.links = {}

    def add(self, action):
        """ Add action to link text """

        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return 'hyper', tag

    def _enter(self, event):
        """ Change mouse cursor on hover """

        self.text.config(cursor='hand2')

    def _leave(self, event):
        """ Restore normal cursor on leave """

        self.text.config(cursor='')

    def _click(self, event):
        """ Execute link action if clicked """

        for tag in self.text.tag_names(CURRENT):
            if tag[:6] == 'hyper-':
                self.links[tag]()
                return
