#THE DIFFERENT RULE TRANSFER FUNCTIONS ARE HERE

import random
import math

def ExtraAction(obj_aff, Oa, O, A, c):
    #temp_val = 1000
    #temp_object = O[0]
        
    states = obj_aff[c.class_ID]
        
    #WE ASSUME THE ACTION TAKEN IS DIRECTED TOWARDS THE CLOSEST OBJECT
    #for o in O:
    #    if o._class == c and (Oa, o.state1) in states:
    #        dist = distance(Oa, o.state1)
    #        if dist <= temp_val:
    #            temp_val = dist #Closest distance
    #            temp_object = o #Closest object
                    
    #if temp_val != 1000: #Object found in obj_aff
    #    return states[(Oa, temp_object.state1)]
    #else:
    #    return random.choice(A)
        
    for o in O:
        if o._class == c and (Oa, o.state1) in states:
            return states[(Oa, o.state1)]
                
    return random.choice(A)
    
def ValueBonus(obj_aff, Oa, O, A, c):
    states = obj_aff[c.class_ID]
        
    for o in O:
        if o._class == c and (Oa, o.state1) in states:
            return 10, states[(Oa, o.state1)]
                
    return 0, random.choice(A)    

def PPR(obj_aff, Oa, O, A, c):
    states = obj_aff[c.class_ID]
        
    for o in O:
        if o._class == c and (Oa, o.state1) in states:
            return states[(Oa, o.state1)]
                
    return random.choice(A)
            
def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

