#!/usr/bin/python
# -*- coding: iso-8859-1 -*- 

import wx
#import wx.lib.mixins.listctrl
import wx.lib.mixins.listctrl  as  listmix
#from wx.lib.mixins.listctrl import *
import wx.aui

#import logging
#logger = logging.getLogger('myapp')
#hdlr = logging.FileHandler('var/myapp.log')
#formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
#hdlr.setFormatter(formatter)
#logger.addHandler(hdlr)
#logger.setLevel(logging.INFO)
#logger.info('a log message')


import os
import time

ID_BUTTON=100
ID_EXIT=200
ID_SPLITTER=300

import TreeSystem
import FileSystem

class MyListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent, id, monFileSystem):

        wx.ListCtrl.__init__(self, 
                                     parent, # parent
                                     id, # identifiant
                                         style=wx.LC_REPORT # une liste détaillée
                                         | wx.LC_VIRTUAL
                                         | wx.LC_HRULES | wx.LC_VRULES # règle de tri
                                         ##| wx.BORDER_SUNKEN
                                         ##| wx.BORDER_NONE # sans bord
                                         ##| wx.LC_EDIT_LABELS # edition du label possible
                                         #| wx.LC_SORT_ASCENDING # cette option pose des problèmes !
                                         ##| wx.LC_NO_HEADER
                                         ##| wx.LC_VRULES
                                         ##| wx.LC_HRULES
                                         ##| wx.LC_SINGLE_SEL
                                         )

                # récupération des images pour le rendu de l'appli
                ##files = os.listdir('.')
                #images = ['images/empty.png', 'images/folder.png', 'images/source_py.png', 
                #       'images/image.png', 'images/pdf.png', 'images/up16.png']
                #images = ['images/folder.png', 'images/folder.png', 'images/folder.png', 
                #       'images/folder.png', 'images/folder.png', 'images/folder.png']

                # Mise en place des colonnes
        self.InsertColumn(0, 'Name')
        self.InsertColumn(1, 'Ext')
        self.InsertColumn(2, 'Size', wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(3, 'Modified')
        self.InsertColumn(4, 'Type')

        # Configuration des colonnes
        self.SetColumnWidth(0, 220)
        self.SetColumnWidth(1, 80) #wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, 80) #wx.LIST_AUTOSIZE)
        self.SetColumnWidth(3, 80) #wx.LIST_AUTOSIZE)
        #self.SetColumnWidth(4, wx.LIST_AUTOSIZE)

        self.il = wx.ImageList(16, 16)
        #for i in images:
        #    self.il.Add(wx.Bitmap(i))

        fldridx       = self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,       wx.ART_OTHER, (16,16) ))
        fldropenidx   = self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,    wx.ART_OTHER, (16,16) ))
        fileidx       = self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE,  wx.ART_OTHER, (16,16) ))
        fldparentridx = self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_GO_TO_PARENT, wx.ART_OTHER, (16,16) ))

        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
         # show how to select an item
        self.SetItemState(5, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour("yellow")
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour("light blue")
               
                # initialize variables
        self._cTreeRoot = monFileSystem.getBuilder().getRoots()[0]
        self._dictChildren = {}
        self.initializeContent( self._cTreeRoot)
        self.itemIndexMap = self._dictChildren.keys()
               
        self.SetItemCount( len(self._dictChildren) )

        self.itemDataMap = self._dictChildren
                # initialisation des composants wx.lib.mixins.listctrl
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, 5)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self)

    def initializeContent(self, elementsContainer):
        """
                Entry: elementsContainer - instance of TreeSystem.Node
                Return: None
                Action: initialize list of children of elementsContainer
        """
        self._elementsContainer = elementsContainer
        listElements = elementsContainer.getChildrenList()
        print listElements
        self._dictChildren.clear()
        ## création des descriptions - table de hachage
        j = 0
        description = ("..","","","","ROOT",elementsContainer.getParent())
        self._dictChildren[j] = description
        j = j + 1
        for element in listElements:
            element.computeAttribs()
            try:
                name = getattr(element, "relativename")
            except:
                 # print "Unexpected error:", sys.exc_info()[0] # raise
                 name = "! UNKNOWN !"
            try:
                 extension = getattr( element, "extension")
            except:
                 extension = "! NONE !"
            try:
                 size = getattr( element, "sizeKb")
            except:
                 size = 0
            try:
                 sec = getattr( element, "mtime")
            except:
                 sec = 0
            # type of element
            typeElement = element.getTypeName()
            description = ( name, extension, 
            str(size) + ' B', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sec)),
                                                        typeElement, element )
            self._dictChildren[j] = description
            j = j + 1

                #print self._dictChildren
                # mise en place dans l'IHM des descriptions
                ##self.updateListCtrl()

                ##self.SetColumnWidth(0, 220)
                ##self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
                ##self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
                ##self.SetColumnWidth(3, wx.LIST_AUTOSIZE)
                ##self.SetColumnWidth(4, wx.LIST_AUTOSIZE)

                ##self.itemDataMap = self._dictChildren
                ##pass

    def updateListCtrl(self):
        """
                Mise à jour des éléments de la liste à partir de la variable interne self._dictChildren
        """
        # mise en place dans l'IHM des descriptions
        self.DeleteAllItems()
        j = 0
        for index in self._dictChildren:
            description = self._dictChildren[index]
            #element = description[5]
            self.InsertStringItem(index, description[0])
            # type of element
            #if element == None or description[4]==u"DIRECTORY": #element.getTypeName() == u"DIRECTORY":
            if description[4]==u"DIRECTORY":
                self.SetItemImage(index, 0) # dossier
            elif description[4]==u"ROOT":
                self.SetItemImage(index, 3) # root
            else:
                self.SetItemImage(index, 2) # fichier
                self.SetStringItem(index, 0, description[0])
                self.SetStringItem(index, 1, description[1])
                self.SetStringItem(index, 2, description[2])
                self.SetStringItem(index, 3, description[3])
                self.SetStringItem(index, 4, description[4])
                self.SetItemData(index, index)
                #if (index % 2) == 0:
                #       self.SetItemBackgroundColour(j, '#e6f1f5')
                j = j + 1
        pass

    def OnGetItemAttr(self, item):
        if item % 2 == 1:
            return self.attr1
        else:
            return None
        
        #def OnGetItemText(self, item, col):
        #       ligne = self._dictChildren[item]
        #       s = ligne[col]
        #       return s
        
    def OnGetItemText(self, item, col):
        index=self.itemIndexMap[item]
        s = self._dictChildren[index][col]
        return s

    def SortItems(self,sorter=cmp):
        items = list(self._dictChildren.keys())
        items.sort(sorter)
        self.itemIndexMap = items
                
                # redraw the list
        self.Refresh()
        
        # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    def OnDoubleClick(self, event):
        print "OnDoubleClick: %s - TopItem: %s" % (self.GetItemText(self.currentItem), self.GetTopItem())
        element = self.GetItemData( self.currentItem)
        print element
        self.initializeContent( self._dictChildren[ int(element)][5])
                #size = self.GetSize()
                #self.splitter.SetSashPosition(size.x / 2)

    def OnItemActivated(self, event):
        self.currentItem = event.m_itemIndex
        print "OnItemActivated: %s - TopItem: %s" % (self.GetItemText(self.currentItem), self.GetTopItem())

    def OnItemSelected(self, event):
        #print event.GetItem().GetTextColour()
        self.currentItem = event.m_itemIndex
        print "OnItemSelected: %s %s" % (self.currentItem, self.GetItemData( self.currentItem))

    def OnItemDeselected(self, evt):
        item = evt.GetItem()
        print "OnItemDeselected: %d" % evt.m_itemIndex

    def OnColClick(self, event):
        print "OnColClick: %d" % event.GetColumn()
        event.Skip()

