# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 11:38:32 2017

@author: laksh
"""

from OfQ import mdp
from OfQ import _object
from OfQ import OfQ_Learning
from OfQ import object_class

actlist = ["Up", "Down", "Left", "Right", "Wait"]
grid = [[-0.04, -0.04, -0.04, -0.04],
        [-0.04, -0.04, -0.04, -0.04],
        [-0.04, -0.04, -0.04, -0.04],
        [-0.04, -0.04, -0.04, -0.04]]
#        [-0.04, -0.04, -0.04, -0.04]]
                                   
terminals = [(2,0),(1,0),(3,1)]
agent_start = (1,1)
gamma = 0.9

#Define these based on the game
enemies = object_class("Enemies") #Enemies class
gold = object_class("Gold") #Final gold class

o1 = _object("Bullet1", enemies, (2,0), -100)
o2 = _object("Bullet2", enemies, (3,0), -100)
o3 = _object("Gold1", gold, (4,1), 100)

#Create object array
objects = [o1, o2, o3]
classes = [enemies, gold]

Normandy_mdp = mdp(grid, terminals, actlist, objects, agent_start, gamma)

o_learner = OfQ_Learning(Normandy_mdp, classes, 50, 10)
o_learner.OFQrun()

