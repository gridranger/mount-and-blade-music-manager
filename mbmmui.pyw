# Mount & Blade Music Manager - User interface module
# Written by Bárdos Dávid (2014-2015)
# License: Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
#          http://creativecommons.org/licenses/by-nc-sa/4.0/

from glob import glob
from os import listdir,makedirs,path
from shutil import copy2
from tkinter import Button, Canvas, Checkbutton, Entry, filedialog, Frame, IntVar, Label, Menu, messagebox, Scrollbar, StringVar, Tk
from tkinter.ttk import Combobox
from xml.etree.ElementTree import Element,ElementTree,parse,SubElement
from mbmm import MusicTxt, Track

class AppWindow(Tk):
    """main window"""
    def __init__(self):
        Tk.__init__(self)
        self.title("Mount & Blade Music Manager")
        self.wm_geometry("600x600+100+100")
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.languageIsSet = False
        self.conf = Config()
        self.language = self.readLanguages()
        self.musicTxt = MusicTxtPalceHolder()
        self.menubar = AppMenu(self)
        self.config(menu = self.menubar)
        self.musicFileName = "music.txt"
        self.musicFolderName = "Music"
        self.game_db = self.conf.readTypes()
        self.game_type = None
        self.rowdict = {}
        self.worktop = Frame(self)
        self.changed = False
        self.order = ("fileName", False) # other possible values are "id" and True
        self.rownum = 0
        self.createCanvas()
        
    def createCanvas(self):
        """generating widgets"""
        self.worktop.destroy()
        self.worktop = Frame(self)
        self.worktop.pack(side="bottom")
        self.buttonline = Frame(self.worktop)
        self.buttonline.pack(side="top", anchor="w")
        self.canvas = Canvas(self.worktop)
        self.mainframe = Frame(self.canvas)
        self.scrollbar = Scrollbar(self.worktop, orient="vertical", command=self.canvas.yview)
        
    def showCanvas(self):
        """shows widgets"""
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right",fill="y")
        self.canvas.pack(side="left")
        self.canvas.create_window((0,0), window = self.mainframe, anchor = "nw")
        self.mainframe.bind("<Configure>", self.scrolling)
            
    def openModule(self):
        """opens a module"""
        if not self.confirmColse():
            return
        self.createCanvas()
        d = filedialog.askdirectory() + "/"
        if d == "/":
            return
        if not path.exists(d + self.musicFileName) or not path.exists(d + self.musicFolderName): # check if txt and folder is in the right place
            answer = messagebox.askyesno(self.conf.ui["question"].get(), self.conf.ui["noMusicTxt"].get()) # if no we ask if we shall create them
            if answer: # if he said yes
                if not path.exists(d + self.musicFolderName): # we check if folder is exists
                        makedirs(d + self.musicFolderName) # if not we create it
                if not path.exists(d + self.musicFileName): # ans also check if the file is exits
                    with open(d + self.musicFileName, "w") as file: # and if not we create it too
                        file.write(str(1) + MusicTxt.header)
            else:
                return
        # finding game type
        self.game_type = None
        for known_game in self.game_db:
            if known_game in d:  # if game title is in the path, we set it as the current game_type
                self.game_type = known_game
                break
        self.musicTxt = MusicTxt(d + "/music.txt")
        self.musicTxt.order_collection("fileName")
        # if automatic identifying the game was unsuccesful we compare the file content against the type dicts
        if self.game_type is None:
            counters = {}
            for known_game in self.game_db:
                counters[known_game] = {"good": 0, "bad": 0, "rate": 0.0}
            id_list = []
            for track in self.musicTxt.collection_get():
                id_list.append(track.getId())
            id_list = set(id_list)
            for type_id in id_list:
                for known_game in self.game_db:
                    if type_id in self.game_db[known_game]["by_id"]:
                        counters[known_game]["good"] += 1
                    else:
                        counters[known_game]["bad"] += 1
            for known_game in counters:
                counters[known_game]["rate"] = counters[known_game]["good"] / (counters[known_game]["good"] + counters[known_game]["bad"])
            games_by_succes_rate = sorted(counters.keys(), key=lambda item: counters[item]["rate"], reverse=True)
            self.game_type = games_by_succes_rate[0]
            if counters[self.game_type]["rate"] != 1.0:
                messagebox.showinfo(self.conf.ui["gametype_title"].get(), self.conf.ui["gametype"].get())
        self.rownum = 0
        xbutton = Button(self.buttonline, text = "\u2620", relief="flat", command = self.invertSelection)  # 274C
        xbutton.pack(side="left", padx = 2)
        self.titleButton = Button(self.buttonline, textvariable = self.conf.ui["title_asc"], width = 34, command = self.sortByTitle)
        self.titleButton.pack(side="left", padx = 2)
        addbutton = Button(self.buttonline, text = "\u271A", command = self.newRow)
        addbutton.pack(side="left")
        self.topicButton = Button(self.buttonline, textvariable = self.conf.ui["topic"], width = 36, command = self.sortByTopic)
        self.topicButton.pack(side="left", padx = 4)
        fileList = self.readMusicFolder()
        registeredFileList = []
        missingFileCounter = 0
        for track in self.musicTxt.collection_get():
            self.rowdict["pk%s" % self.rownum] = Row(self.mainframe, track)
            self.rowdict["pk%s" % self.rownum].pack()
            registeredFileList.append(track.getFn())
            if track.getFn() not in fileList:
                missingFileCounter += 1
                self.rowdict["pk%s" % self.rownum].isToRemove.set(1)
            self.rownum += 1
        for file in fileList:
            if file not in registeredFileList:
                track = self.musicTxt.addTrack(file, '0 0')
                self.rowdict["pk%s" % self.rownum] = Row(self.mainframe, track)
                self.rowdict["pk%s" % self.rownum].pack()
                self.rownum += 1
        self.showCanvas()
        self.menubar.enabler(True)
        if missingFileCounter > 0:
            messagebox.showwarning(self.conf.ui["missingFilesTitle"].get(), self.conf.ui["missingFiles"].get())
            
    def confirmColse(self):
        """asks the user if he or she wants to discard the unsaved changes"""
        answer = True
        if self.changed:
            answer = messagebox.askyesno(self.conf.ui["question"].get(), self.conf.ui["unsaved"].get())
        return answer
            
    def readLanguages(self):
        """get language files' name from main folder"""
        languageFileDict = {}
        languageFiles = glob("lang-*.xml")
        for file in languageFiles:
            languageFileDict[file[5:-4]] = file
        return languageFileDict
        
    def getLanguageKeys(self):
        """passes the registered languages key sorted"""
        return sorted(self.language.keys())
        
    def scrolling(self, event):
        self.canvas.configure(scrollregion = self.canvas.bbox("all"), width = 580, height = 600)
        
    def set_changed(self):
        self.changed = True
        
    def save(self):
        self.musicTxt.save()
        self.changed = False
        
    def exit(self):
        if not self.confirmColse():
            return
        self.quit()
        
    def about(self):
        messagebox.showinfo(self.conf.ui["businesscard"].get(), "Mount & Blade Music Manager v1.0\n" + self.conf.ui["by"].get() + " Bárdos Dávid")
        
    def sortByTitle(self):
        if self.order[0] == "fileName" and not self.order[1]:
            self.order = ("fileName", True)
            self.titleButton.config(textvariable = self.conf.ui["title_desc"])
        else:
            self.order = ("fileName", False)
            self.titleButton.config(textvariable = self.conf.ui["title_asc"])
        self.topicButton.config(textvariable = self.conf.ui["topic"])
        self.sortList()
        
    def sortByTopic(self):
        if self.order[0] == "id" and not self.order[1]:
            self.order = ("id", True)
            self.topicButton.config(textvariable = self.conf.ui["topic_desc"])
        else:
            self.order = ("id", False)
            self.topicButton.config(textvariable = self.conf.ui["topic_asc"])
        self.titleButton.config(textvariable = self.conf.ui["title"])
        self.sortList()
        
    def sortList(self):
        if "mainframe" in locals():
            self.mainframe.destroy()
        self.mainframe = Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.mainframe, anchor = "nw")
        self.mainframe.bind("<Configure>", self.scrolling)
        self.rownum = 0
        qset = []
        if self.order[0] == "fileName" and len(self.musicTxt.collection) > 0:
            self.musicTxt.order_collection(self.order[0], self.order[1])
            qset = self.musicTxt.collection_get()
        elif len(self.musicTxt.collection) > 0:
            qset = sorted(self.musicTxt.collection_get(), key=lambda track: self.game_db[self.game_type]["by_id"][track.getId()].getName(), reverse = self.order[1])
        for track in qset:
            self.rowdict["pk%s" % self.rownum] = Row(self.mainframe, track)
            self.rowdict["pk%s" % self.rownum].pack()
            self.rownum += 1
    
    def readMusicFolder(self):
        fileList = []
        path = self.musicTxt.getPath()
        for file in listdir(path[:-9] + self.musicFolderName):
            if file.endswith(".mp3") or file.endswith(".ogg") or file.endswith(".wav"):
                fileList.append(file)
        if "Modules" in path:
            for file in listdir(path[:path.find("Modules")] + self.musicFolderName):
                if file.endswith(".mp3") or file.endswith(".ogg") or file.endswith(".wav"):
                    fileList.append(file)
        return fileList
        
    def changeLanguage(self, languageCode = "EN"):
        if self.languageIsSet:
            self.conf.setLanguageCode(languageCode)
            self.conf.loadLanguage(False)
            self.menubar.loadText()
            self.game_db = self.conf.readTypes()
            self.sortList()
        else:
            self.languageIsSet = True     
    
    def invertSelection(self):
        for row in self.rowdict.keys():
            self.rowdict[row].isToRemove.set(not self.rowdict[row].isToRemove.get())
            
    def newRow(self):
        """creates a new row and track objects"""
        track = self.musicTxt.addTrack("noFileSelected.yet", '0 0')
        self.rowdict["pk%s" % self.rownum] = Row(self.mainframe, track)
        self.rowdict["pk%s" % self.rownum].browseFile()
        self.rowdict["pk%s" % self.rownum].pack()
        self.rownum += 1
    
