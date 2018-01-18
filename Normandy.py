#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 16:47:26 2017

@author: Lakshmi 

"""

from OfQ import mdp
from OfQ import _object
from OfQ import object_class
import csv

actlist = ["Up", "Down", "Left", "Right", "Wait"]
                                   
terminals = [(2,0),(1,0),(3,1)]
agent_start = (0,0)
gamma = 0.99

#Define these based on the game
enemies = object_class("Enemies") #Enemies class
gold = object_class("Gold") #Final gold class

o1 = _object("Bullet1", enemies, (2,0), -100)
o2 = _object("Bullet2", enemies, (3,0), -100)
o3 = _object("Gold1", gold, (4,1), 100)

#Create object array
objects = [o1, o2, o3]
classes = [enemies, gold]

obj_dict = {}

for c in classes:
    obj_dict.update({c.class_ID:{}})

#Human demonstration in Normandy game domain

bullet = '->'
agent = 'A '
gold = 'G ' 

grid_template = [['  ','  ','  ','  '],
                 ['  ','  ','  ','  '],
                 ['  ','  ','  ','  '],
                 ['  ','  ','  ','  '],
                 ['  ','  ','  ','  ']]

Normandy_mdp = mdp(grid_template, terminals, actlist, objects, agent_start, gamma)

def update_grid(grid, mdp):
    grid_display = [['  ','  ','  ','  '],
                    ['  ','  ','  ','  '],
                    ['  ','  ','  ','  '],
                    ['  ','  ','  ','  '],
                    ['  ','  ','  ','  ']]
    grid_display.reverse()
    for obj in objects:
        if obj._class.class_ID == "Enemies":
            grid_display[obj.state1[0]][obj.state1[1]] = bullet
        elif obj._class.class_ID == "Gold":
            grid_display[obj.state1[0]][obj.state1[1]] = gold
            
    agent_state = mdp.agent_state
    grid_display[agent_state[0]][agent_state[1]] = agent
    grid_display.reverse()
    return grid_display

while True:
        
    grid_new = update_grid(grid_template, Normandy_mdp)
    
    for line in grid_new:
        print line
    
    if Normandy_mdp.agent_state in Normandy_mdp.terminals:
        print "Game complete"
        break
    
    user_input = raw_input("Enter the action: ")
    
    while user_input not in actlist and user_input != 'x':
        print "Invalid action"
        user_input = raw_input("Enter valid action: ")
        
    if user_input == 'x':
        break
    
    for o in objects:
        obj_dict[o._class.class_ID].update({(Normandy_mdp.agent_state, o.state1):user_input})
        
    Normandy_mdp.TakeAction(user_input)
   
with open('Obj_aff.csv', 'wb') as f:
    writer = csv.writer(f)
    for row in obj_dict.iteritems():
        writer.writerow(row)
    
    
        
            
