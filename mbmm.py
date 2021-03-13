# Mount & Blade Music Manager - Business logic module
# Written by Bárdos Dávid (2014-2015)
# License: Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
#          http://creativecommons.org/licenses/by-nc-sa/4.0/

class MusicTxt():
    """class of the main data collection"""    
    header = '\ncant_find_this.ogg 0 0\n'
    
    def __init__(self, path = ""):
        self.collection = []
        self.path = path
        readSuccess = self.read(self.path)            
        
    def read(self, path):
        """reading from file"""
        with open(path, "r") as file:
            records = [line.rstrip() for line in file] # reading the lines to a list
        records = list(filter(('').__ne__, records)) # removing empty lines
        first_record = 1
        if " 0 0" in records[1]:
            first_record = 2
        for record in records[first_record:]: # looping through the file
            try:
                name, id = tuple(record.split(' ',1)) # analizing data
            except ValueError:
                name = record
                value = "000"
            self.addTrack(name, id) # generating Tracks
                
    def addTrack(self, name, id = "0 0"):
        """adds a Track to the collection, needs a file name and id as argument"""
        newTrack = Track(name, id)
        self.collection.append(newTrack)
        return newTrack
            
    def removeTrack(self, track):
        """removes a Track from the collection, needs a Track object as argument"""
        self.collection.remove(track)
        
    def order_collection(self, order_by = "", reverse = False):
        """orders the collection by 'fileName' or 'id'"""
        if order_by == "fileName":
            self.collection.sort(key=lambda item: item.fileName.lower(), reverse=reverse)
        else:
            self.collection.sort(key=lambda item: item.id, reverse=reverse)
            
    def backup(self):
        data = ""
        with open(self.path) as original:
            data = original.read()
        with open(self.path + ".original", "w") as backup:
            backup.write(data)
                
    def save(self):
        """exports the collection to file"""
        exportList = []
        for item in self.collection:
            if not item.getIsToRemove() and item.id != "0 0":
                exportList.append(item)
        trackList = sorted(exportList, key = lambda item: item.fileName)
        content = str(len(trackList) +1) + self.header # the plus 1 represents the track in the header
        for track in trackList:
            content += "%s %s\n" % (track.fileName, track.id)
        with open(self.path, "w") as file:
            file.write(content)
            
    def collection_get(self):
        return self.collection
        
    def setPath(self, newPath):
        self.path = newPath
        
    def getPath(self):
        return self.path
        
class Track():
    """class to represent a line"""
    def __init__(self, musicFileName = '', id = '0 0'):
        self.fileName = musicFileName
        self.id = id
        self.isToRemove = False
        
    def save(self):
        """returns the whole line as string for saving the MusicTxt object"""
        value = '%s %s' % (self.fileName, self.id)
        return value
        
    def getFn(self):
        return self.fileName
        
    def setFn(self, newFn = ""):
        self.fileName = newFn
        
    def getId(self):
        return self.id
        
    def setId(self, newId):
        self.id = newId
        
    def setIsToRemove(self, value = True):
        self.isToRemove = value
        
    def getIsToRemove(self):
        return self.isToRemove