class AppMenu(Menu):
    """menubar"""
    def __init__(self, master):
        Menu.__init__(self, master = master)
        self.master = master
        languages = master.getLanguageKeys()
        self.filemenu = Menu(self, tearoff = 0)
        self.filemenu.add_command(command = master.openModule)
        self.filemenu.add_command(command = master.save, state="disabled")
        self.filemenu.insert_separator(3)
        self.filemenu.add_command(command = master.exit)        
        self.add_cascade(menu = self.filemenu)
        self.language = Menu(self, tearoff = 0)
        for lang in languages:
            self.language.add_radiobutton(label = lang, command = lambda x = lang : master.changeLanguage(x))
        self.language.invoke(languages.index(master.conf.getLanguageCode()))
        self.appmenu = Menu(self, tearoff = 0)
        self.appmenu.add_cascade(menu = self.language)
        self.appmenu.add_command(command = master.about)
        self.add_cascade(menu = self.appmenu)
        self.loadText()

    def loadText(self):
        self.filemenu.entryconfig(0, label = self.master.conf.ui["open"].get())
        self.filemenu.entryconfig(1, label = self.master.conf.ui["save"].get())
        self.filemenu.entryconfig(3, label = self.master.conf.ui["exit"].get())
        self.entryconfig(1, label = self.master.conf.ui["module"].get())  
        self.appmenu.entryconfig(0, label = self.master.conf.ui["language"].get())
        self.appmenu.entryconfig(1, label = self.master.conf.ui["about"].get())
        self.entryconfig(2, label = self.master.conf.ui["application"].get())
        
    def enabler(self, enable = True):
        """enables or disables menu items"""
        if enable:
            self.filemenu.entryconfig(1, state="normal")
        else:
            self.filemenu.entryconfig(1, state="disabled")
        
