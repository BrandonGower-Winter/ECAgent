import random
from sys import maxsize


class Model:
    """ This is the base class for the ABM model.
    You inherit this class to again access to all of the ECS functionality """

    def __init__(self, environment=None, seed: int = None):
        if environment is None:
            self.environment = Environment()
        else:
            self.environment = environment

        # Set the environment model
        self.environment.model = self
        self.systemManager = SystemManager(self)

        # Initialize RNG. It is object based because we want to ensure
        # that object results are reproducable when batch execution
        # is added.

        self.random = random.Random(seed)


class Component:
    """This is the base class for Components"""

    def __init__(self, agent, model: Model):
        self.agent = agent
        self.model = model


class Agent:
    """This is the base class for Agent objects.
    Agents can be thought of as Entities"""

    def __init__(self, id: str, model: Model):
        self.id = id
        self.model = model
        self.components = {}

    def addComponent(self, component: Component):
        if type(component) in self.components.keys():
            raise Exception("Agents cannot have multiple of the components")
        else:
            self.components[type(component)] = component
            self.model.systemManager.registerComponent(component)

    def removeComponent(self, component: Component):
        if type(component) not in self.components.keys():
            raise Exception("Agent does not have component")
        else:
            del self.components[type(component)]
            self.model.systemManager.deregisterComponent(component)

    def getComponent(self, component_type: type):
        """ Gets a component that is the same type as component type.
        Returns None if component doesn't exist."""
        if component_type in self.components.keys():
            return self.components[component_type]
        else:
            return None

    def hasComponent(self, component_type: type):
        """ Returns a (True/False) bool if the agent (does/does not)
        have a component of type component_type """
        return component_type in self.components.keys()


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

    def execute(self):
        pass


class SystemManager:
    """ This class is responsible for managing the adding,
    removing and executing Systems """

    def __init__(self, model: Model):
        self.timestep = 0
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

    def executeSystems(self):  # Simple execute cycle
        for sys in self.executionQueue:
            if sys.start <= self.timestep <= sys.end and \
                    sys.start - self.timestep % sys.frequency == 0:
                sys.execute()
        self.timestep += 1

    def registerComponent(self, component: Component):
        if type(component) not in self.componentPools.keys():
            self.componentPools[type(component)] = [component]
        elif component in self.componentPools[type(component)]:
            raise Exception("Component already registered.")
        else:
            self.componentPools[type(component)].append(component)

    def deregisterComponent(self, component: Component):
        if type(component) not in self.componentPools.keys():
            raise Exception("No components with type " +
                            str(type(component)) + " registered")
        elif component not in self.componentPools[type(component)]:
            raise Exception("Cannot deregister component because "
                            "it was never registered to begin with.")
        else:
            self.componentPools[type(component)].remove(component)
            if len(self.componentPools[type(component)]) == 0:
                del self.componentPools[type(component)]

    def getComponents(self, component: type):
        """Returns the list of components registered to the system with id
        = sysID. Returns None if there is no system with id = sysID"""
        if component in self.componentPools.keys():
            return self.componentPools[component]
        else:
            return None


class Environment:
    """This is the base environment class.
    It is a void environment which means that is has no spacial properties"""

    def __init__(self):
        self.agents = {}
        self.model = None

    def addAgent(self, agent: Agent):
        if agent.id in self.agents.keys():
            raise Exception("Agent has already been added to the environment")
        else:
            self.agents[agent.id] = agent

    def removeAgent(self, agentID: str):
        if agentID not in self.agents.keys():
            raise Exception("Cannot remove agent that is "
                            "not in the environment")
        else:
            del self.agents[agentID]

    def getAgent(self, id: str):
        """Gets agent obj based on its id.
        Returns None if agent does not exist"""
        if id in self.agents.keys():
            return self.agents[id]
        else:
            return None

    def getRandomAgent(self):
        """Gets a random agent in the environment.
        Return None if there are no agents in the environment"""

        if len(self.agents) == 0 or self.model is None:
            return None

        rand = self.model.random.randrange(len(self.agents))
        key = list(self.agents.keys())[rand]
        return self.agents[key]
