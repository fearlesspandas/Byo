
import pyb,utime
import uGestures

class SensorLib:
    def __init__(self,G,SensorList):
        self.sensors = SensorList
        self.G = G
    def getsig(self):
        return  tuple([self.sensors[i][0].read() if (self.sensors[i][1] == None) else self.sensors[i][0].read(self.sensors[i][1]) for i in range(0,len(self.sensors))])
    def read_raw(self,n):
        for i in range(0,n):
            self.G.raw_gesture.append(self.getsig())
            utime.sleep(.1)
    def addSensor(self,Sensr,param):
        self.sensors.append((Sensr,param))

    def add_state_raw(self,name_ = None):
        self.read_raw(20)
        self.G.add_gesture(name = name_)
        self.G.add_activeGesture("close",name = name_)

    def start(self,n = 20):
        self.read_raw(n)
        self.G.set_base_reading()