class Config():
    """settings"""
    def __init__(self):
        self.cfgName = "config.xml"
        self.ui = {}
        self.file = parse(self.cfgName)
        self.root = self.file.getroot()
        self.languageCode = self.root.find("language").text
        self.loadLanguage()
        
    def loadLanguage(self, initialLoad = True):
        """loading language resources"""
        file = parse("lang-%s.xml" % self.languageCode)
        root = file.getroot()
        for item in root.findall("item"):
            id = item.get("id")
            text = item.text
            if initialLoad:
                self.ui[id] = StringVar()
                if id in ["title", "topic"]:
                    self.ui[id + "_asc"] = StringVar()
                    self.ui[id + "_desc"] = StringVar()
            self.ui[id].set(text)
            if id in ["title", "topic"]:
                self.ui[id + "_asc"].set(text + " \u25B2")
                self.ui[id + "_desc"].set(text + " \u25BC")
            
    def getLanguageCode(self):
        return self.languageCode
        
    def setLanguageCode(self, newCode):
        self.languageCode = newCode
        self.saveConfig()
        
    def saveConfig(self):
        cfg = Element('config')
        file = ElementTree(cfg)
        lang = SubElement(cfg, 'language')
        lang.text = self.languageCode
        file.write(self.cfgName, xml_declaration = True, encoding = 'utf-8', method = 'xml')
        
    def readTypes(self):
        """reads the types dictionary from XML and returns it"""
        file = parse("types-%s.xml" % self.languageCode)
        root = file.getroot()
        game_db = {}
        for game_type in root.findall("types"):
            game_name = game_type.get("game")
            game_db[game_name] = {"by_type": {}, "by_id": {}}
            for item in game_type.findall("item"):
                id = item.get("id")
                text = item.text
                newType = Type(text, id)
                game_db[game_name]["by_type"][text] = newType
                game_db[game_name]["by_id"][id] = newType
        return game_db

