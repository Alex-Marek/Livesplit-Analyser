from bs4 import BeautifulSoup
from bs4 import Tag
from datetime import datetime
from collections import defaultdict

class splits_File:
    completedRuns = [int]
    segmentInfo = {}           #string:bool
    foundSubsplits = False
    runs = {}

class run:
    segments = {}
    superSegments = {}
    goldCount = 0
    finalMap = None
    length = 0
    def __init__(self,id, s_Date, e_Date, p_BAT, gT, rT, pT, isComp):
        self.attemptID = id
        self.startDate = s_Date
        self.endDate = e_Date
        self.personalBestAtTime = p_BAT
        self.gameTime = gT
        self.realTime = rT
        self.pauseTime = pT
        self.isCompleted = isComp

    def loadSegmentInfo(self, segmentInfo):    
        newSegments = newSuperSegments = defaultdict(segment)
        blankSegment = segment()
        for value in segmentInfo:
            if value == True:
                newSuperSegments[value] = blankSegment
            else:
                newSegments[value] = blankSegment
        self.segments = newSegments
        self.superSegments = newSuperSegments

    def printRunInfo(self):
        print(f"ID:{self.attemptID}, \nStartDate:{self.startDate}, \nEndDate:{self.endDate}, \nPB:{self.personalBestAtTime}, \nGameTime:{self.gameTime}, \nCompleted:{self.isCompleted}\n")

class segment:
    def __init__(self):
        self.name = ""
        self.realTime = None
        self.gameTime = None
        self.wasGold = False



def findSplits(segs):
    segmentInfo = {}
    foundSubsplits = False
    if type(segs) == Tag:
        segNames = segs.find_all("Name")
        for value in segNames:
            value = value.getText()
            if value.find("{") > -1 and value.find("}") > -1:
                foundSubsplits = True
                segmentInfo[value] = True
            else:
                segmentInfo[value] = False
    res = [segmentInfo, foundSubsplits]
    return res




def readAttemptHistory(attempts, segInfo):
    runs = {}
    personalBest = ""
    for attem in attempts:
        if type(attem) == Tag:
            isComp = False
            id = attem.get("id")
            if id != None: id = int(id)
            convEnded = attem.get("ended")
            convStart = attem.get("started")
            if convEnded != None: convEnded = datetime.strptime(convEnded, "%m/%d/%Y %H:%M:%S")
            if convStart != None: convStart = datetime.strptime(convStart, "%m/%d/%Y %H:%M:%S")
            if len(attem) != 0:
                isComp = True
                gamTim = attem.find("GameTime")
                relTim = attem.find("RealTime")
                pauTim = attem.find("PauseTime")
                if gamTim != None: gamTim = datetime.strptime(gamTim.getText()[:-4], "%H:%M:%S.%f").time()
                if relTim != None: relTim = datetime.strptime(relTim.getText()[:-4], "%H:%M:%S.%f").time()
                if pauTim != None: pauTim = datetime.strptime(pauTim.getText()[:-4], "%H:%M:%S.%f").time()
                if gamTim != None:
                    if personalBest == "" or gamTim < personalBest:
                        personalBest = gamTim
            newRun = run(id,convStart, convEnded,personalBest,gamTim, relTim, pauTim, isComp)
            newRun.loadSegmentInfo(segInfo)
            runs[id] = newRun
    return runs


def readSegmentHistory(segData, runs):
    for seg in segData:
        name = seg.find("Name").getText()
        segHistory = seg.find_all("Time")
        for attemptTimes in segHistory:
            realTimeGold = ""
            gameTimeGold = ""
            id = attemptTimes.get("id")
            realTime = attemptTimes.find("RealTime").getText()
            gameTime = attemptTimes.find("GameTime").getText()
            #Livesplit removes the ms if it's exactly 0 CRINGE
            if realTime.find(".") == -1:
                realTime += ".0000000"
            if gameTime.find(".") == -1:
                gameTime += ".0000000"
            gameTime = datetime.strptime(gameTime[:-4], "%H:%M:%S.%f").time()
            realTime = datetime.strptime(realTime[:-4], "%H:%M:%S.%f").time() 
            
            if realTimeGold == "":
                realTimeGold = realTime
            if gameTimeGold == "":
                gameTimeGold = gameTime
            
            print(id, name, realTime, gameTime)
        print("\n")



def main():
    s_File = splits_File()
    with open("6aa1.lss", 'r') as f:
        data = f.read()
        bs_Data = BeautifulSoup(data,'xml')
        # Find all Split names and whether they're supersplits
        s_File.segmentInfo, s_File.foundSubsplits = findSplits(bs_Data.find("Segments"))
        # Read through attempt history to get a glossary of all runs in the splits
        s_File.runs = readAttemptHistory( bs_Data.find_all("AttemptHistory")[0], s_File.segmentInfo)
        # Now to read through the split history into the runs
        readSegmentHistory(bs_Data.find_all("Segment"), s_File.runs)







if __name__ == "__main__":
    main()
