#coding=utf-8
import wx, os
import wx.dataview as dv
from client import MyClient
from pysimplesoap.client import SoapClient, SoapFault
import sys
import time
reload(sys)
sys.setdefaultencoding("utf-8")

#----------------------------------------------------------------------

# This model class provides the data to the view when it is asked for.
# Since it is a list-only model (no hierachical data) then it is able
# to be referenced by row rather than by item object, so in this way
# it is easier to comprehend and use than other model types.  In this
# example we also provide a Compare function to assist with sorting of
# items in our model.  Notice that the data items in the data model
# object don't ever change position due to a sort or column
# reordering.  The view manages all of that and maps view rows and
# columns to the model's rows and columns as needed.
#
# For this example our data is stored in a simple list of lists.  In
# real life you can use whatever you want or need to hold your data.

class TestModel(dv.PyDataViewIndexListModel):
    def __init__(self, data, log, Client):
        dv.PyDataViewIndexListModel.__init__(self, len(data))
        self.log = log
        self.client=Client
        self.path=self.pwd()
        self.data = data
        self.Init()
        self.SrcCopyPath=None
        self.NewCopyName=None

    # All of our columns are strings.  If the model or the renderers
    # in the view are other types then that should be reflected here.
    def Init(self):
        self.UpdateAll()
    
    def UpdateAll(self):
        dir_list=self.client.ls_dir(self.path)
        file_list=self.client.ls_file(self.path)
        file_list.sort()
        dir_list.sort()
        #for name in dir_list:
            #self.log.write(name)
        
        #clear the model
        datalen=self.GetCount()
        self.DeleteRows(range(0, datalen))
        
        for name in dir_list:
            if len(name)!=0:
                if name[0]!='.':
                    self.AddRow([name,'None', 'Folder'])
        for name in file_list:
            if len(name)!=0:
                if name[0]!='.':
                    size=self.client.getsize(os.path.join(self.path, name))
                    self.AddRow([name, str(size), 'File'])
        print 'ipdate', len(self.data)   
        
    def GetColumnType(self, col):
        return "string"

    # This method is called to provide the data object for a
    # particular row,col
    def GetValueByRow(self, row, col):
        return self.data[row][col]

    # This method is called when the user edits a data item in the view.
    def SetValueByRow(self, value, row, col):
        self.log.write("SetValue: (%d,%d) %s\n" % (row, col, value))
        self.data[row][col] = value

    # Report how many columns this model provides data for.
    def GetColumnCount(self):
        #return len(self.data[0])
        return 3

    # Report the number of rows in the model
    def GetCount(self):
        #self.log.write('GetCount')
        print 'count', len(self.data)
        return len(self.data)
    
    # Called to check if non-standard attributes should be used in the
    # cell at (row, col)
    def GetAttrByRow(self, row, col, attr):
        ##self.log.write('GetAttrByRow: (%d, %d)' % (row, col))
        if col == 0:
            attr.SetColour('blue')
            attr.SetBold(True)
            return True
        return False


    # This is called to assist with sorting the data in the view.  The
    # first two args are instances of the DataViewItem class, so we
    # need to convert them to row numbers with the GetRow method.
    # Then it's just a matter of fetching the right values from our
    # data set and comparing them.  The return value is -1, 0, or 1,
    # just like Python's cmp() function.
    def Compare(self, item1, item2, col, ascending):
        if not ascending: # swap sort order?
            item2, item1 = item1, item2
        row1 = self.GetRow(item1)
        row2 = self.GetRow(item2)
        if col==1:
            if self.data[row1][col]=='None' and self.data[row2][col]=='None':
                return 0
            elif self.data[row1][col]=='None':
                return -1
            elif self.data[row2][col]=='None':
                return 1
            else:
                return cmp(int(self.data[row1][col]), int(self.data[row2][col]))
        else:
            return cmp(self.data[row1][col], self.data[row2][col])

        
    def DeleteRows(self, rows):
        # make a copy since we'll be sorting(mutating) the list
        rows = list(rows)
        # use reverse order so the indexes don't change as we remove items
        rows.sort(reverse=True)
        
        for row in rows:
            # remove it from our data structure
            del self.data[row]
            # notify the view(s) using this model that it has been removed
            self.RowDeleted(row)
            
            
    def AddRow(self, value):
        # update data structure
        self.data.append(value)
        # notify views
        self.RowAppended()
    
    def pwd(self):
        #self.path=self.client.pwd()
        return self.client.pwd()
        
            
