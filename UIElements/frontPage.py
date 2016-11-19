'''

This module defines the appearance and function of the front page of the program.

This page is used to manually move the machine, see the positional readout, and view the file being cut

'''

from kivy.uix.screenmanager                    import Screen
from kivy.properties                           import ObjectProperty, StringProperty
from DataStructures.makesmithInitFuncs         import MakesmithInitFuncs
from kivy.uix.popup                            import Popup
from UIElements.touchNumberInput               import TouchNumberInput
import re

class FrontPage(Screen, MakesmithInitFuncs):
    textconsole    = ObjectProperty(None)
    connectmenu    = ObjectProperty(None) #make ConnectMenu object accessible at this scope
    gcodecanvas    = ObjectProperty(None) 
    screenControls = ObjectProperty(None) 
    
    target = [0,0,0]
    
    connectionStatus = StringProperty("Not Connected")
    
    xReadoutPos = StringProperty("0 mm")
    yReadoutPos = StringProperty("0 mm")
    zReadoutPos = StringProperty("0 mm")
    
    numericalPosX  = 0.0
    numericalPosY  = 0.0
    
    stepsizeval = 0
    feedRate = 0
    
    shiftX = 0
    shiftY = 0
    
    consoleText = StringProperty(" ")
    
    units = StringProperty("MM")
    gcodeLineNumber = StringProperty('0')
    
    INCH            = 25.4
    MILLIMETER       = 1 
    
    def __init__(self, data, **kwargs):
        super(FrontPage, self).__init__(**kwargs)
        self.data = data
    
    def setPosReadout(self, xPos, yPos, zPos, units):
        self.xReadoutPos    = str(xPos) + " " + units
        self.yReadoutPos    = str(yPos) + " " + units
        self.zReadoutPos    = str(zPos) + " " + units
        self.numericalPosX  = xPos
        self.numericalPosY  = yPos
    
    def setTarget(self, xval,yval,zval,units):
        if self.target[0] == 0 and self.target[1] == 0:
            print "first run"
            if units == "MM":
                self.target[0] = xval
                self.target[1] = yval
            elif units == "INCHES":
                self.target[0] = xval
                self.target[1] = yval
            
            print xval
            print self.target[0]
            print self.target[1]
            
            
    
    def setUpData(self, data):
        self.gcodecanvas.setUpData(data)
        self.screenControls.setUpData(data)
        self.data.bind(connectionStatus = self.updateConnectionStatus)
        self.data.bind(units            = self.onUnitsSwitch)
        self.data.bind(gcodeIndex       = self.onIndexMove)
    
    def updateConnectionStatus(self, callback, connected):
        
        if connected:
            self.connectionStatus = "Connected"
        else:
            self.connectionStatus = "Connection Lost"
    
    def switchUnits(self):
        if self.data.units == "INCHES":
            self.data.units = "MM"
        else:
            self.data.units = "INCHES"
    
    def onUnitsSwitch(self, callback, newUnits):
        self.units = newUnits
        #the behavior of notifying the machine doesn't really belong here
        #but I'm not really sure where else it does belong
        if newUnits == "INCHES":
            self.data.gcode_queue.put('G20 ')
            self.moveDistInput.text = str(float(self.moveDistInput.text)/25)
        else:
            self.data.gcode_queue.put('G21 ')
            self.moveDistInput.text = str(float(self.moveDistInput.text)*25)
    
    def onIndexMove(self, callback, newIndex):
        self.gcodeLineNumber = str(newIndex)
    
    def moveGcodeIndex(self, dist):
        self.data.gcodeIndex = self.data.gcodeIndex + dist
        gCodeLine = self.data.gcode[self.data.gcodeIndex]
        print gCodeLine
        
        xTarget = 0
        yTarget = 0
        
        x = re.search("X(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if x:
            xTarget = float(x.groups()[0])
        
        y = re.search("Y(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if y:
            yTarget = float(y.groups()[0])
        
        self.gcodecanvas.targetIndicator.setPos(xTarget,yTarget,self.data.units)
    
    def pause(self):
        self.data.uploadFlag = 0
        self.data.quick_queue.put("STOP") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
        print("Run Paused")
    
    def jmpsize(self):
        try:
            self.stepsizeval = float(self.moveDistInput.text)
        except:
            pass
        try:
            self.feedRate = float(self.moveSpeedInput.text)
        except:
            pass
    
    def upLeft(self):
        self.jmpsize()
        xtarget = -1*self.target[0] - float(self.stepsizeval)
        ytarget = self.target[1] + float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = self.target[0] + float(self.stepsizeval)
        self.target[1] = self.target[1] + float(self.stepsizeval)
        
    def upRight(self):
        self.jmpsize()
        xtarget = -1*self.target[0] + float(self.stepsizeval)
        ytarget = self.target[1] + float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = self.target[0] - float(self.stepsizeval)
        self.target[1] = self.target[1] + float(self.stepsizeval)

    def up(self):
        self.jmpsize()
        target = self.target[1] + float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " Y" + str(target) + " ")
        self.target[1] = self.target[1] + float(self.stepsizeval)

    def left(self):
        self.jmpsize()
        target = -1*self.target[0] - float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(target) + " ")
        self.target[0] = self.target[0] + float(self.stepsizeval)
        print self.target[0]
        
    def right(self):
        self.jmpsize()
        target = -1*self.target[0] + float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(target) + " ")
        self.target[0] = self.target[0] - float(self.stepsizeval)
        
    def downLeft(self):
        self.jmpsize()
        xtarget = -1*self.target[0] - float(self.stepsizeval)
        ytarget = self.target[1] - float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = self.target[0] + float(self.stepsizeval)
        self.target[1] = self.target[1] - float(self.stepsizeval)    

    def down(self):
        self.jmpsize()
        target = self.target[1] - float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " Y" + str(target) + " ")
        self.target[1] = self.target[1] - float(self.stepsizeval)

    def downRight(self):
        self.jmpsize()
        xtarget = -1*self.target[0] + float(self.stepsizeval)
        ytarget = self.target[1] - float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = self.target[0] - float(self.stepsizeval)
        self.target[1] = self.target[1] - float(self.stepsizeval)

    def zUp(self):
        self.jmpsize()
        target = self.target[2] + 0.10*float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " Z" + str(target) + " ")
        self.target[2] = self.target[2] + 0.10*float(self.stepsizeval)

    def zDown(self):
        self.jmpsize()
        target = self.target[2] - 0.10*float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " Z" + str(target) + " ")
        self.target[2] = self.target[2] - 0.10*float(self.stepsizeval)

    def home(self):
        if self.target[2] < 0:
            self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " Z0 ")
            self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X0 Y0 Z0 ")
        if self.target[2] >= 0:
            self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X0 Y0 ")
            self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " Z0 ")
        self.target[0] = 0.0
        self.target[1] = 0.0
        self.target[2] = 0.0
    
    def reZero(self): 
        self.target = [0,0,0]
        
        self.data.gcode_queue.put("G10 X0 Y0 Z0 ")
    
    def moveLine(self, gcodeLine, moveXBy, moveYBy):
        
        originalLine = gcodeLine
        
        try:
            gcodeLine = gcodeLine.upper() + " "
            
            
            x = gcodeLine.find('X')
            if x != -1:
                space = gcodeLine.find(' ', x)
                number = float(gcodeLine[x+1:space]) + moveXBy
                gcodeLine = gcodeLine[0:x+1] + str(number) + gcodeLine[space:]
            
            y = gcodeLine.find('Y')
            if y != -1:
                space = gcodeLine.find(' ', y)
                number = float(gcodeLine[y+1:space]) + moveYBy
                gcodeLine = gcodeLine[0:y+1] + str(number) + gcodeLine[space:]
            
            return gcodeLine
        except ValueError:
            print "line could not be moved:"
            print originalLine
            return originalLine
    
    def moveOrigin(self):
        
        if self.data.units == "INCHES":
            amtToShiftX = self.numericalPosX - self.shiftX
            amtToShiftY = self.numericalPosY - self.shiftY
            self.shiftX = self.shiftX + amtToShiftX
            self.shiftY = self.shiftY + amtToShiftY
        else:
            amtToShiftX = self.numericalPosX - self.shiftX
            amtToShiftY = self.numericalPosY - self.shiftY
            self.shiftX = self.shiftX + amtToShiftX
            self.shiftY = self.shiftY + amtToShiftY
        
        shiftedGcode = []
        
        for line in self.data.gcode:
            shiftedGcode.append(self.moveLine(line , amtToShiftX, amtToShiftY))
        
        self.data.gcode = shiftedGcode
    
    def startRun(self):
        
        self.data.uploadFlag = 1
        self.sendLine()
    
    def sendLine(self):
        try:
            self.data.gcode_queue.put(self.data.gcode[self.data.gcodeIndex])
            self.data.gcodeIndex = self.data.gcodeIndex + 1
        except:
            print "gcode run complete"
            self.gcodecanvas.uploadFlag = 0
            self.data.gcodeIndex = 0
    
    def stopRun(self):
        self.data.uploadFlag = 0
        self.data.gcodeIndex = 0
        self.data.quick_queue.put("STOP") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
        print("Gode Stopped")
    
    def textInputPopup(self, target):
        
        self.targetWidget = target
        
        self.popupContent = TouchNumberInput(done=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=self.popupContent,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up
        
        '''
        
        self.targetWidget.text = self.popupContent.textInput.text
        self._popup.dismiss()