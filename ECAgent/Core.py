import logging
import random

import ECAgent.Tags as Tags

from sys import maxsize
from deprecated import deprecated


class Model:
    """ This is the base class for the ABM model.
    You inherit this class to again access to all of the ECS functionality """

    __slots__ = ['environment', 'systemManager', 'random', 'logger']

    def __init__(self, seed: int = None, logger=None):

        self.environment = Environment(self)
        self.systemManager = SystemManager(self)

        # Initialize RNG. It is object based because we want to ensure
        # that object results are reproducable when batch execution
        # is added.

        self.random = random.Random(seed)

        # Add logger if custom logger isn't specified
        if logger is None:
            self.logger = logging.getLogger('MODEL')
            self.logger.setLevel(logging.INFO)
        else:
            self.logger = logger


class Component:
    """This is the base class for Components"""

    __slots__ = ['agent', 'model']

    def __init__(self, agent, model: Model):
        self.agent = agent
        self.model = model


class Agent:
    """This is the base class for Agent objects.
    Agents can be thought of as Entities"""

    __slots__ = ['id', 'model', 'components', 'tag']

    def __init__(self, id: str, model: Model, tag: int = Tags.NONE):
        self.id = id
        self.model = model
        self.components = {}
        self.tag = tag

    def __getitem__(self, item: type):
        """ [] Override that called the getComponent() function. """
        return self.getComponent(item)

    def __len__(self) -> int:
        """Returns the number of components attached to a given agent"""
        return len(self.components)

    def __contains__(self, item: type):
        """ Returns whether an agent has a particular component of not """
        return self.hasComponent(item)

    def addComponent(self, component: Component):
        if type(component) in self.components.keys():
            raise Exception("Agents cannot have multiple of the components")
        else:
            self.components[type(component)] = component
            self.model.systemManager.registerComponent(component)

    def removeComponent(self, component_type: type):
        """
        Removes component of type ```component_type`` from the agent.

        Parameters:
        component_type : type
            Class of component to be removed from agent.

        Raises
        ------
        ComponentNotFoundError
            If agent does not have a component of class ``component_type``.
        """
        if component_type not in self.components.keys():
            raise ComponentNotFoundError(self, component_type)
        else:
            self.model.systemManager.deregisterComponent(self.components[component_type])
            del self.components[component_type]

    def getComponent(self, component_type: type, throw_error: bool = False):
        """Gets a component that is the same type as ``component_type``.

        Parameters
        ----------
        component_type : type
            The type of component to search for.
        throw_error : bool, Optional
            Boolean that specifies whether a ``ComponentNotFoundError`` should be raised upon failing to find a
            component of type ``component_type``. Defaults to ``False``.
        Returns
        -------
        Component
            A component object matching the class specified by ``component_type``.
        None
            Returns None if agent does not have a component of class ``component_type``.

        Raises
        ------
        ComponentNotFoundError
            If ``throw_error`` is ``True`` and no component matching ``component_type`` is found.
        """
        if component_type in self.components.keys():
            return self.components[component_type]
        elif throw_error:
            raise ComponentNotFoundError(self, component_type)
        else:
            return None

    def hasComponent(self, *args) -> bool:
        """ Returns a (True/False) bool if the agent (does/does not)
        have a component of type component_type """
        for component in args:
            if component not in self.components.keys():
                return False
        return True


class System:
    """This is the base class for the systems in the ECS architecture"""

    __slots__ = ['id', 'model', 'priority', 'frequency', 'start', 'end']

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

    __slots__ = ['timestep', 'systems', 'executionQueue', 'componentPools', 'model']

    def __init__(self, model: Model):
        self.timestep = 0
        self.systems = {}
        self.executionQueue = []
        self.componentPools = {}
        self.model = model

    def addSystem(self, s: System):
        """Adds System s to the ``System`` manager and registers it with execution queue.

        Parameters
        ----------
        s : System
            The ``System`` being added to the ``SystemManager``
        """

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

    def removeSystem(self, s_id: str):
        """Removes ``System`` with ``System.id == s_id`` from the ``SystemManager``.

        Parameters
        ----------
        s_id : str
            The id of the system to be removed.

        Raises
        ------
        SystemNotFoundError
            If the no System with ``System.id == s_id`` can be found.
        """
        if id not in self.systems.keys():
            raise SystemNotFoundError(s_id)
        else:
            self.executionQueue.remove(self.systems[s_id])
            del self.systems[s_id]

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
            raise Exception("No components with type " + str(type(component)) + " registered")
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


