#OBJECTS AND OBJECT CLASSES ARE DEFINED HERE

from collections import defaultdict

class _object:
    #Class for defining each object in the game
    def __init__(self, _id, _class, _state, reward):
        self._id = _id
        self._class = _class #Should be an object of object_class
        self.state1 = _state #Current state - position or x,y coordinate
        self.state0 = None   #Old state
        self.reward = reward
        
    def update_object_state(self, state): #probably don't need this
        self.state0 = self.state1
        self.state1 = state
        
class object_class:
    #Defining an object class
    def __init__(self, class_ID):
        self.class_ID = class_ID
        self.Qr = defaultdict(float)
        self.Qc = defaultdict(float)
        self.Tc = 0 #Set to some min value
        self.candidates = [0,0,0]
        
    def getCandidates(self):
        Tc = self.Tc
        return [float(Tc - 0.1*Tc), float(Tc), float(Tc + 0.1*Tc)] 