class Row(Frame):
    """widget that displays a Track object as a row"""    
    def __init__(self, master, track):
        Frame.__init__(self, master = master)
        self.root = master.master.master.master
        self.track = track # putting a track to a var
        self.isToRemove = IntVar()
        self.isToRemove.set(self.track.getIsToRemove())
        self.isToRemove.trace("w", self.checkbuttonOnChange)
        chkbx = Checkbutton(self, variable = self.isToRemove)
        chkbx.pack(side="left")
        # Trackname
        self.titleVar = StringVar() # getting a var for onChange event
        self.titleVar.set(self.track.fileName) # setting default value
        self.titleVar.trace("w", self.titleVar_onchange) # binding to onChange event
        self.title = Entry(self, textvariable = self.titleVar, width = 40) # creating form element
        self.title.pack(side="left")
        # Browse button
        self.threedots = Button(self, text = "...", command = self.browseFile)
        self.threedots.pack(side="left", padx = 5)
        # Dropdown for type
        self.typeVar = StringVar()
        if self.track.id not in self.root.game_db[self.root.game_type]["by_id"].keys():
            self.track.setId("0 0")
        self.typeVar.set(self.root.game_db[self.root.game_type]["by_id"][self.track.id].getName())
        self.typeVar.trace("w", self.typeVar_onchange)  # binding to onChange event
        self.type = Combobox(self, textvariable=self.typeVar, width = 40)
        self.type['values'] = sorted(self.root.game_db[self.root.game_type]["by_type"].keys())
        if self.isToRemove.get():
            for var in [self.title, self.threedots, self.type]:
                var.config(state = "disabled")
        self.type.pack(side="left")
        
    def titleVar_onchange(self, a, b, c):
        """onChange event for titleVar"""
        self.track.setFn(self.titleVar.get())
        self.root.set_changed()
        
    def typeVar_onchange(self, a, b, c):
        """onChange event for typeVar"""
        self.track.setId(self.root.game_db[self.root.game_type]["by_type"][self.typeVar.get()].getId())
        self.root.set_changed()
        
    def removeTrack(self):
        """removes the current track from the collection"""
        self.root.musicTxt.removeTrack(self.track)
        
    def checkbuttonOnChange(self, a, b, c):
        """enables, disables row"""
        if self.isToRemove.get():
            self.track.setIsToRemove()
            newState = "disabled"
        else:
            newState = "normal"
            self.track.setIsToRemove(False)
        for var in [self.title, self.threedots, self.type]:
            var.config(state = newState)
            
    def browseFile(self):
        """let users pick additional files from disk"""
        filepath = filedialog.askopenfilename(parent = self.root, filetypes = [("MP3 " + self.root.conf.ui["files"].get(), ".mp3"), ("OGG " + self.root.conf.ui["files"].get(), ".ogg"), ("WAV " + self.root.conf.ui["files"].get(), ".wav")])
        if filepath:
            filename = filepath.rsplit('/', 1)[1].replace(" ","_").replace("'", "")
            newfile = copy2(filepath, self.root.musicTxt.getPath()[:-9] + self.root.musicFolderName + '/' + filename)
            self.titleVar.set(filename)
        else:
            return

class Type():
    """a simple Type object"""
    def __init__(self, name, id):
        self.name = name
        self.id = id
        
    def getName(self):
        return self.name
        
    def getId(self):
        return self.id        
        
class MusicTxtPalceHolder():
    """enables some functions before a real MusicTxt object is opened"""
    def __init__(self):
        self.collection = []

    def save(save):
        pass

if __name__ == "__main__":
    a = AppWindow()
    a.mainloop()