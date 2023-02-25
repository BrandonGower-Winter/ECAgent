import logging
import random

import ECAgent.Tags as Tags

from sys import maxsize
from deprecated import deprecated


class Model:
    """This is the base class for your Agent-based Models.
    You inherit this class to again access to all of the ECS functionality

    Attributes
    ----------
    environment : Environment
        The model's environment.
    systems : SystemManager
        The ``SystemManager`` assigned to the model.
    random : random.Random
        The model's pseudo-random number generator.
    logger : logging.Logger
        The model's logger.
    """

    __slots__ = ['environment', 'systems', 'random', 'logger']

    def __init__(self, seed: int = None, logger: logging.Logger = None):

        self.environment = Environment(self)
        self.systems = SystemManager(self)

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

    def __getattr__(self, item: str):
        """Wrapper method for accessing ``model.systems`` attributes.

        Valid ``item`` values are: ``['timestep']``. More may be added in future versions of ECAgent.

        Parameters
        ----------
        item : str
            The name of the property to access.

        Raises
        ------
        AttributeError
            If invalid ``item`` specified.
        """
        if item == 'timestep':
            return self.systems.timestep
        else:
            raise AttributeError(f'Attribute {item} is not recognized as an attribute of Model or SystemManager')

    def set_environment(self, env):
        """Sets the models environment.
        `model.set_environment(new_environment)`  is equivalent to ``model.environment = new_environment``.

        Parameters
        ----------
        env :  Environment
            The model's new environment.
        """
        self.environment = env

    def execute(self, n: int = 1):
        """A wrapper method for calling ``model.systems.execute_systems()``.

        Parameters
        ----------
        n : int, Optional
            The number of times to call ``systems.execute()``. Defaults to `1`.

        Raises
        ------
        TypeError
            If ``n`` is not an ``int``.
        ValueError
            If ``n < 1``.
        """
        if type(n) != int:
            raise TypeError(f"Type {type(n)} not supported. 'n' must be an integer.")

        if n > 0:
            for _ in range(n):
                self.systems.execute_systems()
        else:
            raise ValueError("Value of 'n' must be greater than or equal 1.")


class Component:
    """This is the base class for Components. Inherit from this class to make your own components.

    Attributes
    ----------
    agent : Agent
        The agent the component belongs to.
    model : Model
        The model the component's agent belongs to.
    """
    __slots__ = ['agent', 'model']

    def __init__(self, agent, model: Model):
        self.agent = agent
        self.model = model


