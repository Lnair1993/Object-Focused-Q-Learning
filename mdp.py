#MDP CLASS IS DEFINED HERE

import operator

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
