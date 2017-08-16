#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 14:42:40 2017

@author: lnair
"""
import csv
import ast
import random
from collections import defaultdict
import numpy as np
from matplotlib import pyplot as plt
import math
#There are three ways of using the decision list and we should compare them all

class OfQ_RT_Learning:
    #Class that defines the Object focused Q learning method
    def __init__(self, mdp, C, Ne, loop, alpha=None, epsilon=0.05):
        self.C = C #Must be an array of _object_class objects
        self.Ne = Ne
        self.gamma = mdp.gamma
        self.all_act = mdp.actlist #Get act list from mdp
        self.epsilon = epsilon
        self.mdp_init = mdp
        self.loop = loop
        self.pi = {}
        self.obj_aff = self.act_read()
        
        if (alpha):
            self.alpha = alpha
        else:
            self.alpha = 0.25 #lambda n: 1./(1+n)    #CHECK HERE
        
    def act_read(self):
        with open('Obj_aff.csv','r') as f:
            reader = csv.reader(f)
            obj_aff = {row[0]:ast.literal_eval(row[1]) for row in reader}
        return obj_aff
            
    def OFQ_RTrun(self):
        alpha, gamma = self.alpha, self.gamma
        Ne, epsilon, loop = self.Ne, self.epsilon, self.loop
        reward_total = []
        class_reward = []
        RT_C = 20
        
        actions_in_state = self.all_act
        GetSafeActions = self.GetSafeActions
        EpsilonGreedy = self.EpsilonGreedy
        UpdateThresholds = self.UpdateThresholds
        expected_reward = self.expected_reward
        ExtraAction = self.ExtraAction
        ValueBonus = self.ValueBonus
        PPR = self.PPR
        
        Q_estimate_r = defaultdict(float)
        Q_estimate_c = defaultdict(float)
        
        T = [c.Tc for c in self.C]  #Not reused in the algorithm either
        for c in self.C:
            Q_estimate_c.update(c.Qc)
            Q_estimate_r.update(c.Qr)        

        for loop_run in range(loop):
            for c in self.C:
                Q_control = Q_estimate_c
                Q_r_control = Q_estimate_r
                candidates = c.getCandidates()
                stats = {}
                for num,i in enumerate(candidates):
                    candidate_reward = 0

                    for j in range(1,Ne):
                        episode_reward = 0
                        B = 0 #Bonus value initalized to 0
                        
                        mdp = self.mdp_init #initialize mdp to the initial mdp states - restart episode
                        Oa_init, O_init = mdp.get_init()
                        s = [Oa_init] + O_init
                        
                        while s[0] not in mdp.terminals:
                            A = GetSafeActions(s, Q_r_control, i)
                            
                            phi = 1/1+j
                            
                            """if loop_run <= RT_C:
                                Oa, O, r1 = mdp.update_percept()
                                #a = ExtraAction(Oa, O, A, c)
                                B,a = ValueBonus(Oa, O , A, c)
                            else:
                                B = 0
                                a = EpsilonGreedy(A, Q_control, s, epsilon)"""
                                
                            rand_num = random.uniform(0,1)
                            if (rand_num < phi):
                                Oa, O, r1 = mdp.update_percept()
                                a = PPR(Oa, O, A, c)
                            else:
                                a = EpsilonGreedy(A, Q_control, s, epsilon)   
                                
                            mdp.TakeAction(a)
                            
                            Oa, O, r1 = mdp.update_percept() #Update state, return agent state and obj_class array
                            
                            if Oa in mdp.terminals:
                                break
                            
                            o_states = [o.state1 for o in O]
                            s = [Oa] + o_states #Update s
                            
                            for o in O:  #Declare O as array of object classes and o is one object class from the array
                                if c == o._class: #previously was c = o._class
                                    cls_idx = self.C.index(c)
                                
                                    #alpha = 1/(1+j)
                                
                                    S0 = (Oa, o.state0)
                                    S1 = (Oa, o.state1)
                                    
                                    c.Qc[(S0,a)] = (1-alpha) * c.Qc[(S0,a)] + alpha * (r1 + gamma * max(c.Qc[(S1,a1)]
                                                                   for a1 in actions_in_state) - c.Qc[(S0,a)]) + B
                
                                    c.Qr[(S0,a)] = (1-alpha) * c.Qr[(S0,a)] + alpha * (r1 + gamma * np.mean([c.Qr[(S1,a1)]
                                                                   for a1 in actions_in_state])) + B
                
                                    #Ensure that actual values are being updated
                                    self.C[cls_idx].Qc[(S0,a)] = c.Qc[(S0,a)]
                                    self.C[cls_idx].Qr[(S0,a)] = c.Qr[(S0,a)]
        
                            episode_reward += r1
                            
                        #End of episode
                        candidate_reward += episode_reward
                    #End evaluations         
                    stats[num] = candidate_reward
                #End of candidate loop
                c.Tc = UpdateThresholds(stats, candidates) 
                class_reward.append(expected_reward(c.Qc))
            #End of class loop
            reward_total.append(-np.mean(class_reward))
        #End of outermost loop
        #print self.C[0].Qc
        plt.plot(reward_total)
            
    def GetSafeActions(self, s, Q_r_control, i):
        A = []
        actions_in_state = self.all_act
        agent, objects = s[0], s[1:]
        for o in objects:
            s = (agent,o)
            for a in actions_in_state:
                if Q_r_control[(s,a)] >= i and a not in A:
                    A.append(a)
                
        return A
        
    def EpsilonGreedy(self, A, Q_control, s, epsilon):
        temp_A = A
        agent, objects = s[0], s[1:]
        best_value = -1000
        action = None
        for o in objects:
            s = (agent,o)
            for a in temp_A:
                if Q_control[(s,a)] > best_value and Q_control[(s,a)] != 0:
                    action = a
                    best_value = Q_control[(s,a)]
        
        rand_num = random.uniform(0,1)
        if (rand_num > epsilon):
            return action
        else:
            return random.choice(temp_A) #Not removing the action   #CHECK HERE
    
    def UpdateThresholds(self, stats,  candidates):
        i = np.argmax(stats)
        return candidates[i]
    
    def expected_reward(self, Q_control):
        act_list = self.all_act
        pi = self.pi
        exp_value = []
        temp_value = -1000
        for values in Q_control.keys():
            states = values[0]
            for actions in act_list:
                if Q_control[(states,actions)] > temp_value and Q_control[(states,actions)] != 0:
                    temp_value = Q_control[(states,actions)]
                    pi[states] = actions
                    
            exp_value.append(temp_value)
            
        return np.mean(exp_value)
    
    def ExtraAction(self, Oa, O, A, c):
        obj_aff = self.obj_aff
        #temp_val = 1000
        #temp_object = O[0]
        
        states = obj_aff[c.class_ID]
        
        #WE ASSUME THE ACTION TAKEN IS DIRECTED TOWARDS THE CLOSEST OBJECT
        #for o in O:
        #    if o._class == c and (Oa, o.state1) in states:
        #        dist = self.distance(Oa, o.state1)
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
        
    def ValueBonus(self, Oa, O, A, c):
        obj_aff = self.obj_aff
        states = obj_aff[c.class_ID]
        
        for o in O:
            if o._class == c and (Oa, o.state1) in states:
                return 10, states[(Oa, o.state1)]
                
        return 0, random.choice(A)
    
    def PPR(self, Oa, O, A, c):
        obj_aff = self.obj_aff
        states = obj_aff[c.class_ID]
        
        for o in O:
            if o._class == c and (Oa, o.state1) in states:
                return states[(Oa, o.state1)]
                
        return random.choice(A)
            
    def distance(self, p0, p1):
        return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
            
     #NEED TO IMPLEMENT PPR       