class Agent:
    """This is the base class for Agent objects. Inherit from the class when creating custom agent types.

    In ECAgent, An ``Agent`` is the ``Entity`` in the Entity-Component-System (ECS) architecture.

    Attributes
    ----------
    components : dict
        The components associated with the environment. The key is the Class of the component.
    id : str
        The agent id of the environment.
    model : Model
        The ``Model`` the ``Agent`` belongs to.
    tag : int
        The value of the Tag associated with the environment. Defaults to 0 (which is the value ``NONE``).
    """

    __slots__ = ['id', 'model', 'components', 'tag']

    def __init__(self, id: str, model: Model, tag: int = Tags.NONE):
        self.id = id
        self.model = model
        self.components = {}
        self.tag = tag

    def __getitem__(self, item: type):
        """Wrapper for the ``Agent.get_component()`` function."""
        return self.get_component(item)

    def __len__(self) -> int:
        """Returns the number of components attached to a given agent."""
        return len(self.components)

    def __contains__(self, item: type):
        """Wrapper method for ``Agent.has_component(item)``."""
        return self.has_component(item)

    def add_component(self, component: Component):
        """Adds a ``Component`` to the ``Agent``.

        Parameters
        ----------
        component : Component
            The component to add.

        Raises
        ------
        ValueError
            If the agent already has a component of that type.
        """
        if type(component) in self.components.keys():
            raise ValueError(f"Agent {self.id} already has a component of type {type(component)}.")
        else:
            self.components[type(component)] = component

    @deprecated(reason='For not meeting standard python naming conventions. Use "add_component" instead.')
    def addComponent(self, component: Component):  # pragma no cover
        """Deprecated. Use ``add_component`` instead."""
        self.add_component(component)

    def remove_component(self, component_type: type):
        """Removes component of type ```component_type`` from the agent.

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
            del self.components[component_type]

    @deprecated(reason='For not meeting standard python naming conventions. Use "remove_component" instead.')
    def removeComponent(self, component_type: type):  # pragma: no cover
        self.remove_component(component_type)

    def get_component(self, component_type: type, throw_error: bool = False):
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

    @deprecated(reason='For not meeting standard python naming conventions. Use "get_component" instead.')
    def getComponent(self, component_type: type, throw_error: bool = False):  # pragma: no cover
        """Deprecated. Use ``get_component`` instead."""
        return self.get_component(component_type, throw_error)

    def has_component(self, *args) -> bool:
        """Returns a (True/False) bool if the agent (does/does not) have the list of specified components.

        The functions uses the ``*args`` so you can check for multiple components at once::

            # Will return true if agent has a PositionComponent
            agent.has_component(PositionComponent)

            # Will return true if agent has both a PositionComponent and a RotationComponent
            agent.has_component(PositionComponent, RotationComponent)

        Parameters
        ----------
        args
            The list of ``Component`` classes that will checked.

        Returns
        -------
        bool
            ``True`` if ``Agent`` has all of the components listed, else ``False``
        """
        for component in args:
            if component not in self.components.keys():
                return False
        return True

    @deprecated(reason='For not meeting standard python naming conventions. Use "has_component" instead.')
    def hasComponent(self, *args) -> bool:  # pragma: no cover
        """Deprecated. Use ``has_component`` instead."""
        return self.has_component(*args)


class System:
    """This is the base class for the systems in ECAgent's Entity-Component-System (ECS) architecture.

    Attributes
    ----------
    id : str
        The id of the system.
    model : Model
        The ``Model`` the ``System`` belongs to.
    priority : int
        The priority of the system. Higher priority systems execute first. Defaults to ``0``.
    frequency : int
        How often the system should execute. Defaults to ``1`` which means the system will execute every timestep.
    start : int
        The timestep at which the system should start executing. Defaults to ``0``.
    end : int
        The last timestep at which the system should start executing. Defaults to ``sys.maxsize``.
    """

    __slots__ = ['id', 'model', 'priority', 'frequency', 'start', 'end']

    def __init__(self, id: str, model: Model, priority: int = 0,
                 frequency: int = 1, start: int = 0, end: int = maxsize):
        self.id = id
        self.model = model
        self.priority = priority
        self.frequency = frequency
        self.start = start
        self.end = end

    def clean_up(self):
        self.model.systems.remove_system(self.id)

    def execute(self):
        """Abstract method which, when overridden by a child class, defines the the system's logic.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError


