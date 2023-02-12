import math

import pandas

from ECAgent.Core import Agent, Environment, Component, Model, ComponentNotFoundError


def discreteGridPosToID(x: int, y: int = 0, width: int = 0, z: int = 0, height: int = 0):
    """Returns a unique number of based on the x, y and z coordinates entered.

    Uniqueness is dimension dependent. The equation for calculating uniqueness is defined as:
     ```(z * width * height) + (y * width) + x`

    Parameters
    ----------
    x : int
        The x-coordinate.
    y : int, Optional
        The y-coordinate. Defaults to 0.
    width : int, Optional
        The width of the environment. Defaults to 0.
    z : int, Optional
        The z-coordinate. Defaults to 0.
    height : int, Optional
        The height of the environment. Defaults to 0.

    Returns
    -------
    int
        The unique ID.
    """
    return (z * width * height) + (y * width) + x


class PositionComponent(Component):
    """A position component. It contains three float properties: x, y, z.
    This component can be used to store the position of an Agent in a 1-3D world.
    It is used by the LineWorld, GridWorld and CubeWorld classes to do exactly that.
    """

    __slots__ = ['x', 'y', 'z']

    def __init__(self, agent, model, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        super().__init__(agent, model)
        self.x = x
        self.y = y
        self.z = z

    def getPosition(self) -> (float, float, float):
        """Returns the x,y and z values of the component as a tuple"""
        return self.x, self.y, self.z

    def xy(self):
        """Returns the x and y values of the component as a 2-tuple.
        """
        return self.x, self.y

    def xz(self):
        """Returns the x and z values of the component as a 2-tuple.
        """
        return self.x, self.z

    def yz(self):
        """Returns the y and z values of the component as a 2-tuple.
        """
        return self.y, self.z

    def xyz(self):
        """Returns the x, y and z values of the component as a 3-tuple.

        Equivalent to ``PositionComponent.getPosition()``
        """
        return self.getPosition()


def distance(a: PositionComponent, b: PositionComponent) -> float:
    """Calculates the distance from ``PositionComponent`` a to ``PositionComponent`` b.

    Parameters
    ----------
    a : PositionComponent
        The first set of coordinates.
    b : PositionComponent
        The second set of coordinates.

    Returns
    -------
    float
        The distance from a to b.
    """
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def distance_sqr(a: PositionComponent, b: PositionComponent) -> float:
    """Calculates the squared distance from ``PositionComponent`` a to ``PositionComponent`` b.

    This function does not call ``math.sqrt()`` so it is more performant than calling ``distance(a,b)``.
    This can be useful in situations where you don't need the exact distance (e.g. when comparing distances).

    Parameters
    ----------
    a : PositionComponent
        The first set of coordinates.
    b : PositionComponent
        The second set of coordinates.

    Returns
    -------
    float
        The squared distance from a to b.
    """
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2


class ConstantGenerator:
    """A functor used to create CellComponents with a constant value.

    The idea behind this class is to create a ``ConstantGenerator(val)`` object and supply it as the generator when
    calling ``addCellComponent`` to a DiscreteWorld (e.g. ``GridWorld``). The component will then be created with all
    cells having ``value == val``.

    Attributes
    ----------
    value : Any
        The value you want to set your cell component's values to.
    """
    def __init__(self, value):
        self.value = value

    def __call__(self, pos: tuple, cells: pandas.DataFrame):
        """Used by the ``addCellComponent`` methods to populate a cell component with the value of ``self.value``.
        """
        return self.value


class LookupGenerator:
    """A functor used to create CellComponents based on a Lookup table.

    The intention behind this class is to add a convenient way for users to create Cell Components with different
    values. This is done by creating a lookup table (of the same dimensions as the environment) and supplying it to the
    generator ``LookupGenerator(lookup_table)``.

    Note that coordinates are filled in a [x, y, z] fashion. This means you may need to transform your data
    (e.g. an image) so that x-coordinates can be referenced first.

    Attributes
    ----------
    table : Any
        The lookup table.
    """
    def __init__(self, table):
        self.table = table

    def __call__(self, pos, cells: pandas.DataFrame):
        """Used by the ``addCellComponent`` methods to populate a cell component with the value of ``self.table``.
        at coordinate ``pos``.
        """
        if type(pos) == int:  # LineWorld
            return self.table[pos]
        elif len(pos) == 2:  # GridWorld
            return self.table[pos[0]][pos[1]]
        else:  # CubeWorld
            return self.table[pos[0]][pos[1]][pos[2]]


class LineWorld(Environment):
    """ LineWorld is a discrete environment with only 1 axis (x-axis). It can be used in place of the base Environment
    class. All agents added to a LineWorld class are given a PositionComponent to denote their place in the world.

    A LineWorld's dimensions are defined by a width property.

    LineWorld.addCellComponent(comp) adds component comp to each of the cells in the environment."""

    __slots__ = ['width', 'cells']

    def __init__(self, width, model, id: str = 'ENVIRONMENT'):

        if width < 1:
            raise Exception("Cannot create a LineWorld with a negative width.")

        super().__init__(model, id=id)
        self.width = width

        # Create cells
        self.cells = pandas.DataFrame({'pos': [x for x in range(width)]})

    def addAgent(self, agent: Agent, xPos: int = 0):
        """Adds an agent to the environment. Overrides the base class function.
        This function will also add a PositionComponent to the agent object.
        If the xPos is greater than the width of the world, an error will be thrown."""

        if xPos >= self.width or xPos < 0:
            raise Exception("Cannot add the Agent to position not on the map.")

        agent.addComponent(PositionComponent(agent, agent.model, x=xPos))
        super().addAgent(agent)

    def addCellComponent(self, name: str, generator):
        """ Adds the component supplied by the generator functor to each of the cells.
        The functor is supplied with the index of the cell and dataframe as input"""

        new_components = [generator(i, self.cells) for i in range(self.width)]
        self.cells[name] = new_components

    def removeAgent(self, agentID: str):
        """ Removes the agent from the environment. Will also remove the PositionComponent from the agent"""
        if agentID in self.agents:
            self.agents[agentID].removeComponent(PositionComponent)

        super().removeAgent(agentID)

    def setModel(self, model: Model):
        super().setModel(model)

    def getAgentsAt(self, xPos: int, leeway: int = 0):
        """Returns a list of agents at position xPos. Will return [] empty if no agents are in that cell.
        If leeway > 0 all agents within the range xPos +/- leeway will be returned as well."""
        return [self.agents[agentKey] for agentKey in self.agents
                if xPos - leeway <= self.agents[agentKey][PositionComponent].x <= xPos + leeway]

    def getDimensions(self):
        return self.width

    def getCell(self, x: int):
        if x < 0 or x >= len(self.cells):
            return None
        else:
            return self.cells.iloc[x]

    def getNeighbours(self, cellID: int, radius: int = 1, moore: bool = False) -> [Agent]:
        """Returns a list of all the neighbouring cells within the specified radius. If moore = true the supplied cell
        will also be included in that list"""
        neighbours = []
        lower_bound = max(0, self.cells['pos'][cellID] - radius)
        upper_bound = min(self.width, self.cells['pos'][cellID] + radius + 1)  # +1 to account for range() exclusion

        for x in range(lower_bound, upper_bound):
            if moore:
                neighbours.append(x)
            elif self.cells['pos'][cellID] != x:
                neighbours.append(x)

        return neighbours

    def move(self, agent: Agent, x: int):
        """Moves an agent x units along the environment.

        The function automatically clamps agent movement to the range ``0 <= x < self.width``.

        Parameters
        ----------
        agent : Agent
            The agent object to be moved.
        x : int
            The number of discrete units to move the agent.

        Raises
        ------
        ComponentNotFoundError
            If ``agent`` does not have a ``PositionComponent``.
        """
        if PositionComponent not in agent:
            raise ComponentNotFoundError(agent, PositionComponent)

        component = agent[PositionComponent]
        component.x = max(min(component.x + x, self.width - 1), 0)

    def move_to(self, agent: Agent, x: int):
        """Moves an agent to position x in the environment.

        Parameters
        ----------
        agent : Agent
            The agent object to be moved.
        x : int
            The new x-coordinate of the agent.

        Raises
        ------
        ComponentNotFoundError
            If ``agent`` does not have a ``PositionComponent``.
        IndexError
            If x-coordinate are out of bounds.
        """
        if PositionComponent not in agent:
            raise ComponentNotFoundError(agent, PositionComponent)
        elif 0 <= x < self.width:
            component = agent[PositionComponent]
            component.x = x
        else:
            raise IndexError(f'Position ({x}) is out of the environment\'s range')


class GridWorld(Environment):
    """ GridWorld is a discrete environment with 2 axes (x,y-axes). It can be used in place of the base Environment
    class. All agents added to a GridWorld class are given a PositionComponent to denote their place in the world.

    A GridWorld's dimensions are defined by a width and height properties.

    GridWorld.addCellComponent(comp) adds component comp to each of the cells in the environment."""

    __slots__ = ['width', 'height', 'cells']

    def __init__(self, width, height, model, id: str = 'ENVIRONMENT'):

        if width < 1 or height < 1:
            raise Exception("Cannot create a GridWorld with a negative width or height.")

        super().__init__(model, id=id)
        self.width = width
        self.height = height

        # Create cells
        self.cells = pandas.DataFrame({'pos': [(x, y) for y in range(height) for x in range(width)]})

    def addAgent(self, agent: Agent, xPos: int = 0, yPos: int = 0):
        """Adds an agent to the environment. Overrides the base class function.
        This function will also add a PositionComponent to the agent object.
        If the xPos or yPos is greater than the width of the world, an error will be thrown."""

        if xPos >= self.width or xPos < 0 or yPos >= self.height or yPos < 0:
            raise Exception("Cannot add the Agent to position not on the map.")

        agent.addComponent(PositionComponent(agent, agent.model, x=xPos, y=yPos))
        super().addAgent(agent)

    def addCellComponent(self, name: str, generator):
        """ Adds the component supplied by the generator functor to each of the cells.
        The functor is supplied with the cell as input"""

        self.cells[name] = [generator(pos, self.cells) for pos in self.cells['pos']]

    def removeAgent(self, agentID: str):
        """ Removes the agent from the environment. Will also remove the PositionComponent from the agent"""
        if agentID in self.agents:
            self.agents[agentID].removeComponent(PositionComponent)

        super().removeAgent(agentID)

    def setModel(self, model: Model):
        super().setModel(model)

    def getAgentsAt(self, xPos: int, yPos: int, xLeeway: int = 0, yLeeway: int = 0):
        """Returns a list of agents at position xPos. Will return [] empty if no agents are in that cell.
        If x or y leeway specified, agents withing range xPos +/- xLeeway and yPos +/- yLeeway will be
        returned as well """
        return [self.agents[agentKey] for agentKey in self.agents
                if xPos - xLeeway <= self.agents[agentKey][PositionComponent].x <= xPos + xLeeway
                and yPos - yLeeway <= self.agents[agentKey][PositionComponent].y <= yPos + yLeeway]

    def getDimensions(self):
        return self.width, self.height

    def getCell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        else:
            return self.cells.iloc[x + (y * self.width)]

    def getNeighbours(self, cell_pos: (int, int), radius: int = 1, moore: bool = False) -> [int]:
        """Returns a list of all the neighbouring cells within the specified radius. If moore = true the supplied cell
        will also be included in that list"""
        neighbours = []

        xlower_bound = max(0, cell_pos[0] - radius)
        xupper_bound = min(self.width, cell_pos[0] + radius + 1)  # +1 to account for range() exclusion

        ylower_bound = max(0, cell_pos[1] - radius)
        yupper_bound = min(self.height, cell_pos[1] + radius + 1)  # +1 to account for range() exclusion
        cellID = discreteGridPosToID(cell_pos[0], cell_pos[1], self.width)

        for y in range(ylower_bound, yupper_bound):
            for x in range(xlower_bound, xupper_bound):
                id = discreteGridPosToID(x, y, self.width)
                if self.cells['pos'][cellID][0] == x and self.cells['pos'][cellID][1] == y:
                    if moore:
                        neighbours.append(id)
                else:
                    neighbours.append(id)

        return neighbours

    def move(self, agent: Agent, x: int = 0, y: int = 0):
        """Moves an agent (x,y) units in the environment.

        The function automatically clamps agent movement to the range ``(0,0) <= x < (self.width,self.height)``.

        Parameters
        ----------
        agent : Agent
            The agent object to be moved.
        x : int, Optional
            The number of discrete units to move the agent. Defaults to 0.
        y : int, Optional
            The number of discrete units to move the agent. Defaults to 0.

        Raises
        ------
        ComponentNotFoundError
            If ``agent`` does not have a ``PositionComponent``.
        """
        if PositionComponent not in agent:
            raise ComponentNotFoundError(agent, PositionComponent)

        component = agent[PositionComponent]
        component.x = max(min(component.x + x, self.width - 1), 0)
        component.y = max(min(component.y + y, self.height - 1), 0)

    def move_to(self, agent: Agent, x: int = 0, y: int = 0):
        """Moves an agent to position (x,y) in the environment.

        Parameters
        ----------
        agent : Agent
            The agent object to be moved.
        x : int, Optional
            The new x-coordinate of the agent. Defaults to 0.
        y : int, Optional
            The new y-coordinate of the agent. Defaults to 0.

        Raises
        ------
        ComponentNotFoundError
            If ``agent`` does not have a ``PositionComponent``.
        IndexError
            If coordinates are out of bounds.
        """
        if PositionComponent not in agent:
            raise ComponentNotFoundError(agent, PositionComponent)
        elif 0 <= x < self.width and 0 <= y < self.height:
            component = agent[PositionComponent]
            component.x = x
            component.y = y
        else:
            raise IndexError(f'Position ({x},{y}) is out of the environment\'s range')


class CubeWorld(Environment):
    """ CubeWorld is a discrete environment with 3 axes (x,y,z-axes). It can be used in place of the base Environment
    class. All agents added to a GridWorld class are given a PositionComponent to denote their place in the world.

    A CubeWorld's dimensions are defined by a width, height and depth properties.

    CubeWorld.addCellComponent(comp) adds component comp to each of the cells in the environment."""

    __slots__ = ['width', 'height', 'depth', 'cells']

    def __init__(self, width, height, depth, model, id: str = 'ENVIRONMENT'):

        if width < 1 or height < 1 or depth < 1:
            raise Exception("Cannot create a CubeWorld with a negative width or height.")

        super().__init__(model, id=id)
        self.width = width
        self.height = height
        self.depth = depth

        # Create cells
        self.cells = pandas.DataFrame({
            'pos': [(x, y, z) for z in range(depth) for y in range(height) for x in range(width)]
        })

    def addAgent(self, agent: Agent, xPos: int = 0, yPos: int = 0, zPos: int = 0.0):
        """Adds an agent to the environment. Overrides the base class function.
        This function will also add a PositionComponent to the agent object.
        If the xPos, yPos or zPos is greater than the width of the world, an error will be thrown."""

        if xPos >= self.width or xPos < 0 or yPos >= self.height or yPos < 0 or zPos >= self.depth or zPos < 0:
            raise Exception("Cannot add the Agent to position not on the map.")

        agent.addComponent(PositionComponent(agent, agent.model, x=xPos, y=yPos, z=zPos))
        super().addAgent(agent)

    def addCellComponent(self, name: str, generator):
        """ Adds the component supplied by the generator functor to each of the cells.
        The functor is supplied with the cell as input"""
        self.cells[name] = [generator(pos, self.cells) for pos in self.cells['pos']]

    def removeAgent(self, agentID: str):
        """ Removes the agent from the environment. Will also remove the PositionComponent from the agent"""
        if agentID in self.agents:
            self.agents[agentID].removeComponent(PositionComponent)

        super().removeAgent(agentID)

    def setModel(self, model: Model):
        super().setModel(model)

    def getAgentsAt(self, xPos: int, yPos: int, zPos: int, xLeeway: int = 0, yLeeway: int = 0, zLeeway: int = 0):
        """Returns a list of agents at position xPos. Will return [] empty if no agents are in that cell
        If x,y or z leeway specified, function will return all agents within the range xPos +/- xLeeway,
        yPos +/- yLeeway and zPos +/- zLeeway."""
        return [self.agents[agentKey] for agentKey in self.agents
                if xPos - xLeeway <= self.agents[agentKey][PositionComponent].x <= xPos + xLeeway
                and yPos - yLeeway <= self.agents[agentKey][PositionComponent].y <= yPos + yLeeway
                and zPos - zLeeway <= self.agents[agentKey][PositionComponent].z <= zPos + zLeeway]

    def getDimensions(self):
        return self.width, self.height, self.depth

    def getCell(self, x, y, z):
        if x < 0 or x >= self.width or y < 0 or y >= self.height or z < 0 or z >= self.depth:
            return None
        else:
            return self.cells['pos'][discreteGridPosToID(x, y, self.width, z, self.height)]

    def getNeighbours(self, cell_pos: (int, int, int), radius: int = 1, moore: bool = False) -> [int]:
        """Returns a list of all the neighbouring cells within the specified radius. If moore = true the supplied cell
        will also be included in that list"""
        neighbours = []
        cellID = discreteGridPosToID(cell_pos[0], cell_pos[0], self.width, cell_pos[2], self.height)

        xlower_bound = max(0, self.cells['pos'][cellID][0] - radius)
        xupper_bound = min(self.width, self.cells['pos'][cellID][0] + radius + 1)

        ylower_bound = max(0, self.cells['pos'][cellID][1] - radius)
        yupper_bound = min(self.height, self.cells['pos'][cellID][1] + radius + 1)

        zlower_bound = max(0, self.cells['pos'][cellID][2] - radius)
        zupper_bound = min(self.depth, self.cells['pos'][cellID][2] + radius + 1)

        for z in range(zlower_bound, zupper_bound):
            for y in range(ylower_bound, yupper_bound):
                for x in range(xlower_bound, xupper_bound):
                    id = discreteGridPosToID(x, y, self.width, z, self.height)
                    if self.cells['pos'][cellID][0] == x and self.cells['pos'][cellID][1] == y and \
                            self.cells['pos'][cellID][2] == z:
                        if moore:
                            neighbours.append(id)
                    else:
                        neighbours.append(id)

        return neighbours

    def move(self, agent: Agent, x: int = 0, y: int = 0, z: int = 0):
        """Moves an agent (x,y,z) units in the environment.

        The function automatically clamps agent movement to the range
        ``(0,0,0) <= x < (self.width,self.height,self.depth)``.

        Parameters
        ----------
        agent : Agent
            The agent object to be moved.
        x : int, Optional
            The number of discrete units to move the agent. Defaults to 0.
        y : int, Optional
            The number of discrete units to move the agent. Defaults to 0.
        z : int, Optional
            The number of discrete units to move the agent. Defaults to 0.

        Raises
        ------
        ComponentNotFoundError
            If ``agent`` does not have a ``PositionComponent``.
        """
        if PositionComponent not in agent:
            raise ComponentNotFoundError(agent, PositionComponent)

        component = agent[PositionComponent]
        component.x = max(min(component.x + x, self.width - 1), 0)
        component.y = max(min(component.y + y, self.height - 1), 0)
        component.z = max(min(component.z + z, self.depth - 1), 0)

    def move_to(self, agent: Agent, x: int = 0, y: int = 0, z: int = 0):
        """Moves an agent to position (x,y,z) in the environment.

        Parameters
        ----------
        agent : Agent
            The agent object to be moved.
        x : int, Optional
            The new x-coordinate of the agent. Defaults to 0.
        y : int, Optional
            The new y-coordinate of the agent. Defaults to 0.
        z : int, Optional
            The new z-coordinate of the agent. Defaults to 0.

        Raises
        ------
        ComponentNotFoundError
            If ``agent`` does not have a ``PositionComponent``.
        IndexError
            If coordinates are out of bounds.
        """
        if PositionComponent not in agent:
            raise ComponentNotFoundError(agent, PositionComponent)
        elif 0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.depth:
            component = agent[PositionComponent]
            component.x = x
            component.y = y
            component.z = z
        else:
            raise IndexError(f'Position ({x},{y},{z}) is out of the environment\'s range')
