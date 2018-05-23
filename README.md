# Byo
Welcome to Byo, a MicroPython library for easily configuring Bio-Reactive devices that work as intended. Byo allows anyone with a Pyboard or other MicroPython device to easily configure a bio-reactive user interface using a multitude of sensors, and machine learning to make the user experience as smooth as possible.


# Getting started with Byo
In order to start using Byo, simply copy the files uGestures.py, SensorLib.py, and NBC.py onto your MicroPython device. Once these are loaded on the majority of configuration can be done by importing uGestures and SensorLib into main. Note: NBC.py is a just a data classifier (Naive Bayesian Classifier), and can easily be swapped out for other data classifiers when desired. Here we show you how to configure a Pyboard so that using its user switch quickly adds new gestures.

  
# Step 0: Import to Main
As mentioned above, first all the files must be copied to your Pyboard. Then in main.py, start by importing uGestures and SensorLib, and any other libraries you may want to use. From here we will also instantiate our gesture library G.

  >>>import pyb,utime
  >>>import uGestures,SensorLib
  >>>G = uGestures.Gesture()

# Step 1: Configuring the Sensors
Once everything imports properly, we want to specify our sensors. On the Pyboard, this usually just means specifying the pins that will be used. Currently, sensors can be any object that have a read() method. In the following example we will use two ADC pins (analog to digital conversion) and all three axis of the built in accelerometer as our sensors. 

  >>>raw1 = pyb.ADC(pyb.Pin.board.X3)
  >>>raw2 = pyb.ADC(pyb.Pin.board.X4)
  >>>A = pyb.Accel()
  
Once we have our sensors specified we can package them into a SensorLib object which will handle taking in and organizing all of our sensor data from here.

  >>>S = SensorLib.SensorLib(G,[(raw1,None),(raw2,None),(A,0),(A,1),(A,2)])
  
SensorLib has two arguments. The first is just our Gesture object from before. The second is a list of pairs of the form (SensorObject, Args), where SensorObject is any object with a read() method, and Args is any arguments that will be used when read() is called (specifying None for Args does not pass None, however, it just passes no argument). In our above example, we use the accelerometer object A in three different pairs. This is because A.read(0) gives the x-coordinate, A.read(1) gives the y-coordinate, and A.read(2) gives the z-coordinate. Hence, if we wanted to restrict our accelerometer data to only the x and y coordinates, we woud simply remove the last pair from our list. Once our SensorLib is set up, in REPL we can test if its reading properly with the getsig method.

  >>> S.getsig()                                                                  
  (899, 1345, 1, 2, 23)  
  
SensorLib returns a tuple of all our sensor readings, which is data that we can now pass on to our Gesture object.

# Step 2: Understanding the basic Gesture Object
The Gesture class provides a lot of potential functionality, but at its most basic level it acts as a library to organize and configure your Gesture profiles. For the average user, there are four main stores of data within our Gesture class that will be of interest: gestures, activeGestures, activeStates, and State.  
  -gestures: Stores inactive gesture profiles (gesture profiles that won't be looked at during classification)
  -activeGestures: Stores active Gesture profiles
  -activeStates: Stores functions to be called during a given state of the Gesture object
  -State: an integer variable that represents which state the Gesture object is in
We will focus on the first two for now, as activeStates and State will be illustrated later. Here we will specify how to store gesture profiles. In general the easiest way to do this is through some methods in the SensorLib class (remember it is linked to an instance of Gesture, and therefore has access to these data stores).

First we want to set a base reading which is a collection of sensor data meant to look like random noise (this is used in gesture classification). To do this we use the "start" method in the SensorLib class. Once this method is called, the Pyboard will take in sensor data for about 1 second, and extract its parameters.

  >>> S.start()                                                                   
  >>> G.base_signals                                                              
  {'param': {'means': (689.3499, 1043.0, 1.1, 2.55, 21.75), 'var': (2506.727, 5599.999, 0.5900001, 0.5474999, 0.3875) }

We can then check if it worked in REPL by checking that G.base_signals is not empty. Now we can add our first Gesture. For simplicity we will make it an active Gesture (inactive Gestures we will discuss later). To do this use the "add_state_raw" method in SensorLib. It takes a string argument to be used as the name of that gesture, and if left blank you will be prompted to input a name in REPL. Once this method is called, the Pyboard will start reading sensor data for roughly 1 second, and construct your gesture profile.

  >>> S.add_state_raw("g1")                                                       
  >>> G.activeGestures                                                            
  {'g1': {'name': 'g1', 'param': {'means': (690.35, 1043.65, 1.0, 2.45, 21.55), 'var': (2384.827, 5344.527, 0.5, 0.6474999, 0.3475)}, 'actions':}
  
Once we have gestures, in principle we can start classifying data, although generally we will be using more than one gesture profile to compare with. To classify, simply pass a data point to the "getclass" method in G. Here we use the "getsig" method in S to retrieve our datapoint
  