class SystemManager:
    """This class is responsible for managing the adding, removing and executing of Systems.

    Every ``Model`` will get a ``SystemManager`` which they can access using ``model.systems``.

    Attributes
    ----------
    model : Model
        The model the ``SystemManager`` belongs to.
    timestep : int
        The amount of time that has elapsed in the model.
    systems : dict
        A dictionary containing all of the model's systems. The key is the system's id.
    execution_queue : list
        A list of containing the order at which the systems execute when ``execute_systems()`` is called.
    component_pools : dict
        A dictionary containing lists of all components registered with the ``SystemManager``. The key is type of the
        ``Component``.
    """

    __slots__ = ['timestep', 'systems', 'execution_queue', 'component_pools', 'model']

    def __init__(self, model: Model):
        self.timestep = 0
        self.systems = {}
        self.execution_queue = []
        self.component_pools = {}
        self.model = model

    def add_system(self, s: System):
        """Adds System s to the ``SystemManager`` and registers it with execution queue.

        Parameters
        ----------
        s : System
            The ``System`` being added to the ``SystemManager``

        Raises
        ------
        KeyError
            If system already exists in the execution queue.
        """
        if s.id in self.systems.keys():
            raise KeyError(f"System {s.id} already registered with the execution queue.")
        else:
            self.systems[s.id] = s  # Add to systems dict
            # Add to event queue
            for i in range(0, len(self.execution_queue)):
                if s.priority > self.execution_queue[i].priority:
                    self.execution_queue.insert(i, s)
                    break
            # Add to the end of queue if s has the lowest priority
            if s not in self.execution_queue:
                self.execution_queue.append(s)

    @deprecated(reason='For not meeting standard python naming conventions. Use "add_system" instead.')
    def addSystem(self, s: System):  # pragma: no cover
        """Deprecated. Use ``add_system`` instead."""
        self.add_system(s)

    def remove_system(self, s_id: str):
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
        if s_id not in self.systems.keys():
            raise SystemNotFoundError(s_id)
        else:
            self.execution_queue.remove(self.systems[s_id])
            del self.systems[s_id]

    @deprecated(reason='For not meeting standard python naming conventions. Use "remove_system" instead.')
    def removeSystem(self, s_id: str):  # pragma: no cover
        """Deprecated. Use ``remove_system`` instead."""
        self.remove_system(s_id)

    def execute_systems(self):
        """Function that loops through all systems in the ``execution_queue`` and calls the ``execute()`` method.
        The value of ``SystemManager.timestep`` is increased by ``1`` each time this method is called.

        The function uses the System's ``start``, ``end`` and ``frequency`` to determine if its ``execute()`` should be
        called::

        if sys.start <= self.timestep <= sys.end and (sys.start - self.timestep) % sys.frequency == 0:
                sys.execute()
        """
        for sys in self.execution_queue:  # Simple execute cycle
            if sys.start <= self.timestep <= sys.end and (sys.start - self.timestep) % sys.frequency == 0:
                sys.execute()
        self.timestep += 1

    @deprecated(reason='For not meeting standard python naming conventions. Use "execute_systems" instead.')
    def executeSystems(self):  # pragma: no cover
        self.execute_systems()

    def register_component(self, component: Component):
        """Registers a component with the ``SystemManager``.

        Registered components can be accessed using ``SystemManager.component_pools[type(component)]``.

        Parameters
        ----------
        component : Component
            The ``Component`` to register.

        Raises
        ------
        KeyError
            When ``component`` has already been registered with the ``SystemManager``.
        """
        if type(component) not in self.component_pools.keys():
            self.component_pools[type(component)] = [component]
        elif component in self.component_pools[type(component)]:
            raise KeyError(f"Agent {component.agent.id}'s {str(type(component))} Component already registered with the"
                           f"System Manager.")
        else:
            self.component_pools[type(component)].append(component)

    def deregister_component(self, component: Component):
        """Deregisters (removes) a component from the ``SystemManager`` component pool.

        Parameters
        ----------
        component : Component
            The ``Component`` to deregister.

        Raises
        ------
        KeyError
            When ``component`` is not registered with the ``SystemManager``.
        """
        if type(component) not in self.component_pools.keys():
            raise KeyError(f"No components with type {str(type(component))} registered with the SystemManager.")
        elif component not in self.component_pools[type(component)]:
            raise KeyError(f"Cannot deregister Agent {component.agent.id}'s {str(type(component))} Component because "
                           f"it was never registered with the SystemManager to begin with.")
        else:
            self.component_pools[type(component)].remove(component)
            if len(self.component_pools[type(component)]) == 0:
                del self.component_pools[type(component)]

    def get_components(self, component_type: type):
        """Returns the list of components registered to the ``SystemManager`` with a type of ``component_type``.
        Returns ``None`` if there are no components of type ``component_type`` registered with the ``SystemManager``.

        Parameters
        ----------
        component_type : type
            The type of components you want to search for (e.g. ``PositionComponent``).

        Returns
        -------
        list
            Of components with type ``component_type``.
        None
            If no components of type ``component_type`` can be found.
        """
        if component_type in self.component_pools.keys():
            return self.component_pools[component_type]
        else:
            return None

    @deprecated(reason='For not meeting standard python naming conventions. Use "get_components" instead.')
    def getComponents(self, component_type: type):  # pragma: no cover
        """Deprecated. Use ``get_components`` instead."""
        return self.get_components(component_type)


class Environment(Agent):
    """Base environment class. It is a void environment which means that is has no spacial properties.

    In ECAgent, all environments are treated as agents. This means that they can have components added and removed from
    them. From a design perspective, An ``Environment`` is an ``Agent`` that contains other agents.

    Attributes
    ----------
    agents : dict
        A ``dict`` of agents occupying the environment. The key is the agent's id.
    components : dict
        The components associated with the environment. The key is the Class of the component.
    id : str
        The agent id of the environment.
    model : Model
        The ``Model`` the ``Environment`` belongs to.
    tag : int
        The value of the Tag associated with the environment. Defaults to 0 (which is the value ``NONE``).
    """

    __slots__ = ['agents']

    def __init__(self, model, id: str = 'ENVIRONMENT'):
        super().__init__(id, model)
        self.agents = {}

    def set_model(self, model: Model):
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
            for ckey in agent.components:
                self.model.systems.register_component(agent[ckey])

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
            for ckey in self.agents[a_id].components:
                self.model.systems.deregister_component(self.agents[a_id][ckey])
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
    def getAgent(self, id: str, throw_error: bool = False):  # pragma: no cover
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
                if self.agents[agentKey].has_component(*args):
                    matching_agents.append(self.agents[agentKey])

        # Filter by tag if tag was supplied
        if tag is not None:
            matching_agents = [a for a in matching_agents if a.tag == tag]

        return matching_agents

    def __len__(self):
        """Returns the number of agents currently in the environment."""
        return len(self.agents)

    def __iter__(self):
        """Returns a tuple of all agents in the environment."""
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
