from sys import maxsize


class Model:
    """ This is the base class for the ABM model.
    You inherit this class to again access to all of the ECS functionality """

    def __init__(self, environment):
        self.timestep = 0
        self.environment = environment
        self.systemManager = SystemManager(self)


class Component:
    """This is the base class for Components"""

    def __init__(self, agentID: str, systemID: str, model: Model):
        self.agentID = agentID
        self.systemID = systemID
        self.model = model


class Agent:
    """This is the base class for Agent objects.
    Agents can be thought of as Entities"""

    def __init__(self, id: str, model: Model):
        self.id = id
        self.model = model
        self.components = []

    def addComponent(self, component: Component):
        if component.systemID in [com.systemID for com in self.components]:
            raise Exception("Agents cannot have multiple of the components")
        else:
            self.components.append(component)
            self.model.systemManager.registerComponent(component)

    def removeComponent(self, component: Component):
        if component.systemID not in [com.systemID for com in self.components]:
            raise Exception("Agent does not have component")
        else:
            self.components.remove(component)
            self.model.systemManager.deregisterComponent(component)


class System:
    """This is the base class for the systems in the ECS architecture"""

    def __init__(self, id: str, model: Model, priority: int = 0,
                 frequency: int = 1, start=0, end=maxsize):
        self.id = id
        self.model = model
        self.priority = priority
        self.frequency = frequency
        self.start = start
        self.end = end

    def cleanUp(self):
        self.model.systemManager.removeSystem(self.id)

    def execute(self, components: [Component]):
        pass


class SystemManager:
    """ This class is responsible for managing the adding,
    removing and executing Systems """

    def __init__(self, model: Model):
        self.systems = {}
        self.executionQueue = []
        self.componentPools = {}
        self.model = model

    def addSystem(self, s: System):
        """Adds System s to the systems dict and registers
        it in the execution queue"""

        if s.id in self.systems.keys():
            raise Exception("System already registered.")
        else:
            self.systems[s.id] = s  # Add to systems dict
            self.componentPools[s.id] = []
            # Add to event queue
            for i in range(0, len(self.executionQueue)):
                if s.priority > self.executionQueue[i].priority:
                    self.executionQueue.insert(i, s)
                    break
            # Add to the end of queue if s has the lowest priority
            if s not in self.executionQueue:
                self.executionQueue.append(s)

    def removeSystem(self, id: str):
        """Removes System s from the systems dict and
        deregisters it within the execution queue"""
        if id not in self.systems.keys():
            raise Exception("System cannot be deregistered because "
                            "it was never registered to begin with")
        else:
            self.executionQueue.remove(self.systems[id])
            del self.systems[id]
            del self.componentPools[id]

    def executeSystems(self):  # Simple execute cycle
        for sys in self.executionQueue:
            if sys.start <= self.model.timestep <= sys.end and \
                    sys.start - self.model.timestep % sys.frequency == 0:
                sys.execute(self.componentPools[sys.id])

    def registerComponent(self, component: Component):
        if component.systemID not in self.componentPools.keys():
            raise Exception("No System with ID " + component.systemID)
        if component in self.componentPools[component.systemID]:
            raise Exception("Component already registered.")
        else:
            self.componentPools[component.systemID].append(component)

    def deregisterComponent(self, component: Component):
        if component.systemID not in self.componentPools.keys():
            raise Exception("No System with ID " + component.systemID)
        if component not in self.componentPools[component.systemID]:
            raise Exception("Cannot deregister component because "
                            "it was never registered to begin with.")
        else:
            self.componentPools[component.systemID].remove(component)


class Environment:
    """This is the base environment class.
    It is a void environment which means that is has no spacial properties"""

    def __init__(self):
        self.agents = {}

    def addAgent(self, agent: Agent):
        if agent.id in self.agents.keys():
            raise Exception("Agent has already been added to the environment")
        else:
            self.agents[agent.id] = agent

    def removeAgent(self, agent: Agent):
        if agent.id not in self.agents.keys():
            raise Exception("Cannot remove agent that is "
                            "not in the environment")
        else:
            del self.agents[agent.id]

    def getAgent(self, id: str):
        """Gets agent obj based on its id.
        Returns None if agent does not exist"""
        if id in self.agents.keys():
            return self.agents[id]
        else:
            return None