class Environment(Agent):
    """Base environment class.

    It is a void environment which means that is has no spacial properties.
    """

    __slots__ = ['agents']

    def __init__(self, model, id: str = 'ENVIRONMENT'):
        super().__init__(id, model)
        self.agents = {}

    def setModel(self, model: Model):
        self.model = model

    def add_agent(self, agent: Agent):
        """
        Adds an agent to the environment. Agents cannot have duplicate ``id`` values.

        Parameters
        ----------
        agent : Agent
            The agent being added to the environment.

        Raises
        ------
        DuplicateAgentError
            If the agent already exists in the environment.
        """
        if agent.id in self.agents.keys():
            raise DuplicateAgentError(agent.id, self.model.environment)
        else:
            self.agents[agent.id] = agent

    @deprecated(reason='For not meeting standard python naming conventions. Use "add_agent" instead.')
    def addAgent(self, agent: Agent):  # pragma: no cover
        """Deprecated. Use ``Environment.add_agent`` instead."""
        self.add_agent(agent)

    def remove_agent(self, a_id: str):
        """Removes an agent with ``agent.id == a_id`` from the environment.

        Parameters
        ----------
        a_id : str
            The ``id`` of the agent to remove.

        Raises
        ------
        AgentNotFoundError
            If no agent with an ``agent.id == a_id`` can be found.
        """
        if a_id not in self.agents.keys():
            raise AgentNotFoundError(a_id, self)
        else:
            del self.agents[a_id]

    @deprecated(reason='For not meeting standard python naming conventions. Use "remove_agent" instead.')
    def removeAgent(self, a_id: str):  # pragma: no cover
        """Deprecated. Use ``Environment.remove_agent`` instead."""
        self.remove_agent(a_id)

    def get_agent(self, id: str, throw_error: bool = False):
        """Gets agent obj based on its ``id``.

        Returns None if agent does not exist.

        Parameters
        ----------
        id : str
            The id of the agent object to search for.
        throw_error : bool, Optional
            Determines if the function should raise an AgentNotFoundError when it cannot find an agent object with a
            matching id.

        Returns
        -------
        Agent
            The agent with ``agent.id == id``

        Raises
        ------
        AgentNotFoundError
            If ``throw_error == True`` and agent with ``agent.id == id`` could not be found.
        """
        if id in self.agents.keys():
            return self.agents[id]
        elif throw_error:
            raise AgentNotFoundError(id, self)
        else:
            return None

    @deprecated(reason='For not meeting standard python naming conventions. Use "remove_agent" instead.')
    def getAgent(self, id: str, throw_error: bool = False):  # pragma no cover
        """Deprecated. Use ``Environment.remove_agent`` instead."""
        self.get_agent(id, throw_error)

    @deprecated(reason='For not meeting standard python naming conventions. Use "get_random_agent" instead')
    def getRandomAgent(self, *args):  # pragma: no cover
        """Deprecated. Use ``Environment.get_random_agent`` instead."""
        return self.get_random_agent(*args)

    def get_random_agent(self, *args, tag: int = None):
        """Returns a random agent in the environment.

        See ``Agent.get_agents`` for a guide on how component template and tag searches work. This function uses
        ``Agent.get_agents(*args, tag)`` to get a list of valid agents to randomly select from.

        Parameters
        ----------
        *args : Optional
            A template (list of Components) the returned agent must have.
        tag : int, Optional
            Tag that the returned agent must have.

        Returns
        -------
        Agent
            A randomly selected agent from a list of agents matching the Component template or tag specified.
        None
            If no agents exist that match the Component template or tag specified.
        """
        valid_agents = self.get_agents(*args, tag=tag)
        # Return none if no agent matches filter
        if len(valid_agents) == 0:
            return None

        return self.model.random.choice(valid_agents)

    @deprecated(reason='For not meeting standard python naming conventions. Use "get_agent" instead')
    def getAgents(self, *args):  # pragma: no cover
        """Deprecated. Use ``Environment.get_agents`` instead."""
        return self.get_agents(*args)

    def get_agents(self, *args, tag: int = None) -> list:
        """Returns a list of agents within the environment.

        This method is very flexible. There are three (four technically) ways it can be used:

        1. The default case::

            all_agents = environment.get_agents()

        2. Using a component template::

            # This will return a list of agents with Components of type 'Component1' and 'Component2'
            template_search = environments.get_agents(Component1, Component2)

        3. Using an agent's tag:::

            # This code assumes the tag 'PREY' already exists
            import ECAgent.Tags as Tags

            tag_search = environment.get_agents(tag = Tags.PREY)

        Additionally, you can specify a component template and tag to search for (although this is a niche case)::

            # This code assumes the tag 'PREY' already exists
            import ECAgent.Tags as Tags

            # This will return a list of agents with Components of type 'Component1' and tag == PREY
            template_tag_search = environments.get_agents(Component1, tag = Tags.PREY)

        Parameters
        ----------
        *args : Optional
            A template (list of Components) the returned agents must have.
        tag : int, Optional
            Tag that the returned agents must have.
        Returns
        -------
        list
            list of Agents
        """
        matching_agents = []

        # If no component filter is supplied, return all agents
        if len(args) == 0:
            matching_agents = [self.agents[agentKey] for agentKey in self.agents]
        else:
            # If a component filter is supplied, filter for agents that meet the condition
            for agentKey in self.agents:
                if self.agents[agentKey].hasComponent(*args):
                    matching_agents.append(self.agents[agentKey])

        # Filter by tag if tag was supplied
        if tag is not None:
            matching_agents = [a for a in matching_agents if a.tag == tag]

        return matching_agents

    def __len__(self):
        """Returns the number of agents currently in the environment."""
        return len(self.agents)

    def __iter__(self):
        """Returns a list all of all agents in the environment."""
        return (self.agents[a] for a in self.agents)

    def shuffle(self, *args, tag: int = None):
        """Returns a list of agents with matching components in a random order.

        This method is just a wrapper for calling ``self.model.random.shuffle(self.get_agents(*args, tag=tag))``. The
        method finds a list of agents with components and/or tag matching those included in ``*args`` and ``tag``
        respectively. This method returns them in random order.

        The order is random each time the function is called. This is useful if you want to mitigate benefits agents get
        when executing their behaviour earlier than others.

        Parameters
        ----------
        args
            A list of ``Component`` classes that describe a template the agents need to match in order to be included in
            the list of shuffled agents.
        tag : int, Optional
            The tag the returned agents need to have in order to be included in
            the list of shuffled agents. Default to None which disables tag filtering.

        Returns
        -------
        list
            Of agents with components matching ``*args``. The order of the agents is random.
        """
        matching_agents = self.get_agents(*args, tag=tag)
        self.model.random.shuffle(matching_agents)
        return matching_agents


