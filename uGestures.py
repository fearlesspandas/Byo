'''
Gestures allows for the construction of custom gesture profiles, while also providing a simple classifier for distinguishing between
profiles. The classifier used currently is NBC (Naive Bayesian Classification), and the structure of the Gestures is set up to
reflect that. Changing classification systems entails defining a new classifier class structure, then initializing Gestures with that
classifier instead of NBC (see __init__ in Gestures). The new classifier needs to define at least two functions: "getclass(x)", and "getdistparam(L)".

The first function "getclass(x)" defines a way for Gestures to classify new data from its gesture library. This returns the gesture profile that is the class of an incoming
datapoint. The second function, getdistparam(L) a function that takes in a list of sample data, and constructs parameters for that data to be used in classification.
See their respective definitions in NBC as an example.

'''
import math
import pyb
import NBC
#lib = c.CDLL('./LibGestures.so')

class Gesture:
    def __init__(self,N,ser_):
        self.numTests = N
        self.gest = [None for i in range(0,N)]
        self.state = 0
        self.gestures = {}
        self.activeGestures = {}
        self.activeStates={}
        self.Histogram = {y:0 for y in self.activeGestures}
        self.imugestures= []
        self.raw_gesture = []
        self.base_signals = {}
        self.classifier = NBC.NBC(self) #links classifier to Gesture instance, so that classifier can use base signals/gesture library
        self.ser = ser_ #serial communication line for raw data
    '''
    Gesture specific class structure in Python.

    The gesture library (activeGestures + gestures) are structured as a dictionary with parameters {["name"]:["param"]["actions"]}
    i.e. each gesture "name" is associated with some parameters that describe its data, and "actions", the functions that we want called
    when that gesture is activated.

    The state library (activeStates) are functions that can be passed onto a gesture instance G, where G has an internal method doState()
    which calls the proper function for whatever the value of G.state is. Each state function must take G as a parameter. G.state can be set
    externally, or within state functions allowing two states to be "linked" (i.e. one state induces another). Note, the control logic can
    be handled entirely externally from G if desired. However, using the state library means the main loop for the controller has to simply
    specify its state functions, and then repeatedly call G.doState()
    '''
    def updateHistogram(self):
        self.Histogram = {y:0 for y in self.activeGestures}
    def zeroHistogram(self):
        for y in self.Histogram:
            self.Histogram[y] = 0
    def totalGestures(self):
        return len(self.gestures) + len(self.activeGestures)
    def add_state(self,index,f,Link = None):
        self.activeStates[index] = {"action":f,"link":Link}
    def doState(self):
        self.activeStates[self.state]["action"](self)
        if not (self.activeStates[self.state]["link"] == None):
            self.state = self.activeStates[self.state]["link"]
    def getclass(self,x,gest_list= None,rettype = None,index = 0):#wrapper for classifier getclass function
        if gest_list == None:
            gest_list = self.activeGestures
        return self.classifier.getclass(x,gest_list,rettype,index)
    def classify(self,x,gest_list= None,rettype = None):
        if gest_list == None:
            gest_list = self.activeGestures
        A = {n:0 for n in gest_list}
        for i in range(0,self.numTests):
            cl = self.classifier.getclass(x,gest_list,rettype,index = i)
            A[cl['name']] = A[cl['name']] + 1
        mostVotes = 0
        mostVoted = None
        for y in A:
            if A[y] >= mostVotes:
                mostVotes = A[y]
                mostVoted = y
        return gest_list[mostVoted]


    #First allows construction of a new state sequence
    #Then takes state sequence and maps it onto an inactive gesture in gestures
    #the chosen gesure is then transferred to the activeGestures
    def add_activeGesture(self,first = False,name = None):
        newstate = {}
        actionQ = []
        if first == 'close':
            newstate["actions"] = [pyb.LED(1).toggle]
            newstate["cycle"] = False
        elif first == "open":
            newstate["actions"] =[pyb.LED(1).off]
            newstate["cycle"] = False
        else:
            x = input("Enter name of Active Gesture to be added to action queue: ")
            while(x!= 'end'):
                for y in self.activeGestures:
                    if y == x:
                        c = y
                        actionQ = actionQ + c["state"]["action"]
                x = input("Press enter to add another state or type 'end' to stop data collection")
            x = input("If this state is to cycle press enter, otherwise type 'single', then press enter")
            if x == 'single':
                newstate["cycle"] = False
            else:
                newstate["cycle"] = True
        if name == None:
            x = input("Enter the name of the (inactive) gesture which will map to this new state: ")
            CC = [y for y in self.gestures if y == x ] #all gestures which share that name
            while len(CC) == 0: #loops until gesture is found
                x = input("Enter the name of the (inactive) gesture which will map to this new state: ")
                CC = [y for y in self.gestures if y == x ]
            c = self.gestures[CC[0]]
        else:
            c = self.gestures[name]
        newstate["name"] = c["name"]
        newstate["param"] = c["param"]
        newstate["actions"] = actionQ
        self.activeGestures[c["name"]] = newstate
        self.gestures.pop(c["name"])

    def modify_gesture(self,g_data = None,name = None):
        if g_data == None:
            g_data = self.classifier.getdistparam(self.raw_gesture)
        if name == None:
            name = input("Pick Gesture you want to modify")
        self.gestures[name]['param'].append(g_data)
    def add_gesture(self,g_data = None,name = None):
        if g_data == None:
            g_data = self.classifier.getdistparam(self.raw_gesture)
            self.raw_gesture.clear()
        if name == None:
            name = input("name your gesture: ")
        newgest = {}
        newgest["name"] = name
        newgest["param"] = g_data
        newgest["actions"] = None
        self.gestures[name] = newgest
        return self.gestures
    def remove_state(self,name): #stores removed gesture in self.gesture for future accessibility
        self.gestures[name] = self.activeGestures[name]
        self.activeGestures.pop(name)

    def set_base_reading(self,g_data = None):
        if g_data == None:
            g_data = self.raw_gesture
        x = self.classifier.getdistparam(g_data)
        self.base_signals["param"] = x
        self.raw_gesture.clear()