class TestPanel(wx.Panel):
    def __init__(self, parent, monSysteme):
        #self.log = log
        wx.Panel.__init__(self, parent, -1)

        self.nb = wx.aui.AuiNotebook(self)
        #page = wx.TextCtrl(self.nb, -1, text, style=wx.TE_MULTILINE)
        page = MyListCtrl(self.nb, -1, monSysteme)
        self.nb.AddPage(page, "Welcome")

        for num in range(1, 5):
            page = wx.TextCtrl(self.nb, -1, "This is page %d" % num ,
                                            style=wx.TE_MULTILINE)
            self.nb.AddPage(page, "Tab Number %d" % num)

        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)


class FileHunter(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title)

        monSysteme = FileSystem.FileManager()
        monBuilder = monSysteme.getBuilder()
        monBuilder.findRoots()

        p1 = TestPanel(self, monSysteme)

                #p1 = MyListCtrl(self, -1, monSysteme)

                #self.splitter = wx.SplitterWindow(self, ID_SPLITTER, style=wx.SP_BORDER)
                #self.splitter.SetMinimumPaneSize(50)

                #p1 = MyListCtrl(self.splitter, -1, monSysteme)
                #p2 = MyListCtrl(self.splitter, -1, monSysteme)
                #self.splitter.SplitVertically(p1, p2)

        self.Bind(wx.EVT_SIZE, self.OnSize)
                # self.Bind(wx.EVT_SPLITTER_DCLICK, self.OnDoubleClick, id=ID_SPLITTER)

        self.sb = self.CreateStatusBar()

        filemenu= wx.Menu()
        filemenu.Append(ID_EXIT,"E&xit"," Terminate the program")
        editmenu = wx.Menu()
        netmenu = wx.Menu()
        showmenu = wx.Menu()
        configmenu = wx.Menu()
        helpmenu = wx.Menu()

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")
        menuBar.Append(editmenu, "&Edit")
        menuBar.Append(netmenu, "&Net")
        menuBar.Append(showmenu, "&Show")
        menuBar.Append(configmenu, "&Config")
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)

        tb = self.CreateToolBar( wx.TB_HORIZONTAL | wx.NO_BORDER | 
                                                                 wx.TB_FLAT | wx.TB_TEXT)
                #tb.AddSimpleTool(10, wx.Bitmap('images/previous.png'), 'Previous')
                #tb.AddSimpleTool(20, wx.Bitmap('images/up.png'), 'Up one directory')
                #tb.AddSimpleTool(30, wx.Bitmap('images/home.png'), 'Home')
                #tb.AddSimpleTool(40, wx.Bitmap('images/refresh.png'), 'Refresh')
                #tb.AddSeparator()
                #tb.AddSimpleTool(50, wx.Bitmap('images/write.png'), 'Editor')
                #tb.AddSimpleTool(60, wx.Bitmap('images/terminal.png'), 'Terminal')
                #tb.AddSeparator()
                #tb.AddSimpleTool(70, wx.Bitmap('images/help.png'), 'Help')
        tb.AddSimpleTool(10, wx.Bitmap('images/Class.png'), 'Previous')
        tb.AddSimpleTool(20, wx.Bitmap('images/Class.png'), 'Up one directory')
        tb.AddSimpleTool(30, wx.Bitmap('images/Class.png'), 'Home')
        tb.AddSimpleTool(40, wx.Bitmap('images/Class.png'), 'Refresh')
        tb.AddSeparator()
        tb.AddSimpleTool(50, wx.Bitmap('images/Class.png'), 'Editor')
        tb.AddSimpleTool(60, wx.Bitmap('images/Class.png'), 'Terminal')
        tb.AddSeparator()
        tb.AddSimpleTool(70, wx.Bitmap('images/Class.png'), 'Help')
        tb.Realize()

        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        button1 = wx.Button(self, ID_BUTTON + 1, "F3 View")
        button2 = wx.Button(self, ID_BUTTON + 2, "F4 Edit")
        button3 = wx.Button(self, ID_BUTTON + 3, "F5 Copy")
        button4 = wx.Button(self, ID_BUTTON + 4, "F6 Move")
        button5 = wx.Button(self, ID_BUTTON + 5, "F7 Mkdir")
        button6 = wx.Button(self, ID_BUTTON + 6, "F8 Delete")
        button7 = wx.Button(self, ID_BUTTON + 7, "F9 Rename")
        button8 = wx.Button(self, ID_EXIT, "F10 Quit")

        self.sizer2.Add(button1, 1, wx.EXPAND)
        self.sizer2.Add(button2, 1, wx.EXPAND)
        self.sizer2.Add(button3, 1, wx.EXPAND)
        self.sizer2.Add(button4, 1, wx.EXPAND)
        self.sizer2.Add(button5, 1, wx.EXPAND)
        self.sizer2.Add(button6, 1, wx.EXPAND)
        self.sizer2.Add(button7, 1, wx.EXPAND)
        self.sizer2.Add(button8, 1, wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)

        #self.sizer = wx.BoxSizer(wx.VERTICAL)
                #self.sizer.Add(self.splitter,1,wx.EXPAND)
                #self.sizer.Add(self.sizer2,0,wx.EXPAND)
                #self.SetSizer(self.sizer)

        self.sizer = wx.BoxSizer()
        self.sizer.Add(p1, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        size = wx.DisplaySize()
        size = ( size[0]-100, size[1]-100)
        self.SetSize(size)

                #self.sb = self.CreateStatusBar()
        self.sb.SetStatusText(os.getcwd())
        self.Center()
        self.Show(True)

    def OnExit(self,e):
        self.Close(True)

    def OnSize(self, event):
        size = self.GetSize()
                #self.splitter.SetSashPosition(size.x / 2)
        self.sb.SetStatusText(os.getcwd())
        event.Skip()


app = wx.App(0)
FileHunter(None, -1, 'File Hunter')
app.MainLoop()


