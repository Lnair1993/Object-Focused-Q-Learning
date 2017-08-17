# -*- coding: utf-8 -*-
"""
Created on Wed Aug 09 12:55:05 2017

@author: Lakshmi
"""

import numpy as np
import random
import csv
import ast
import math
from matplotlib import pyplot as plt
from collections import defaultdict

from RT import ExtraAction
from RT import ValueBonus
from RT import PPR
      
class OfQ_Learning:
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
            self.alpha = 0.25 #lambda n: 1./(1+n)    

    def act_read(self):
        with open('Obj_aff.csv','r') as f:
            reader = csv.reader(f)
            obj_aff = {row[0]:ast.literal_eval(row[1]) for row in reader}
        return obj_aff
            
    def OFQrun(self, RT=None, RT_C = 20):
        alpha, gamma = self.alpha, self.gamma
        Ne, epsilon, loop = self.Ne, self.epsilon, self.loop
        reward_total = []
        class_reward = []
        
        actions_in_state = self.all_act
        
        GetSafeActions = self.GetSafeActions
        EpsilonGreedy = self.EpsilonGreedy
        UpdateThresholds = self.UpdateThresholds
        expected_reward = self.expected_reward
        
        Q_estimate_r = defaultdict(float)
        Q_estimate_c = defaultdict(float)
        
        T = [c.Tc for c in self.C]  #Not reused in the algorithm either
        for c in self.C:
            Q_estimate_c.update(c.Qc)
            Q_estimate_r.update(c.Qr)        
        #[c.Qc for c in C]
        #Q_estimate_r = [c.Qr for c in C]

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
                        B = 0 #Bonus value initialized to 0
                        
                        mdp = self.mdp_init #initialize mdp to the initial mdp states - restart episode
                        Oa_init, O_init = mdp.get_init()
                        s = [Oa_init] + O_init
                        
                        while s[0] not in mdp.terminals:
                            A = GetSafeActions(s, Q_r_control, i)
                            
                            if RT == 'ExtraAction':
                                if loop_run <= RT_C:
                                    Oa, O, r1 = mdp.update_percept()
                                    a = ExtraAction(self.obj_aff, Oa, O, A, c)
                            elif RT == 'BonusValue':
                                if loop_run <= RT_C:
                                    Oa, O, r1 = mdp.update_percept()
                                    B,a = ValueBonus(self.obj_aff, Oa, O , A, c)
                            elif RT == 'PPR':
                                phi = 1/1+j
                                rand_num = random.uniform(0,1)
                                if (rand_num < phi):
                                    Oa, O, r1 = mdp.update_percept()
                                    a = PPR(self.obj_aff, Oa, O, A, c)
                                else:
                                    a = EpsilonGreedy(A, Q_control, s, epsilon)
                            else:
                                a = EpsilonGreedy(A, Q_control, s, epsilon)

                            mdp.TakeAction(a)
                            
                            Oa, O, r1 = mdp.update_percept() #Update state, return agent state and obj_class array
                            
                            if Oa in mdp.terminals: #End if terminal state
                                break
                            
                            o_states = [o.state1 for o in O]
                            s = [Oa] + o_states #Update s
                            
                            for o in O:  #Declare O as array of object classes and o is one object class from the array
                                if c == o._class: 
                                    cls_idx = self.C.index(c)
                                
                                    S0 = (Oa, o.state0)
                                    S1 = (Oa, o.state1)
                                    
                                    c.Qc[(S0,a)] = (1-alpha) * c.Qc[(S0,a)] + alpha * (r1 + gamma * max(c.Qc[(S1,a1)]
                                                                   for a1 in actions_in_state) - c.Qc[(S0,a)])
                
                                    c.Qr[(S0,a)] = (1-alpha) * c.Qr[(S0,a)] + alpha * (r1 + gamma * np.mean([c.Qr[(S1,a1)]
                                                                   for a1 in actions_in_state]))
                
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
                
    
