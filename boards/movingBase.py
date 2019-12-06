from boards.board import Board
import time


class MovingBase(Board):

    def __init__(self, nom, fonction, communication, param1=None, param2=None):
        Board.__init__(self, nom, fonction, communication, param1, param2)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication
        self._isXYSupported = None
        self._isPathSupported = None

    def enableMovements(self):
        if self.isConnected():
            self.sendMessage("move enable")
            echo = ""
            echo = self.receiveMessage()  # "move OK"
            if "move OK" not in echo: #if ERROR is received, retry
                time.sleep(0.1)
                print "retry enableMovements("+echo+")"
                return self.enableMovements()
            return True

    def disableMovements(self):
        if self.isConnected():
            self.sendMessage("move disable")
            echo = ""
            echo = self.receiveMessage()  # "move OK"
            if "move OK" not in echo: #if ERROR is received, retry
                time.sleep(0.1)
                print "retry disableMovements("+echo+")"
                return self.disableMovements()
            return True

    def setPosition(self, x, y, angle):
        if self.isConnected():
            self.sendMessage("pos set {:.0f} {:.0f} {:.0f}".format(x, y, angle))
            echo = ""
            echo = self.receiveMessage()  # "position OK"
            if "pos OK" not in echo: #if ERROR is received, retry
                time.sleep(0.1)
                print "retry setPosition("+echo+")"
                return self.setPosition(x, y, angle)
            return True

    def setSpin(self, direction, speed):
        if self.isConnected():
            self.sendMessage("spin {:.0f} {:.0f}".format(direction, speed))
            echo = ""
            echo = self.receiveMessage()  # "spin OK"
            if "spin OK" not in echo: #if ERROR is received, retry
                time.sleep(0.1)
                print "retry setSpin("+echo+")"
                return self.setSpin(direction, speed)
            return True

    def getPositionXY(self):
        if self.isConnected():
            self.sendMessage("pos getXY")
            position = ""
            position = self.receiveMessage()  # "position x;y;angle;speed"
            if "pos" not in position: #if ERROR is received, retry
                time.sleep(0.1)
                print "retry getPositionXY("+position+")"
                return self.getPositionXY()
            #print position
            values = position.split(" ")
            x = float(values[1])
            y = float(values[2])
            angle = float(values[3])
            speed = float(values[4])/10.0
            return x, y, angle, speed

    def getPositionDistanceAngle(self):
        if self.isConnected():
            self.sendMessage("pos getDA")
            position = ""
            position = self.receiveMessage()  # "position distance;angle;speed"
            if "pos" not in position: #if ERROR is received, retry
                time.sleep(0.1)
                print "retry getPositionDistanceAngle("+position+")"
                return self.getPositionDistanceAngle()
            values = position.split(" ")
            distance = float(values[1])
            angle = float(values[2])
            speed = float(values[3])/10.0
            return distance, angle, speed

    def startMovementXY(self, x, y, angle, speed):
        if self.isConnected():
            if self.isXYSupported():
                self.sendMessage("move XY {:.0f} {:.0f} {:.0f} {:.0f}".format(x,y,angle,speed*10.0))
                echo = ""
                echo = self.receiveMessage()  # "move OK"
                if "move OK" not in echo:  # if ERROR is received, retry
                    time.sleep(0.1)
                    print "retry startMovementXY("+echo+")"
                    return self.startMovementXY(x, y, angle, speed)
                return True
            else:
                print("ERROR: XY move not supported")
                return False

    def startMovementDistanceAngle(self, distance, angle, speed):
        if self.isConnected():
            self.sendMessage("move DA {:.0f} {:.0f} {:.0f}".format(distance,angle,speed*10.0))
            echo = ""
            echo = self.receiveMessage()  # "move OK"
            if "move OK" not in echo:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry startMovementDistanceAngle("+echo+")"
                return self.startMovementDistanceAngle(distance, angle, speed)
            return True

    def getMovementStatus(self):
        if self.isConnected():
            self.sendMessage("move status")
            status = ""
            status = self.receiveMessage()  # "move running" "move stuck" "move finished"
            if "move" not in status:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry getMovementStatus("+status+")"
                return self.getMovementStatus()
            return status.split(" ")[1]

    def getSpeed(self):
        if self.isConnected():
            self.sendMessage("speed get")
            speed = ""
            speed = self.receiveMessage()  # "speed 0.3"
            if "speed" not in speed:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry getSpeed("+speed+")"
                return self.getSpeed()
            value = float(speed.split(" ")[1])/10.0
            return value

    def emergencyBreak(self):
        if self.isConnected():
            self.sendMessage("move break")
            echo = ""
            echo = self.receiveMessage()  # "move OK"
            if "move OK" not in echo:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry emergencyBreak("+echo+")"
                return self.emergencyBreak()
            return True

    def startRepositioningMovement(self, distance, speed=0.2):  # recallage. Movement where the robot is expected to be stuck
        if self.isConnected():
            self.sendMessage("move RM {:.0f} {:.0f}".format(distance,speed*10))
            echo = ""
            echo = self.receiveMessage()  # "move OK"
            if "move OK" not in echo:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry startRepositioningMovement("+echo+")"
                return self.startRepositioningMovement(distance, speed)
            return True

    def isXYSupported(self):
        if self._isXYSupported is None and self.isConnected():
            self._isXYSupported = False
            self.sendMessage("support XY")
            support = ""
            support = self.receiveMessage()  # "support 0" or "support 1"
            if "support" not in support:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry isXYSupported("+support+")"
                return self.isXYSupported()
            if "1" in support:
                self._isXYSupported = True
        return self._isXYSupported

    def isPathSupported(self):
        if self._isPathSupported is None and self.isConnected():
            self._isPathSupported = False
            self.sendMessage("support Path")
            support = ""
            support = self.receiveMessage()  # "support 0" or "support 1"
            if "support" not in support:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry isPathSupported("+support+")"
                return self.isPathSupported()
            if "1" in support:
                self._isPathSupported = True
        return self._isPathSupported

    def startMovementPath(self, pathArray):
        if self.isConnected():
            if self.isPathSupported():
                command = "move setPath {}|".format(len(pathArray))
                for move in pathArray:
                    command += "{};{};{};{}|".format(move.x,move.y,move.angle, move.speed)
                self.sendMessage(command)
                echo = ""
                echo = self.receiveMessage()  # "move OK"
                if "move OK" not in echo:  # if ERROR is received, retry
                    time.sleep(0.1)
                    print "retry startMovementPath("+echo+")"
                    return self.startMovementPath(pathArray)
                return True
            else:
                print("ERROR: XY move not supported")
                return False