class TestPanel(wx.Panel):
    def __init__(self, parent, log, model=None, data=None, soapclient=None):
        self.log = log
        wx.Panel.__init__(self, parent, -1)
        

        # Create a dataview control
        self.dvc = dv.DataViewCtrl(self,
                                   style=wx.BORDER_THEME
                                   | dv.DV_ROW_LINES # nice alternating bg colors
                                   #| dv.DV_HORIZ_RULES
                                   | dv.DV_VERT_RULES
                                   | dv.DV_MULTIPLE
                                   )
        
        # Create an instance of our simple model...
        if model is None:
            self.model = TestModel(data, log,soapclient)
        else:
            self.model = model            

        # ...and associate it with the dataview control.  Models can
        # be shared between multiple DataViewCtrls, so this does not
        # assign ownership like many things in wx do.  There is some
        # internal reference counting happening so you don't really
        # need to hold a reference to it either, but we do for this
        # example so we can fiddle with the model from the widget
        # inspector or whatever.
        self.dvc.AssociateModel(self.model)

        # Now we create some columns.  The second parameter is the
        # column number within the model that the DataViewColumn will
        # fetch the data from.  This means that you can have views
        # using the same model that show different columns of data, or
        # that they can be in a different order than in the model.
        c1=self.dvc.AppendTextColumn("Size",  1, width=170, mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        c2=self.dvc.AppendTextColumn("Type",   2, width=260, mode=dv.DATAVIEW_CELL_ACTIVATABLE)
   

        # There are Prepend methods too, and also convenience methods
        # for other data types but we are only using strings in this
        # example.  You can also create a DataViewColumn object
        # yourself and then just use AppendColumn or PrependColumn.
        c0 = self.dvc.PrependTextColumn("Name", 0, width=200, mode=dv.DATAVIEW_CELL_ACTIVATABLE)

        # The DataViewColumn object is returned from the Append and
        # Prepend methods, and we can modify some of it's properties
        # like this.
        c0.Alignment = wx.ALIGN_RIGHT
        c1.Alignment= wx.ALIGN_RIGHT
        c2.Alignment= wx.ALIGN_RIGHT
        
        c0.Renderer.Alignment = wx.ALIGN_RIGHT
        c0.MinWidth = 100
        
        c1.Renderer.Alignment = wx.ALIGN_RIGHT
        c1.MinWidth = 100
        
        c2.Renderer.Alignment = wx.ALIGN_RIGHT
        c2.MinWidth = 100
        # Through the magic of Python we can also access the columns
        # as a list via the Columns property.  Here we'll mark them
        # all as sortable and reorderable.
        for c in self.dvc.Columns:
            c.Sortable = True
            c.Reorderable = True

        # Let's change our minds and not let the first col be moved.
        c0.Reorderable = False


        
        # set the Sizer property (same as SetSizer)
        self.Sizer = wx.BoxSizer(wx.VERTICAL) 
        self.SetSizer(self.Sizer)
    
        self.path=self.model.pwd()
        # Add some thing to help out with the tests
        
        #upload
        uploadbtn = wx.Button(self, label="upload",  name="Upload", style=wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.OnUpload, uploadbtn)       
       
        #go ahead
        go_back_btn = wx.Button(self, label="back", name="go_back", style=wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.OnGoback, go_back_btn)
     
        #go back
        #go_back_btn = wx.Button(self, label="back", name="go_back", style=wx.BU_EXACTFIT)
        #self.Bind(wx.EVT_BUTTON, self.OnGoback, go_back_btn)
        
        #path
        l1 = wx.StaticText(self, -1, "  path:")
        self.t1 = wx.TextCtrl(self, -1, self.path, size=(450, -1), style=wx.TE_PROCESS_ENTER)
        
        #status
        l2=wx.StaticText(self, -1, "status: ")
        self.status=wx.StaticText(self, -1, "")
        #self.status.SetLabel('hello')
        #btnbox
        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        StatusBox=wx.BoxSizer(wx.HORIZONTAL)
        
        #add
        #btnbox.Add(go_ahead_btn, 0,wx.LEFT|wx.RIGHT, 5 )
        btnbox.Add(go_back_btn, 0,wx.LEFT|wx.RIGHT, 5 )
        btnbox.Add(l1, 0,wx.ALIGN_CENTER, 5 )
        btnbox.Add(self.t1, 0,wx.LEFT|wx.RIGHT, 5 )
        btnbox.Add(uploadbtn, 0, wx.RIGHT, 5)
        StatusBox.Add(l2, 0, wx.LEFT|wx.RIGHT, 5)
        StatusBox.Add(self.status, 0, wx.LEFT|wx.RIGHT, 5)
        self.Sizer.Add(btnbox, 0, wx.TOP|wx.BOTTOM, 5)
        self.Sizer.Add(self.dvc, 1, wx.EXPAND)
        self.Sizer.Add(StatusBox, 0, wx.EXPAND)
        '''dir_list=self.client.ls_dir()
        id = 0
        value = [' %d' % id,
                 'new title %d' % id,
                 'genre %d' % id]
        self.model.AddRow(value)'''
        # Bind some events so we can see what the DVC sends us
        self.Bind(dv.EVT_DATAVIEW_ITEM_EDITING_DONE, self.OnEditingDone, self.dvc)
        self.Bind(dv.EVT_DATAVIEW_ITEM_VALUE_CHANGED, self.OnValueChanged, self.dvc)
        self.Bind(dv.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.OnRightBtnClick, self.dvc)
        self.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.OnDoubleClick, self.dvc)   #double click
        self.Bind(wx.EVT_TEXT_ENTER , self.OnTextEnter, self.t1)
    
    def OnTextEnter(self, evt):
        enter_path=self.t1.GetValue()
        if self.model.client.cd(enter_path):
            self.model.path=enter_path
            self.model.UpdateAll()
            self.status.SetLabel('into the path ok')
        else:
            self.status.SetLabel('No Such Path')
            
    def OnRightBtnClick(self, evt):
        # only do this part the first time so the events are only bound once
        #
        # Yet another anternate way to do IDs. Some prefer them up top to
        # avoid clutter, some prefer them close to the object of interest
        # for clarity. 
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()  #下载
            self.popupID2 = wx.NewId()  #删除
            self.popupID3 = wx.NewId()  #重命名
            self.popupID4 = wx.NewId()  #复制
            self.popupID5 = wx.NewId()  #粘贴

            self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
            self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)


        # make a menu
        menu = wx.Menu()
        
        # Show how to put an icon in the menu
        item = wx.MenuItem(menu, self.popupID1,"下载到本机")
        #bmp = images.Smiles.GetBitmap()
        #item.SetBitmap(bmp)
        menu.AppendItem(item)

        
        # add some other items
        menu.Append(self.popupID2, "删除")
        menu.Append(self.popupID3, "重命名")
        menu.Append(self.popupID4, "复制")
        menu.Append(self.popupID5, "粘贴")



        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()
        
    def OnPopupOne(self, event):
        self.log.WriteText("下载\n")
        
        items=self.dvc.GetSelections()
        # In this case we include a "New directory" button. 
        Enable=True
        for name in items:
            if self.model.data[self.model.GetRow(name)][2]=='Folder':
                Enable=False
        if Enable:
            dlg = wx.DirDialog(self, "Choose a directory:",
                              style=wx.DD_DEFAULT_STYLE
                               #| wx.DD_DIR_MUST_EXIST
                               #| wx.DD_CHANGE_DIR
                               )
    
            # If the user selects OK, then we process the dialog's data.
            # This is done by getting the path data from the dialog - BEFORE
            # we destroy it. 
            
            if dlg.ShowModal() == wx.ID_OK:
                store_path=dlg.GetPath()
            # Only destroy a dialog after you're done with it.
                dlg.Destroy()
               
                for item in items:
                    row=self.model.GetRow(item)
                    filename=os.path.join(self.model.path, self.model.data[row][0])
                    print store_path
                    args=(filename, 8002, store_path,)
                    if self.model.client.getfile(*args):
                        self.status.SetLabel('download %d  '%os.path.getsize(store_path) )
                        time.sleep(2)
                        self.status.SetLabel('DOWNLOAD OK')
                    
                
            

    def OnPopupTwo(self, event):
        self.log.WriteText("删除\n")
        items = self.dvc.GetSelections()
        rows = [self.model.GetRow(item) for item in items]
        for row in rows:
            del_item=os.path.join(self.model.path, self.model.data[row][0])
            if self.model.data[row][2]=='Folder':
                self.model.client.rmdir(del_item)
            else:
                self.model.client.rm(del_item)
        self.model.DeleteRows(rows)

    def OnPopupThree(self, event):
        self.log.WriteText("重命名\n")
                
        items = self.dvc.GetSelections()
        rows = [self.model.GetRow(item) for item in items]
        item=self.model.data[rows[0]]
        #Folder=False
        if item[2]=='Folder':
            #Folder=True
            title='rename a folder'
        else:
            title='rename a file'
        dlg = wx.TextEntryDialog(
                self, '   New Name',
                title, 'Pydthon')

        dlg.SetValue("new_name")
        
        if dlg.ShowModal() == wx.ID_OK:
            self.model.client.rename(os.path.join(self.model.path, item[0]),os.path.join(self.model.path, dlg.GetValue()))
            self.log.WriteText('You entered: %s\n' % dlg.GetValue())
        
        dlg.Destroy()
        self.model.UpdateAll()

    def OnPopupFour(self, event):
        self.log.WriteText("复制\n")
                
        items = self.dvc.GetSelections()
        rows = [self.model.GetRow(item) for item in items]
        item=self.model.data[rows[0]]
        if item[2]!='Folder':
            title='copy a file'
            dlg = wx.TextEntryDialog(
                    self, '   New Name',
                    title, 'Pydthon')
    
            dlg.SetValue("new_name")
            
            if dlg.ShowModal() == wx.ID_OK:
                self.model.SrcCopyPath=os.path.join(self.model.path, item[0])
                self.model.NewCopyName=dlg.GetValue()
                self.log.WriteText('You entered: %s\n' % dlg.GetValue())
            
    def OnPopupFive(self, event):
        self.log.WriteText("粘贴\n")
        print self.model.SrcCopyPath,  self.model.NewCopyName
        if self.model.SrcCopyPath!=None and self.model.NewCopyName!=None:
            NewFilePath=os.path.join(self.model.path, self.model.NewCopyName)
            self.model.client.cp(self.model.SrcCopyPath, NewFilePath)
            self.model.UpdateAll()
    
    def OnDoubleClick(self, evt):
        items = self.dvc.GetSelections()
        rows = [self.model.GetRow(item) for item in items]
        item=self.model.data[rows[0]]
        if item[2]=='Folder':
            self.model.path=os.path.join(self.model.path, item[0])+'/'
            self.t1.Clear()
            self.t1.AppendText(self.model.path)
            self.model.UpdateAll()
            
        else:
            self.OnPopupOne(evt)
            
    def OnGoback(self, evt):
        cur_path=self.model.path
        if cur_path!='/':
            if cur_path[-1]=='/':
                cur_path=cur_path[:-1]
            
            parent_path=cur_path.split('/')[:-1]
            parent_path='/'.join(parent_path)
            parent_path=parent_path+'/'
            self.model.path=parent_path
        
        self.log.WriteText(self.model.path)
        self.t1.Clear()
        self.t1.AppendText(self.model.path)
        self.model.UpdateAll()
        

    def OnUpload(self, evt):
        wildcard = "*.*"
           
        self.log.WriteText("CWD: %s\n" % os.getcwd())
        
        # Create the dialog. In this case the current directory is forced as the starting
        # directory for the dialog, and no default file name is forced. This can easilly
        # be changed in your program. This is an 'open' dialog, and allows multitple
        # file selections as well.
        #
        # Finally, if the directory is changed in the process of getting files, this
        # dialog is set up to change the current working directory to the path chosen.
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        paths=[]
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            paths = dlg.GetPaths()

            #self.log.WriteText('You selected %d files:' % len(paths))

     

        # Compare this with the debug above; did we change working dirs?
        self.log.WriteText("CWD: %s\n" % os.getcwd())

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()
        for path in paths:
            savepath=os.path.join(self.model.path, os.path.basename(path))
            args=(path, savepath, '115.156.209.190')
            self.model.client.sendfile(*args)
            self.model.UpdateAll()
            self.status.SetLabel('Upload ok')

        
    def OnNewView(self, evt):
        f = wx.Frame(None, title="New view, shared model", size=(600,400))
        TestPanel(f, self.log, self.model)
        b = f.FindWindowByName("newView")
        b.Disable()
        f.Show()


    def OnDeleteRows(self, evt):
        # Remove the selected row(s) from the model. The model will take care
        # of notifying the view (and any other observers) that the change has
        # happened.
        items = self.dvc.GetSelections()
        rows = [self.model.GetRow(item) for item in items]
        self.model.DeleteRows(rows)

        
    def OnAddRow(self, evt):
        # Add some bogus data to a new row in the model's data
        id = len(self.model.data) + 1
        value = ['new Name %d' %id,
                 'new Name %d' % id,
                 'new title %d' % id]
        self.model.AddRow(value)
                

    def OnEditingDone(self, evt):
        self.log.write("OnEditingDone\n")

    def OnValueChanged(self, evt):
        self.log.write("OnValueChanged\n")

        