##############
# Exceptions #
##############

class AgentNotFoundError(Exception):
    """Exception raised for errors when an agent object cannot be found.

    Attributes:
    -----------
    a_id : str
        ``id`` of Agent to search for.
    environment : Environment
        Environment that was searched.
    message : str
        Explanation of error.
    """
    def __init__(self, a_id: str, environment: Environment):
        """
        Parameters
        ----------
        a_id : str
            ``id`` of Agent to search for.
        environment : Environment
            Environment that was searched.
        """
        self.a_id = a_id
        self.environment = environment
        self.message = f'Agent "{a_id}" could not be found in Environment "{environment.id}"'
        super(AgentNotFoundError, self).__init__(self.message)


class DuplicateAgentError(Exception):
    """Exception raised for errors when an agent object already exists in an environment.

    Attributes:
    -----------
    a_id : str
        ``id`` of the Agent.
    environment : Environment
        The ``Environment`` the agents exists in.
    message : str
        Explanation of error.
    """
    def __init__(self, a_id: str, environment: Environment):
        """
        Parameters
        ----------
        a_id : str
            ``id`` of Agent.
        environment : Environment
            The ``Environment`` the agents exists in.
        """
        self.a_id = a_id
        self.environment = environment
        self.message = f'Agent "{a_id}" already exists in Environment "{environment.id}"'
        super(DuplicateAgentError, self).__init__(self.message)


class ComponentNotFoundError(Exception):
    """Exception raised for errors when components are accessed on agents that do not have them.

    Attributes:
    -----------
    agent : Agent
        Agent whose components list was accessed.
    component_type : type
        Class of Component that was searched for.
    message : str
        Explanation of error.
    """

    def __init__(self, agent: Agent, component_type: type):
        """
        Parameters
        ----------
        agent : Agent
            Agent whose components list was accessed.
        component_type : type
            Class of Component that was searched for.
        """
        self.agent = agent
        self.component_type = component_type
        self.message = f'Agent {agent.id} does not have a component of type {str(component_type)}.'
        super(ComponentNotFoundError, self).__init__(self.message)


class SystemNotFoundError(Exception):
    """Exception raised for errors when systems that don't exist are accessed.

    Attributes:
    -----------
    s_id : str
        ``id`` of system that was searched for.
    message : str
        Explanation of error.
    """

    def __init__(self, s_id: str):
        """
        Parameters
        ----------
        s_id : str
        ``id`` of system that was searched for.
        """
        self.s_id = s_id
        self.message = f'System with id "{s_id}" does not exist.'
        super(SystemNotFoundError, self).__init__(self.message)
