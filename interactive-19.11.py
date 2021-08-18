# -*- coding: utf-8 -*-
"""
Geoplotter 2000: an interactive plotting tool for UK cities

author: James Lockwood
date: 20/11/2018
"""

#%% Import standard modules

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter import filedialog
import matplotlib.pyplot as plt
import math

#%% Import modules with uncertain import results

importerror = False
weberror = False
try:
    from PIL import Image, ImageTk
except ModuleNotFoundError:
    importerror = True
try:
    import webbrowser
    import requests
except ModuleNotFoundError:
    weberror = True


#%% Set up variables

plottypes = ["Placenames","Heatmap"]
methods = ["Cities","Image boundaries"]
markers = ['s','o','^','v','*']
colours = ['r','c','y','b','m']


# Function for checking for presence of essential headers in CSV-file
def checkHeader(headers,validHeaders,name='valid'):
    headerFound = False
    for h in range(len(headers)):
        if headers[h].lower() in validHeaders:
            return h
    messagebox.showinfo("ERROR",("The file you have selected does not contain a %s header."%(name)
            +"\nPlease verify your data sheet."))
    return False


#%% Main UI class

# This is the main class of the UI, containing all the logic and functions.
class Geoplotter:
    
    def __init__(self,master):
        '''
        Initialises the Geoplotter GUI and assigns values to default variables.
        '''
        
        #Setup of UI window
        self.master = master
        master.title("Geoplotter 2000")
        master.resizable(0,0)

        #Plot variables
        self.p1 = None
        self.cont = False
        self.coords = []
        
        #GUI variables - store states of settings 
        self.fileLoaded = False
        self.imageLoaded = False
        self.firstLoad = True


        self.typeoption = tk.StringVar(master)
        self.typeoption.set(plottypes[0])

        self.methodoption = tk.StringVar(master)
        self.methodoption.set(methods[0])

        self.populationVal = tk.IntVar()
        self.populationVal.set(0)
        self.typeVal = tk.IntVar()
        self.typeVal.set(1)
        

        self.placename = tk.IntVar()
        self.placename.set(1)
        
        self.legend = tk.IntVar()
        self.legend.set(1)

        self.hyperlink = tk.IntVar()
        self.hyperlink.set(1)
        
        self.criteria = []

        #GUI setup
        #Frames
        self.fileframe = tk.LabelFrame(master,text="Open File")
        self.mapframe = tk.LabelFrame(master,text="Open map")
        self.analysisframe = tk.LabelFrame(master,text="Analysis")
        self.boundariesframe = tk.LabelFrame(master,text="Boundaries")
        self.buttons = ttk.Frame(master)

        #Frame layout
        self.fileframe.grid(row=0,column=0,padx=5,pady=5,ipadx=5,ipady=5,sticky='NSEW')
        self.mapframe.grid(row=0,column=1,rowspan=5,padx=5,pady=5,ipadx=5,ipady=5,sticky='NESW')
        self.analysisframe.grid(row=1,column=0,rowspan=5,padx=5,pady=5,
            ipadx=5,ipady=5,sticky='NESW')
        self.boundariesframe.grid(row=0,column=3,rowspan=3,padx=5,pady=5,ipadx=5,ipady=5)
        self.buttons.grid(row=7,column=0,columnspan=4)#,sticky='NESW')

        #File frame
        self.datafile = ttk.Label(self.fileframe,text="Data file: ")
        self.datafilename = ttk.Entry(self.fileframe,width = 30)
        self.datafilename.insert(10,string="hello there")
        self.datafilename.configure(state='readonly')

        self.filebutton = ttk.Button(self.fileframe,
            text="Open data file...",command = self.dothings)

        #File frame positions
        self.datafile.grid(row=0,column=0)
        self.datafilename.grid(row=0,column=1)
        self.filebutton.grid(row=1,column=0, columnspan=2,sticky='WE')

        #Map frame
        self.mapfile = ttk.Label(self.mapframe,text="Map file: ")
        self.mapfilename = ttk.Entry(self.mapframe,width = 20)
        self.mapfilename.insert(0,string="hello there")
        self.mapfilename.configure(state='readonly')

        self.mapbutton = ttk.Button(self.mapframe,text="Open map image...",command = self.openimage)
        
        # Try to display image of map
        if not importerror: #only display image if PIL has been correctly imported
            self.imagedisplay = ttk.Label(self.mapframe,text="(no image loaded)"+"\n"*10)
            
        else:
            self.imagedisplay = tk.Label(self.mapframe,
                text="(image preview not available)\n(module PIL failed to import)"+"\n"*15)
            self.imagedisplay.configure(state='disable')
                
            
        #Map frame positions
        self.mapfile.grid(row=0,column=0)
        self.mapfilename.grid(row=0,column=1)
        self.mapbutton.grid(row=1,column=0, columnspan=2,sticky='WE')
        self.imagedisplay.grid(row=2,column=0,rowspan=2,columnspan=2,padx=(20,10),sticky='WE')
        
        #Analysis frame - settings of plots 
        self.type = ttk.Label(self.analysisframe, text="Type: ")
        self.typelist = ttk.OptionMenu(self.analysisframe, self.typeoption,'',plottypes[0])

        self.title = ttk.Label(self.analysisframe, text="Title: ")
        self.titleInput = tk.Entry(self.analysisframe, width=20,foreground='black')
        self.colours = ttk.Label(self.analysisframe, text="Colours: ")
        
        self.colourButton = tk.Button(self.analysisframe,text="Edit",
            command=self.colourWindow,width=10)
        
        self.criteriaLabel = ttk.Label(self.analysisframe, text="Criteria: ")
        self.populationCheck = ttk.Checkbutton(self.analysisframe,
            text="Population",variable=self.populationVal,onvalue=1,offvalue=0)
        self.typeCheck = ttk.Checkbutton(self.analysisframe,
            text="Type",variable=self.typeVal,onvalue=1,offvalue=0)
        

        self.placenameCheck = ttk.Checkbutton(self.analysisframe,
            text="Placenames", variable=self.placename,onvalue=1,offvalue=0)
        self.legendCheck = ttk.Checkbutton(self.analysisframe,
            text="Legend", variable=self.legend,onvalue=1,offvalue=0)
        self.hyperlinkCheck = ttk.Checkbutton(self.analysisframe,
            text="Hyperlinks", variable=self.hyperlink,onvalue=1,offvalue=0)



        #Analysis frame positions
        self.type.grid(row=0,column=0)
        self.typelist.grid(row=0,column=1,sticky='WE') 
        self.title.grid(row=1,column=0)
        self.titleInput.grid(row=1, column=1)
        self.colours.grid(row=2,column=0)
        self.colourButton.grid(row=2,column=1)
        self.criteriaLabel.grid(row=3,column=0)
        self.populationCheck.grid(row=3,column=1)
        self.typeCheck.grid(row=3,column=2)

        self.placenameCheck.grid(row=4,column=0,sticky='W')
        self.legendCheck.grid(row=5,column=0,sticky='W')
        self.hyperlinkCheck.grid(row=6,column=0,sticky='W')

        
        for child in self.analysisframe.winfo_children(): #grey out analysis widgets until file is loaded
            child.configure(state='disable')

        #Boundaries frame - specify the boundaries of the map in order to accurately plot the positions of cities
        self.methodlabel = ttk.Label(self.boundariesframe,text="Method: ")
        self.methodlist = ttk.OptionMenu(self.boundariesframe, self.methodoption,'',methods[0],
            methods[1],command=lambda _: self.change())
        self.methodoption.trace('w',self.change) #track if method has been updated

        # Option 1: provide the coordinates of two cities and deduce map boundaries implicitly
        # -- City 1: provide pixel and geographical coordinates of a far out city (cities closer to the boundary provide better accuracy over the entire map)
        self.citiesframe = tk.Frame(self.boundariesframe)
        self.imagelimitsframe = tk.Frame(self.boundariesframe)
        self.resolutionframe = tk.Frame(self.boundariesframe)
        self.city1 = ttk.Label(self.citiesframe,text="City 1")
        self.city1px = ttk.Label(self.citiesframe,text="Image Coords: ")
        self.city1pxlat = ttk.Label(self.citiesframe,text="Pixel latitude: ")
        self.city1pxlon = ttk.Label(self.citiesframe,text="Pixel longitude: ")
        self.city1geo = ttk.Label(self.citiesframe,text="Geographical coordinates: ")
        self.city1geolat= ttk.Label(self.citiesframe,text="Geo latitude: ")
        self.city1geolon = ttk.Label(self.citiesframe,text="Geo longitude: ")
        self.c1pxlat = ttk.Entry(self.citiesframe,state='normal',width=7)
        self.c1pxlon = ttk.Entry(self.citiesframe,state='normal',width=7)
        self.c1geolat = ttk.Entry(self.citiesframe,state='normal',width=7)
        self.c1geolon = ttk.Entry(self.citiesframe,state='normal',width=7)
        
        # -- City 2: provide pixel and geographical coordinates of the second city
        self.city2 = ttk.Label(self.citiesframe,text="City 2")
        self.city2px = ttk.Label(self.citiesframe,text="Image Coords: ")
        self.city2pxlat = ttk.Label(self.citiesframe,text="Pixel latitude: ")
        self.city2pxlon = ttk.Label(self.citiesframe,text="Pixel longitude: ")
        self.city2geo = ttk.Label(self.citiesframe,text="Geographical coords: ")
        self.city2geolat= ttk.Label(self.citiesframe,text="Geo latitude: ")
        self.city2geolon = ttk.Label(self.citiesframe,text="Geo longitude: ")
        self.c2pxlat = ttk.Entry(self.citiesframe,state='normal',width=7)
        self.c2pxlon = ttk.Entry(self.citiesframe,state='normal',width=7)
        self.c2geolat = ttk.Entry(self.citiesframe,state='normal',width=7)
        self.c2geolon = ttk.Entry(self.citiesframe,state='normal',width=7)
        
        # Option 2: give the geographical coordinate boundaries of the image-map 
        self.boundslabel = ttk.Label(self.imagelimitsframe,text="Map boundaries")
        self.boundwestlabel = ttk.Label(self.imagelimitsframe,text="West lim")
        self.boundnorthlabel = ttk.Label(self.imagelimitsframe,text="North lim")
        self.boundeastlabel = ttk.Label(self.imagelimitsframe,text="East lim")
        self.boundsouthlabel = ttk.Label(self.imagelimitsframe,text="South lim")
        self.west = ttk.Entry(self.imagelimitsframe,state='disabled',width=7)
        self.north = ttk.Entry(self.imagelimitsframe,state='disabled',width=7)
        self.east = ttk.Entry(self.imagelimitsframe,state='disabled',width=7)
        self.south = ttk.Entry(self.imagelimitsframe,state='disabled',width=7)

        # Resolution information about the image 
        self.resolutionlabel = ttk.Label(self.resolutionframe,text="Image Resolution (X x Y):")
        self.resolutionentryX = ttk.Entry(self.resolutionframe,state='normal',width=7)
        self.resolutionentryY = ttk.Entry(self.resolutionframe,state='normal',width=7)
        if not importerror: #automatically add in the resolution if PIL is imported
            self.resolutionentryX.insert(0,string="N/A")
            self.resolutionentryX.configure(state='disable')
            self.resolutionentryY.insert(0,string="N/A")
            self.resolutionentryY.configure(state='disable')

        #Boundaries frame positions
        self.methodlabel.grid(row=0,column=0,sticky='W',padx=0)
        self.methodlist.grid(row=0,column=1,sticky='WE')

        self.citiesframe.grid(row=1,column=0,columnspan=2,sticky='WE')
        self.imagelimitsframe.grid(row=2,column=0,columnspan=2,sticky='WE')
        self.resolutionframe.grid(row=3,column=0,columnspan=2,sticky='WE')

        self.city1.grid(row=0,column=0)
        self.city1px.grid(row=1,column=0)
        self.city1pxlat.grid(row=1,column=1)
        self.city1pxlon.grid(row=1,column=2)
        self.city1geo.grid(row=3,column=0)
        self.city1geolat.grid(row=3,column=1)
        self.city1geolon.grid(row=3,column=2)
        self.c1pxlat.grid(row=2,column=1)
        self.c1pxlon.grid(row=2,column=2)
        self.c1geolat.grid(row=4,column=1)
        self.c1geolon.grid(row=4,column=2)

        self.city2.grid(row=6,column=0)
        self.city2px.grid(row=7,column=0)
        self.city2pxlat.grid(row=7,column=1)
        self.city2pxlon.grid(row=7,column=2)
        self.city2geo.grid(row=9,column=0)
        self.city2geolat.grid(row=9,column=1)
        self.city2geolon.grid(row=9,column=2)
        self.c2pxlat.grid(row=8,column=1)
        self.c2pxlon.grid(row=8,column=2)
        self.c2geolat.grid(row=10,column=1)
        self.c2geolon.grid(row=10,column=2)

        self.boundslabel.grid(row=0,column=0,padx=5,sticky='W')
        self.boundwestlabel.grid(row=2,column=1,padx=5)
        self.boundnorthlabel.grid(row=1,column=2,padx=5)
        self.boundeastlabel.grid(row=2,column=3,padx=5)
        self.boundsouthlabel.grid(row=3,column=2,padx=5)
        self.west.grid(row=3,column=1)
        self.north.grid(row=2,column=2)
        self.east.grid(row=3,column=3)
        self.south.grid(row=4,column=2,padx=10)

        self.resolutionlabel.grid(row = 0,column=0,sticky='W',padx=10)
        self.resolutionentryX.grid(row=0,column=1,padx=5,pady=10)
        self.resolutionentryY.grid(row=0,column=2,padx=5,pady=10)
        
        #Buttons frame - major actions that can be taken by the user: About, Help, Run the plotting, Close the UI
        self.aboutButton = tk.Button(self.buttons,text="About",command=self.aboutWindow)
        self.helpButton = tk.Button(self.buttons,text = "Help",command=self.helpWindow)
        self.runButton = tk.Button(self.buttons,text="Run",command=self.run)
        self.closeButton = tk.Button(self.buttons,text="Close",command=self.master.destroy)

        #Button positions
        self.aboutButton.grid(row=0,column=0,padx=30,pady=10)
        self.helpButton.grid(row=0,column=1,padx=30,pady=10)
        self.runButton.grid(row=0,column=2,padx=30,pady=10)
        self.closeButton.grid(row=0,column=3,padx=30,pady=10)

        #General layout:
        #Apply the same layout to al widgets in analysis frame and mapframe
        for c in self.analysisframe.winfo_children():
            if type(c)==tk.ttk.Label:
                c.grid(sticky='W',pady=5)
        for c in self.mapframe.winfo_children():
            c.grid(padx=5,pady=5)
            
        #Apply the same layout to each widget in each frame of the boundaries frame
        for frame in self.boundariesframe.winfo_children():
            for label in self.citiesframe.winfo_children():
                if type(label)==tk.ttk.Label:
                    label.grid(sticky='W',padx=5,pady=0)

    def openfile(self):
        '''
        Method used to open the CSV data file to be analysed and plotted.
        '''

        #Open window for user to select a (valid) CSV file.
        filepath = tk.filedialog.askopenfile(filetypes=(("CSV files","*.csv"),("Text files","*.txt")))

        #Check that filepath exists before updating the GUI
        if filepath!=None:
            self.path = filepath.name
            self.datafilename.configure(state='normal')
            self.datafilename.delete(0,'end')
            self.datafilename.insert(0,string=self.path)
            self.datafilename.configure(state='readonly')
            self.file = open(self.path,'r')
            self.fileLoaded = True
        else:
            #update fileLoaded to inform program to not proceed until appropriate file has been loaded 
            self.fileLoaded = False
        return 1


    def change(self,*args):
        '''
        Method bound to the boundaries method option-menu: if the user updates the menu, the GUI updates the entries the user can use accordingly
        '''

        # Get the option in boundaries method drop-down menu
        ans = self.methodoption.get()

        #Check if the menu is set to the first method
        if ans == methods[0]:
            #Disable all widgets within the unused frame
            for child in self.imagelimitsframe.winfo_children():
                child.configure(state='disable')
            #Enable all widgets within the used frame
            for kid in self.citiesframe.winfo_children():
                kid.configure(state='normal')
        #If the menu is set to the second method, apply same procedure
        elif ans == methods[1]:
            for child in self.imagelimitsframe.winfo_children():
                child.configure(state='normal')
            for kid in self.citiesframe.winfo_children():
                kid.configure(state='disable') 
        
        # Note: implementation of additional methods can be added here (with further elif's)
        
        return 1
            
            
    def openimage(self):
        '''
        Method used to open the map image to which the data should be plotted.
        '''

        # Open window for user to select an image for the map
        imagefile = tk.filedialog.askopenfile(filetypes=(("PNG files","*.png"),
            ("JPEG files","*.jpg"),("All files","*.*")))
        
        #Check image has been selected
        if imagefile!=None:

            self.imgpath = imagefile.name
            
            #Track if default image has already been loaded and, if not, update entries with default values
            # -- Note: this option allows for a default image to be loaded with known boundaries
            # -- Although this is currently hard-coded, a smarter cache system can be implemented here
            if self.imgpath[-10:]=="ukMERC.png": self.default()
    

            self.mapfilename.configure(state='normal')
            self.mapfilename.delete(0,'end')
            self.mapfilename.insert(0,string=self.imgpath)
            self.mapfilename.configure(state='readonly')
            #Display image preview if PIL installed
            if not importerror:
                img = Image.open(str.encode(self.imgpath))
                self.res = img.size
                img = img.resize((200,300),Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(img,master=self.master)
                self.imagedisplay.configure(image=photo)
                self.imagedisplay.image = photo

                #Retrieve image resolution from PIL 
                self.resolutionentryX.configure(state='normal')
                self.resolutionentryY.configure(state='normal')
                self.resolutionentryX.delete(0,'end')
                self.resolutionentryY.delete(0,'end')
                self.resolutionentryX.insert(0,string=self.res[0])
                self.resolutionentryY.insert(0,string=self.res[1])
                self.resolutionentryX.configure(state='readonly')
                self.resolutionentryY.configure(state='readonly')
            self.imageLoaded = True
            
        else:
            #Allow program to record if no image has been loaded
            self.imageLoaded = False

    def lineReader(self):
        '''
        Method to read line by line the opened data file and store in self.data.
        '''
        

        #Track if capable of opening using csv module 
        csvFail = False
        self.data = []
    
        csv = True if self.path[-3:]=='csv' else False
        # If csv-file imported, load it using csv package. Note: alternatives exist, such as pandas.read_csv
        if csv:
            try:
                import csv
                reader = csv.reader(self.file,delimiter=',')
                #add each row to as list of values to data
                for row in reader:
                    self.data.append(row)
                self.firstline = self.data[0]

            except ModuleNotFoundError:
                #alert user that CSV module was not found
                csvFail = True
                messagebox.showinfo("ERROR",("The CSV module does not appear to be installed."\
                    "The file will be opened conventionally."))
            except:
                #alert user that some other error has occured
                csvFail = True
                messagebox.showinfo("ERROR",("an unforeseen error has occured."\
                    "The file will be opened conventionally"))
            
        #if error occured in csv-read or file is not explicitly a .csv 
        if csvFail or not csv:
            try:
                #add each row to as list of values to data
                for row in self.file:
                    r = row.rstrip()
                    self.data.append(r.split(','))
                    self.firstline = self.data[0]

         
            except:
                #alert user that this file is not appropriately structured
                messagebox.showinfo("ERROR",("File is not structured as a .csv."))
                #inform program that the selected file is not valid
                self.fileLoaded = False

    def dataLoader(self):
        '''
        Method used to distribute the elements of self.data into their respective lists
        '''

        #Define all possible headers in the CSV-file
        cityHeaders = ['% place','%place','place','city','cities']
        lonHeaders = ['longitude','lon']
        latHeaders = ['latitude','lat']
        popHeaders = ['population','pop']
        typeHeaders = ['type']

        #Presume file is incorrect until otherwise updated
        self.fileLoaded = False

        #Check for the three essential headers
        self.citIdx = checkHeader(self.firstline,cityHeaders,'city')
        if self.citIdx==False and type(self.citIdx)==bool: return 0
        self.lonIdx = checkHeader(self.firstline,lonHeaders,'longitude')
        if self.lonIdx==False and type(self.lonIdx)==bool: return 0
        self.latIdx = checkHeader(self.firstline,latHeaders,'latitude')
        if self.latIdx==False and type(self.latIdx)==bool: return 0

        #Check that the other desired headers are present
        self.popIdx = checkHeader(self.firstline,popHeaders,'population')
        if self.popIdx==False and type(self.popIdx)==bool: 
            self.populationCheck.configure(state='disable')
        self.typeIdx = checkHeader(self.firstline,typeHeaders,'type')
        if self.typeIdx==False and type(self.typeIdx)==bool: 
            self.typeCheck.configure(state='disable')
            
        #Check all values expected to be numerical are valid
        try:
            self.x, self.y,self.pop = [], [], []
            for i in range(1,len(self.data)):
                self.x.append(float(self.data[i][self.lonIdx]))
                self.y.append(float(self.data[i][self.latIdx]))
                if self.popIdx!=False and type(self.popIdx)==int:
                    self.pop.append(int(self.data[i][self.popIdx]))
            self.fileLoaded = True
        except ValueError:
            #Inform user that file has values that can't be interpreted correctly (i.e. expected a number, none given)
            messagebox.showinfo("ERROR",
                ("The file may only contain floats or integers for the coordinates of the city%s."%("and the populations" if (self.popIdx!=False and type(self.popIdx)==int) else "")))
            self.fileLoaded = False
            return 0

    def default(self):
        '''
        Method used to assign the default values to the city entries when the default map, ukMERC.png is selected.
        '''

        #Exit method if map was already loaded once before 
        if not self.firstLoad:
            return 0

        self.firstLoad = False
        i=0
        #Default city values: known boundaries for the default map
        vals = [-775,218,50.37153,-4.14305,-272.5,268.5,55.95206,-3.19648]
        for child in self.citiesframe.winfo_children():
            if type(child)==tk.ttk.Entry:
                child.insert(0,string=str(vals[i]))
                i+=1
        #Default resolution values
        self.resolutionentryX.insert(0,string=str(538))
        self.resolutionentryY.insert(0,string=str(811))    

    def dothings(self):
        '''
        Method called when file is loaded: opens file and processes the data
        '''
        self.openfile()
        if self.fileLoaded:
            self.lineReader()
        if self.fileLoaded:
            self.dataLoader()
        
        #Allow user to start modifying the parameters dependant on the data
        if self.fileLoaded:
            for child in self.analysisframe.winfo_children():
                child.configure(state='normal')

    def colourWindow(self):
        '''
        Open window to edit the colour scheme: NOT YET IMPLEMENTED
        '''
        self.colourFrame = tk.Toplevel(self.master)
        self.message = tk.Label(self.colourFrame,text="This feature has not been enabled yet.")
        self.message.grid(row=0,column=0,padx=10,pady=20)

    def checkCoords(self):
        '''
        Method to check user's input in all the boundary boxes
        '''

        messageEmpty = "Some values appear to have been left blank."
        messageInvalid = '"%s" is not valid number (%s).'
        conclusion = "\nPlease verify all your values before proceeding."
        
        #Function to check all entries in a frame
        def check(frame,func=float):
            for element in frame.winfo_children():
                if type(element)==tk.ttk.Entry:
                    value = element.get()
                    if value=="":
                        #Inform user that some entries have been left blank
                        messagebox.showinfo("ERROR",(messageEmpty+conclusion))
                        return 0
                    else:
                        try:
                            func(value) 
                        except ValueError:
                            #Inform user that some of their inputs are not numerically valid
                            messagebox.showinfo("ERROR",
                                (messageInvalid%(value,func.__name__)+conclusion))
                            return 0
            return 1

        #Check frames that have been filled in by user
        if self.methodoption.get()==methods[0]:
            if check(self.citiesframe)==0: return 0
        else:
            if check(self.imagelimitsframe)==0: return 0
        if check(self.resolutionframe,func=int)==0: return 0

    def setcoords(self):
        '''
        Method that calculates the coordinate boundaries of a map image from either two cities or user input
        '''
        #Get resolution if PIL not imported
        if importerror:
            self.res = [int(self.resolutionentryX.get()),int(self.resolutionentryY.get())]

        #Two cities method
        if self.methodoption.get() == methods[0]:
            #Coordinates of both cities, in pixels and in real coordinates
            c1img = list(map(float,[self.c1pxlon.get(),self.c1pxlat.get()]))
            c1geo = list(map(float,[self.c1geolon.get(),self.c1geolat.get()]))
            c2img = list(map(float,[self.c2pxlon.get(),self.c2pxlat.get()]))
            c2geo = list(map(float,[self.c2geolon.get(),self.c2geolat.get()]))

            #Calculations for transforming between coordinate systems
            xdif = abs(c1geo[0]-c2geo[0])
            ydif = abs(c1geo[1]-c2geo[1])
            udif = abs(c1img[0]-c2img[0])
            vdif = abs(c1img[1]-c2img[1])
    
            multx = xdif/udif
            multy = ydif/vdif
            self.aspect = multx/multy
            
            xlen = multx*self.res[0]
            ylen = multy*self.res[1]

            cx = c1geo[0]-multx*c1img[0]
            cy = c1geo[1]-multy*c1img[1]         
        
            self.xlims = [cx,cx + xlen]
            self.ylims = [cy-ylen,cy]

        #Boundaries method: get user's input
        else:
            self.xlims = [float(self.west.get()),float(self.east.get())]
            self.ylims = [float(self.south.get()),float(self.north.get())]
         
    def townCity(self):
        '''Method to differentiate between different places using the type column of the data'''

        self.types = list(set([self.data[i][self.typeIdx] for i in range(1,len(self.data))])) 
        self.xs, self.ys = [], []
        self.pops = []

        #Keep each x,y,pop data separate for each type t
        for t in self.types:
            self.xs.append([])
            self.ys.append([])
            self.pops.append([])
            for i in range(1,len(self.data)):
                if self.data[i][self.typeIdx]==t:
                    self.xs[len(self.xs)-1].append(float(self.data[i][self.lonIdx]))
                    self.ys[len(self.ys)-1].append(float(self.data[i][self.latIdx]))
                    self.pops[len(self.pops)-1].append(float(self.data[i][self.popIdx]))

    def top10Pops(self):
        '''Method to work out ten most populated places'''

        self.top10 = []
        allPops = []
        
        allPops = list(reversed(list(sorted(self.pop))))
        if len(allPops)<11:
            self.top10 = allPops
        else:
            self.top10 = allPops[:10]
 

    def run(self):
        '''
        Method that runs the plotting and displays the data on the map based on the user's input on the GUI
        '''

        self.plots = []
        message = 'No %s has been loaded.'

        #Check if all data has been loaded correctly
        if not self.fileLoaded:
            messagebox.showinfo("ERROR",(message%'file'))
            return 0
        if not self.imageLoaded:
            messagebox.showinfo("ERROR",(message%'image'))
            return 0

        #Check user has correctly filled in the required boundary information
        if self.checkCoords() == 0: return 0

        #Set the boundaries
        self.setcoords()

        #Begin the plot setup
        img = plt.imread(self.imgpath)
        self.fig = plt.figure()
        
        self.ax = self.fig.add_subplot(111)
        #Define the limits of the plot
        self.ax.imshow(img,extent=[self.xlims[0],self.xlims[1],self.ylims[0],self.ylims[1]])
        self.ax.set_aspect(aspect=self.aspect)

        #if type not selected
        if self.typeVal.get()==0:
            if self.populationVal.get()==1:
                sizeList,colourList = self.getSizeList()
            else:
                sizeList = 7
                colourList = 'r'

            p = self.ax.scatter(self.x,self.y,s=sizeList,c= colourList,cmap='jet',marker=markers[0],label='city or town',picker=7,alpha=0.9)
            self.plots.append(p)
        
        #if type selected, check that type exists
        elif self.typeIdx!=False and type(self.typeIdx)!=bool:
            self.townCity()
            for s in range(len(self.xs)):
                p, = self.ax.plot(self.xs[s],self.ys[s],colours[s]+markers[s],label=self.types[s],picker=7,alpha=0.5)
                self.plots.append(p)

        #if type selected but not type column
        else:
            messagebox.showinfo("ERROR",("Type cannot be displayed as there is no header 'type'."\
                +"Please untick the type box before proceeding"))
            return 0

        #Give the plot its title
        plt.title(self.titleInput.get())
        
        #Check if placename labels are required and display if so
        if self.placename.get() == 1:
            for i in range(1,len(self.data)):
                self.top10Pops()
                if int(self.data[i][self.popIdx]) in self.top10:
                    self.ax.annotate(self.data[i][self.citIdx],
                        (float(self.data[i][self.lonIdx]),float(self.data[i][self.latIdx])))

        #Check if legen is required and display if so
        if self.legend.get()==1:
            plt.legend(loc='upper right')
        
        #Check if hyperlink is required and enable if so
        if self.hyperlink.get()==1:
            self.fig.canvas.mpl_connect("pick_event", self.openURL)

        #Check if plot is able to support interactivity and display if so
        if self.typeVal.get()==1 and self.populationVal.get()==0:
            self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

        #Show what all the hard work has led up to:
        plt.show()
    

    def getSizeList(self):
        '''Method to customise size and color w.r.t. data'''

        #Adapt larger numbers to manageable domain
        lnPops = list(map(math.log,self.pop))
        baseMarker = 7
        minPop = min(lnPops)
        maxPop = max(lnPops)

        #Change wieght of colour and size respectively
        colourList = [int(baseMarker*(i-minPop+1)**1.1) for i in lnPops]
        sizeList = [int(baseMarker*(i-minPop+1)**3) for i in lnPops]

        return [sizeList,colourList]

    def highlight(self,p,event):
        '''Method to highlight marker and change associated text'''
        cont,ind = p.contains(event)

        if cont:
            #Coordinates information
            x,y = p.get_data()
            xIdx = x[ind["ind"][0]]
            yIdx = y[ind["ind"][0]]


            dIdx = self.x.index(xIdx)+1
            for e in range(len(self.types)):
                #Check which type the marker is (city or town?)
                if self.data[dIdx][self.typeIdx]==self.types[e]:
                    col = colours[e]
                    mkr = markers[e]
            #Text to display with the info about the marker
            textstr = "%s\nPopulation: %s\nLatitude: %s\nLongitude: %s"%(self.data[dIdx][self.citIdx],
                self.data[dIdx][self.popIdx],
                self.data[dIdx][self.latIdx],
                self.data[dIdx][self.lonIdx])
            #Check if hyperlinks are desired by user
            if self.hyperlink.get()==1:
                textstr += "\nClick for more info (Wiki)"
            props = dict(boxstyle='round',facecolor='wheat',alpha=0.7)
            #Add text to plot
            self.text = self.ax.text(0.05,0.95,textstr,bbox = props,transform=self.ax.transAxes,fontsize=7,verticalalignment='top')
            self.text.set_visible(True)
            #Add temporarily highlighted marker to plot
            temp, = self.ax.plot(xIdx,yIdx,col+mkr,markersize=20,alpha=1)
            
            #Update the log of all the highlighted points 
            if self.p1==None: self.p1=[]
            self.p1.append(temp)
            self.fig.canvas.draw()
        
        return cont
            
            
    def hover(self,event):
        '''
        Method used to detect mouse hovering above marker
        '''

        self.text = None
        #Check if mouse inside plot
        if event.inaxes == self.ax:
            if not self.cont:
                #Check if mouse is hovering over a city
                p = self.plots[0]
                self.cont = self.highlight(p,event)
                
            if not self.cont:
                #Check if mouse is hovering over town
                p=self.plots[1]
                self.cont = self.highlight(p,event)
                
            if self.p1!=None:
                #Update plot when no longer overing over marker
                self.cont = False
                self.text.set_visible(False)
                for i in self.p1:
                    i.remove()
                    self.p1=None

    def openURL(self,event):
        '''
        Method to open web browser web page when marker is clicked
        '''
        #Clicked marker information
        thisMarker =event.artist

        x = thisMarker.get_xdata()
        y = thisMarker.get_ydata()
        ind = event.ind
        #Marker coordinates
        points = (float(x[ind][0]),float(y[ind][0]))
        
        #Index of city in self.data with firstline offset taken into account (i.e. +1)
        dIdx = self.x.index(points[0])+1
        city = self.data[dIdx][self.citIdx] 

        #Path to open
        path = "https://en.wikipedia.org/wiki/"+city
        #request = requests.get(path)
        #Check that URL exists
        #if request.status_code==200:
        try:
            webbrowser.open("https://en.wikipedia.org/wiki/"+city)
        except:
            messagebox.showinfo("Web warning",("It appears that Wikipedia can't open the page for this city."))
            
    def aboutWindow(self):
        '''Launch about window when button pressed by calling an instance of AboutWindow'''
        self.about = tk.Toplevel(self.master)
        self.app = AboutWindow(self.about)

    def helpWindow(self):
        '''Launch help window when button pressed by calling an instance of HelpWindow'''
        self.helpWindow = tk.Toplevel(self.master)
        self.app = HelpWindow(self.helpWindow)

class AboutWindow:
    '''
    Class that deals with the about window of Geoplotter
    '''
    def __init__(self,master):
        self.master = master
        master.wm_title("About Geoplotter 2000")
        master.geometry('400x250')
        master.resizable(0, 0)

        #Frames
        self.frame1 = ttk.Frame(master)
        self.frame1.pack()

        #Frame elements
        self.aboutText = tk.Label(self.frame1,
                        text='\n'
                             'Geoplotter 2000 (version 1.0)\n'
                             '\n'
                             'A Geographical Data Analysis\n'
                             'Program for Python\n'
                             '\n'
                             '(c) James Lockwood (2018)\n'
                             'Department of Physics and Astronomy\n'
                             'The University of Manchester\n'
                             '\n')


        self.close = ttk.Button(self.frame1, text='Close'
                                , width=20, command=master.destroy)

        #Frame element positions
        self.aboutText.grid(row=0)
        self.close.grid(row=1)

class HelpWindow:
    '''
    Class that deals with the help window of Geoplotter
    '''
    def __init__(self,master):
        self.master = master
        master.wm_title("Geoplotter 2000 HELP")
        master.geometry('1000x600')
        master.resizable(0, 0)


        #Frames
        self.frame1 = ttk.Frame(master)
        self.frame1.pack()

        #Frame elements
        text = ("GEOPLOTTER 2000 HELP WINDOW\n\n"
                "To use this program, an CSV data file with headers 'City', 'Type', 'Population', 'Longitude' and 'Latitude'\n"
                "has to be loaded by pressing the Open Data File button in the top left corner.\n"
                "Similarly a map image must be loaded using the Open Map Image button. By default the program recognises the\n"
                "'ukMERC.png' map and automatically loads in the data for this map.\n"
                "Please note that if the program manages to import PIL, a small display of the map will be shown in the centre\n"
                "of the window.\n"
                "The boundaries frame on the right hand side allows users to manually input the boundaries for their map.\n"
                "The default method, however, is to find the pixel coordinates of two cities on the map and input these along with\n"
                "their real cooordinates. For the ukMERC.png map, Plymouth and Edinburgh were used."
                "If for whatever reason this were not to occur, please select 'Boundaries' from the \n"
                "dropdown list on the right and input from North to East (clockwise):\n"
                "58.97832, 1.85502, 49.9717, -8.22923.\n\n"
                "At this stage, you are ready to RUN the program using the third button at the bottom of the window. Each press\n"
                "will lead to a new plot being created.\n\n"
                "Option to customise the plots can be found on the left hand side and include: \n"
                "- change map title\n- display difference between towns and cities\n- display population size\n"
                "- add legend\n- add labels for top 10 most populated placesn\n- add option to click on point to take you to\n"
                "website of the town or city.\n\n"
                "To get the interactive map (increased marker size when mouse hovers above marker and hyperlinks), make sure to\n"
                "deselect the population checkmark and select the type checkmark.\n\n"
                "To get the full benifit of the program, please ensure the maps are plotted to a SEPARATE WINDOW, and are not\n"
                "simply inline with a kernel (e.g. Spyder's default settings).\n\n\n"


                )
        self.aboutText = tk.Label(self.frame1,
                        text=text,justify='left')
        self.close = ttk.Button(self.frame1, text='Close'
                                , width=20, command=master.destroy)

        #Frame element positions
        self.aboutText.grid(row=0)
        self.close.grid(row=1)

# Main: run code if script is run as main file. 
# This allows the classes to be imported by other scripts without running main code.
if __name__ == '__main__':
    # Create root window
    root = tk.Tk()
    # Crate instance of UI class
    r = Geoplotter(root)
    # Run the root-window
    root.mainloop()