#----------------------------------------------------------------------

def runTest(frame, nb, log):
    # Get the data from the ListCtrl sample to play with, converting it
    # from a dictionary to a list of lists, including the dictionary key
    # as the first element of each sublist.
    musicdata = {
    #1 : ("Bad English", "The Price Of Love", "asd"),
    #2 : ("Bad math", "The Price Of Love", "asd"),
    }

    #musicdata = musicdata.items()
    #musicdata.sort()
    #musicdata = [["1","qwe","234" ], ["2","qwe","sd"]]#[list(v) for v in musicdata]
    server_ip='192.168.16.105'
    server_port='8008'
    fulladdr="http://"+server_ip+":"+server_port+"/"
    soapinfo = SoapClient(
            location = fulladdr,
        action = fulladdr, # SOAPAction
        namespace = "http://example.com/sample.wsdl", 
        soap_ns='soap',
        trace = True,
        ns = False)
    my=MyClient(soapinfo)
    
    data=[]
    for k in musicdata:
        data.append(list(musicdata[k]))
    musicdata = data
    
    mymodel=TestModel(musicdata, log, my)
    win = TestPanel(nb, log, model=mymodel, )
    return win

#----------------------------------------------------------------------



overview = """<html><body>
<h2><center>DataViewCtrl with DataViewIndexListModel</center></h2>

This sample shows how to derive a class from PyDataViewIndexListModel and use
it to interface with a list of data items. (This model does not have any
hierarchical relationships in the data.)

<p> See the comments in the source for lots of details.

</body></html>
"""



if __name__ == '__main__':
    import FileManager
    import sys
    FileManager.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])

