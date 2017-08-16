# -*- coding: utf-8 -*-
"""
Created on Wed Aug 09 12:55:05 2017

@author: Lakshmi
"""

from collections import defaultdict
import numpy as np
import operator
import random
from matplotlib import pyplot as plt

#Reward associated with objects?
#Terminal state associated with objects

#init is the initial state of agent and objects

class mdp:
    def __init__(self, grid, terminals, actlist, objects, agent_start, gamma = 0.9, game = 'Normandy'):
        self.grid = grid
        self.terminals = terminals
        self.gamma = gamma
        self.actlist = actlist
        self.agent_state = agent_start
        self.objects = objects #Array of _object classes
        
        self.objects_init = [obj.state1 for obj in objects]
        self.agent_init = self.agent_state
        self.states = self.GetStates(self.grid)
        
    def GetStates(self, grid):
        #Returns possible locations of the agent
        grid.reverse()
        rows = len(grid)
        cols = len(grid[0])
        states = []
        
        for x in range(cols):
            for y in range(rows):
                states.append((x,y)) #States of the agent
        return states
                
    def UpdateTerminals(self):
        #Move terminal state to the right by 1
        grid = self.grid
        objects = self.objects
        objects_init = self.objects_init
        new_terminals = []
        
        for i,obj in enumerate(objects):
            if obj.state1[1] < len(grid[0])-1 and obj.reward < 0: #Move the negative rewards only
                new_state = tuple(map(operator.add, obj.state1, (0,1)))
                obj.update_object_state(new_state)
                #obj.state1 = tuple(map(operator.add, obj.state1, (1,0)))
            else:
                new_state = objects_init[i]
                obj.update_object_state(new_state)
                #obj.state1 = objects_init[i]
                
            #By some probability its on the negative side of the axis - not in the world    
                
            #new_terminals.append(obj.state1)   #Update each object class here with new states
            new_terminals.append(new_state)
            
        self.terminals = new_terminals
                
    def TakeAction(self, a):
        agent_state = self.agent_state
        grid = self.grid
        if a == "Up":
            if agent_state[0] < len(grid)-1:
                self.agent_state = tuple(map(operator.add, agent_state, (1,0)))
        elif a == "Down":
            if agent_state[0] > 0:
                self.agent_state = tuple(map(operator.sub, agent_state, (1,0)))
        elif a == "Left":
            if agent_state[1] > 0:
                self.agent_state = tuple(map(operator.sub, agent_state, (0,1)))
        elif a == "Right":
            if agent_state[1] < len(grid[0])-1:
                self.agent_state = tuple(map(operator.add, agent_state, (0,1)))
        elif a == "Wait":
            self.agent_state = agent_state
                
        self.UpdateTerminals() #Move objects as well
        
    def get_init(self):
        return self.agent_init,self.objects_init
        
    def update_percept(self):
        grid = self.grid
        grid.reverse()
        agent_state = self.agent_state
        obj = self.objects #Updated object classes
        obj_states = [o.state1 for o in obj]
        
        if agent_state in obj_states:
            idx = obj_states.index(agent_state)
            reward = obj[idx].reward
        else:
            reward = grid[agent_state[0]][agent_state[1]]
        
        return agent_state, obj, reward

#Define object class Qc, Qr and Tc
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
        
#ABOVE THIS LINE VERIFIED
        
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
        
        if (alpha):
            self.alpha = alpha
        else:
            self.alpha = 0.25 #lambda n: 1./(1+n)    #CHECK HERE
            
        #if state in self.terminals:
        #    return [None]
        #else:
        #    return self.all_act 
            
    def OFQrun(self):
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
                    #discount_reward = 0
                    for j in range(1,Ne):
                        episode_reward = 0
                        #discount_reward = 0
                        mdp = self.mdp_init #initialize mdp to the initial mdp states - restart episode
                        Oa_init, O_init = mdp.get_init()
                        s = [Oa_init] + O_init
                        
                        while s[0] not in mdp.terminals:
                            A = GetSafeActions(s, Q_r_control, i)
                            a = EpsilonGreedy(A, Q_control, s, epsilon)
                            mdp.TakeAction(a)
                            
                            Oa, O, r1 = mdp.update_percept() #Update state, return agent state and obj_class array
                            
                            if Oa in mdp.terminals: #End if terminal state
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
                                                                   for a1 in actions_in_state) - c.Qc[(S0,a)])
                
                                    c.Qr[(S0,a)] = (1-alpha) * c.Qr[(S0,a)] + alpha * (r1 + gamma * np.mean([c.Qr[(S1,a1)]
                                                                   for a1 in actions_in_state]))
                
                                    #Ensure that actual values are being updated
                                    self.C[cls_idx].Qc[(S0,a)] = c.Qc[(S0,a)]
                                    self.C[cls_idx].Qr[(S0,a)] = c.Qr[(S0,a)]
        
                            episode_reward += r1
                            #discount_reward += gamma*best_value
                        #End of episode
                        candidate_reward += episode_reward
                    #End evaluations
                    #reward_total.append(discount_reward/Ne)
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
                
            
        
        
        
            
            
            

            
            
    
            
            
    
        
    
