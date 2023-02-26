import math
import numpy as np
import pandas

from deprecated import deprecated
from ECAgent.Core import Agent, Environment, Component, Model, ComponentNotFoundError


def discrete_grid_pos_to_id(x: int, y: int = 0, width: int = 0, z: int = 0, height: int = 0):
    """Returns a unique number of based on the x, y and z coordinates entered.

    Uniqueness is dimension dependent. The equation for calculating uniqueness is defined as:
     ``(z * width * height) + (y * width) + x``

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


@deprecated(reason='For not meeting standard python naming conventions. Use "discrete_grid_pos_to_id" instead.')
def discreteGridPosToID(x: int, y: int = 0, width: int = 0, z: int = 0, height: int = 0):  # pragma: no cover
    """Deprecated. Use ``discrete_grid_pos_to_id`` instead."""
    return discrete_grid_pos_to_id(x, y, width, z, height)


class PositionComponent(Component):
    """A position component. It contains three float properties: x, y, z.
    This component can be used to store the position of an Agent in a 1-3D world.
    It is used by ``DiscreteWorld`` classes to do exactly that.
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
    calling ``add_cell_component`` to a DiscreteWorld (e.g. ``GridWorld``). The component will then be created with all
    cells having ``value == val``

    Assuming a ``3x3 DiscreteWorld``::

        env.add_cell_component('constant', ConstantGenerator(1))

    will create a cell component called ``'constant'`` which will have values stored in a
    contiguous array: ``[1,1,1,1,1,1,1,1,1]`` which when viewed in 2D looks like:

    +---------+---------+---------+
    | 1       |  1      |  1      |
    +---------+---------+---------+
    | 1       |  1      |  1      |
    +---------+---------+---------+
    | 1       |  1      |  1      |
    +---------+---------+---------+

    Attributes
    ----------
    value : Any
        The value you want to set your cell component's values to.
    """
    def __init__(self, value):
        self.value = value

    def __call__(self, pos: tuple, cells: pandas.DataFrame):
        """Used by the ``add_cell_component`` methods to populate a cell component with the value of ``self.value``.
        """
        return self.value


class LookupGenerator:
    """A functor used to create CellComponents based on a Lookup table.

    The intention behind this class is to add a convenient way for users to create Cell Components with different
    values. This is done by creating a lookup table (of the same dimensions as the environment) and supplying it to the
    generator ``LookupGenerator(lookup_table)``.

    Note that coordinates are filled in a [x, y, z] fashion. This means you may need to transform your data
    (e.g. an image) so that x-coordinates can be referenced first.

    Assuming a ``3x3 DiscreteWorld``::

        table = [[0, 1, 2],
                 [3, 4, 5],
                 [6, 7, 8]]
        env.add_cell_component('lookup', LookupGenerator(table))

    will create a cell component called ``'lookup'`` which will have values stored in a
    contiguous array: ``[0,1,2,3,4,5,6,7,8]`` which when viewed in 2D looks like:

    +---------+---------+-----------+
    | 6       |  7      |  8        |
    +---------+---------+-----------+
    | 3       |  4      |  5        |
    +---------+---------+-----------+
    | 0       |  1      |  2        |
    +---------+---------+-----------+

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


class SpaceWorld(Environment):
    """Base Class for all Spacial Environments. It inherits from the Environment base class and contains properties
    related to the spacial extents of the environment. Currently, the environment can, at most, be three dimensional.

    Note that the origin is (0,0,0) and is assumed to be located in the bottom left corner of the environment.

    Attributes
    ----------
    width : int
        The width of the environment. This attribute can be thought of as the spacial extent of the x-axis.
    height : int
        The height of the environment. This attribute can be thought of as the spacial extent of the y-axis.
    depth : int
        The depth of the environment. This attribute can be thought of as the spacial extent of the z-axis.
    """
    __slots__ = ['width', 'height', 'depth']

    def __init__(self, model, width: int, height: int = 0, depth: int = 0, id: str = 'ENVIRONMENT'):
        super().__init__(model, id=id)
        self.width = width
        self.height = height
        self.depth = depth

    def add_agent(self, agent: Agent, x_pos: int = 0, y_pos: int = 0, z_pos: int = 0):
        """Adds an agent to the environment. Overrides the base ``Environment.add_agent`` class function.
        This function will also add a ``PositionComponent`` to the agent object.
        If the x, y or z positions are greater than or equal to the width, height and depth of the world
        (or less than zero), an error will be thrown.

        Parameters
        ----------
        agent : Agent
            The agent being added to the environment.
        x_pos : int, Optional
            The starting x-position of the agent. Defaults to 0.
        y_pos : int, Optional
            The starting y-position of the agent. Defaults to 0.
        z_pos : int, Optional
            The starting z-position of the agent. Defaults to 0.

        Raises
        ------
        DuplicateAgentError
            If the agent already exists in the environment.
        Exception
            If the agent's initial position is outside the environment's spacial extents.
        """
        # TODO create Error for being outside spacial extents.
        x_bool = x_pos >= self.width or x_pos < 0 if self.width > 0 else False
        y_bool = y_pos >= self.height or y_pos < 0 if self.height > 0 else False
        z_bool = z_pos >= self.depth or z_pos < 0 if self.depth > 0 else False
        if x_bool or y_bool or z_bool:
            raise Exception("Cannot add the Agent to position not on the map.")

        super().add_agent(agent)
        agent.add_component(PositionComponent(agent, agent.model, x=x_pos, y=y_pos, z=z_pos))

    def remove_agent(self, a_id: str):
        """Removes the agent from the environment. Overrides the base ``Environment.remove_agent`` method.
        This method will also remove the ``PositionComponent`` from the agent.

        Parameters
        ----------
        a_id : str
            The ``id`` of the agent to remove.

        Raises
        ------
        AgentNotFoundError
            If no agent with an ``agent.id == a_id`` can be found.
        """
        if a_id in self.agents:
            self.agents[a_id].remove_component(PositionComponent)

        super().remove_agent(a_id)

    def get_agents_at(self, x_pos: float = 0.0, y_pos: float = 0.0, z_pos: float = 0.0, leeway: float = 0.0,
                      x_leeway: float = 0, y_leeway: float = 0, z_leeway: float = 0) -> [Agent]:
        """Returns a list of agents at position (x_pos, y_pos, z_pos) +/- any leeway.

        The function will return ``[]`` empty if no agents are within the specified region.

        The function also uses the maximum possible leeway for a given axis. So if the following is executed::

            env.get_agents_at(10.0, 10.0, 10.0, leeway = 3.0, y_leeway = 5.0)

        The function will return a list of agents within ``3.0`` units of the coordinates ``(10.0, 10.0, 10.0)`` on the
        x and z axes and within ``5.0`` units of the coordinates ``(10.0, 10.0, 10.0)`` on the y-axis.

        Parameters
        ----------
        x_pos : float, Optional
            The x-coordinate of the search origin point. Defaults to ``0.0``.
        y_pos : float, Optional
            The y-coordinate of the search origin point. Defaults to ``0.0``.
        z_pos : float, Optional
            The z-coordinate of the search origin point. Defaults to ``0.0``.
        leeway : float, Optional
            The general leeway value (i.e. leeway applied to all axes). Defaults to ``0.0``.
        x_leeway : float, Optional
            The x-axis leeway (i.e. leeway applied to x-axis). Defaults to ``0.0``.
        y_leeway : float, Optional
            The y-axis leeway (i.e. leeway applied to y-axis). Defaults to ``0.0``.
        z_leeway : float, Optional
            The z-axis leeway (i.e. leeway applied to z-axis). Defaults to ``0.0``.

        Returns
        -------
        [Agent]
            A list of agents within the specified coordinates. An empty list ``[]`` is returned if no agents are found.
        """

        # TODO Account for clamp mode

        xmin, xmax = min(x_pos - x_leeway, x_pos - leeway), max(x_pos + x_leeway, x_pos + leeway)
        ymin, ymax = min(y_pos - y_leeway, y_pos - leeway), max(y_pos + y_leeway, y_pos + leeway)
        zmin, zmax = min(z_pos - z_leeway, z_pos - leeway), max(z_pos + z_leeway, z_pos + leeway)

        return [self.agents[agentKey] for agentKey in self.agents
                if xmin <= self.agents[agentKey][PositionComponent].x <= xmax
                and ymin <= self.agents[agentKey][PositionComponent].y <= ymax
                and zmin <= self.agents[agentKey][PositionComponent].z <= zmax]

    def get_dimensions(self) -> (int, int, int):
        """Returns a 3-tuple containing the extents of the environment:
        ``(width, height, depth)``."""
        return self.width, self.height, self.depth

    def move(self, agent: Agent, x: float = 0, y: float = 0, z: float = 0):
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

    def move_to(self, agent: Agent, x: float = 0, y: float = 0, z: float = 0):
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
        elif (0 <= x < self.width or self.width < 1) and (0 <= y < self.height or self.height < 1) and (
                0 <= z < self.depth or self.depth < 1):
            component = agent[PositionComponent]
            component.x = x
            component.y = y
            component.z = z
        else:
            raise IndexError(f'Position ({x},{y},{z}) is out of the environment\'s range')


class DiscreteWorld(SpaceWorld):
    """Base Class for all Discrete Spacial Environments. It inherits from ``SpaceWorld``class and contains properties
    and methods related to grid-based environments.

    This class also adds functionality to add cell components. This is a special type of component that stores a single
    value for every cell in the DiscreteWorld.

    Assuming a ``3x3 DiscreteWorld``::

        env = DiscreteWorld(model, 3, 3)

    You can add a cell component to the environment by calling::

        env.add_cell_component('example', generator)

    Where ``'example'`` will be the name of cell component. The second argument is known as a generator and is a function
    object (functor) that populates the gridworld with the value of the cell component.

    A custom generator can be written as follows::

        def custom_generator(pos, cells):
            # add logic here
            return value_of_cell

    When writing a generator, your function must accept two arguments: the ``cells`` which is the pandas dataframe of
    of the environment and ``pos`` which is a 3-tuple which contains the coordinates ``(x,y,z)`` of the grid cell
    you are generating for. So using the example::

        def sum_generator(pos, cells):
            return sum(*pos)

        env.add_cell_component('sum', sum_generator)

    Our original ``3x3 DiscreteWorld`` will get a cell component called ``'sum'`` which will have values stored in a
    contiguous array: ``[0,1,2,1,2,3,2,3,4]`` which when viewed in 2D looks like:

    +---------+---------+---------+
    | 2       |  3      |  4      |
    +---------+---------+---------+
    | 1       |  2      |  3      |
    +---------+---------+---------+
    | 0       |  1      |  2      |
    +---------+---------+---------+

    **Note** that all cell components are stored as 1D arrays which you can access using ``env.cells[cell_name]''. To
    translate a 3d coordinate (or PositionComponent) into a unique integer to get the value of a specific cell in a
    ``DiscreteWorld``, use the ``discrete_grid_pos_to_id`` method. Additionally, all ``DiscreteWorld`` environments
    are initialized with a ``'pos'`` cell component which contains the 3d coordinate representation of the cell.

    Attributes
    ----------
    cells : Pandas.DataFrame
        A table containing all of the cell components in the environment.
    """
    def __init__(self, model, width: int, height: int = 0, depth: int = 0, id: str = 'ENVIRONMENT'):
        super().__init__(model, width, height, depth, id)

        # Create cells
        self.cells = pandas.DataFrame({
            'pos': [(x, y, z) for z in range(max(depth, 1)) for y in range(max(height, 1)) for x in range(max(width, 1))]
        })

    def add_cell_component(self, name: str, generator):
        """Adds the component supplied by the generator functor to each of the cells.
        The functor is supplied with the cell's position ``(x,y,z)`` and the environment pandas dataframe as input.

        A custom generator can be written as follows::

            def custom_generator(pos, cells):
                # add logic here
                return value_of_cell

        You can also use the one of the included generators: ``ConstantGenerator`` or ``LookupGenerator``. Alternatively,
        you can populate the cells by directly supplying their data as a 1D contiguous array that is the same size
        as the environment. Assuming a ``3x3 GridWorld``::

            data = [0, 1, 2, 3, 4, 5, 6, 7, 8]
            env.add_cell_component('data', data)

        will create a cell component called ``'data'`` which will have values stored in a
        contiguous array: ``[0,1,2,3,4,5,6,7,8]`` which when viewed in 2D looks like:

        +---------+---------+---------+
        | 6       |  7      |  8      |
        +---------+---------+---------+
        | 3       |  4      |  5      |
        +---------+---------+---------+
        | 0       |  1      |  2      |
        +---------+---------+---------+

        Parameters
        ----------
        name : str
            The name of the cell component.
        generator : obj | numpy.ndarray | list
            The generator used to populate the cell component. If a obj is supplied, it must have the ``__call__``
            method implemented. If a ``numpy.ndarray`` or ``list`` is used, it must be 1-dimensional and of size
            ``width * height * depth``.
        """
        if isinstance(generator, np.ndarray):
            self.cells[name] = np.copy(generator)
        elif isinstance(generator, list):
            self.cells[name] = generator
        else:
            self.cells[name] = [generator(pos, self.cells) for pos in self.cells['pos']]

    @deprecated(reason='For not meeting standard python naming conventions. Use "add_cell_component" instead.')
    def addCellComponent(self, name: str, generator):  # pragma: no cover
        """Deprecated. Use ``add_cell_component`` instead."""
        self.add_cell_component(name, generator)

    def remove_cell_component(self, name: str):
        """Removes a cell component from the environment.

        Parameters
        ----------
        name : str
            The name of the cell component.

        Raises
        ------
        ComponentNotFoundError
            If no cell component with the specified name can be found.
        """
        if name not in self.cells:
            raise ComponentNotFoundError(self, name)
        else:
            self.cells.drop(columns=[name], inplace=True)

    def get_cell(self, x, y: int = 0, z: int = 0) -> pandas.Series:
        """Returns a ``Pandas.Series`` containing the values of cell components at the specified grid cell.

        Assuming a ``3x1 DiscreteWorld`` with two cell components called ``'rainfall'`` and ``'slope'``::

            # The cell DataFrame will look something like:
            [{'pos': (0,0,0), 'rainfall': 10.0, 'slope': 4.0},
             {'pos': (1,0,0), 'rainfall': 22.0, 'slope': 21.0},
             {'pos': (2,0,0), 'rainfall': 15.0, 'slope': 32.0}]

            cell = env.get_cell(1)
            print(cell)

            # Will print something like:
            {'pos': (1,0,0), 'rainfall': 22.0, 'slope': 21.0}

        Parameters
        ----------
        x : int
            The x-coordinate.
        y : int, Optional
            The y-coordinate. Defaults to 0.
        z : int, Optional
            The z-coordinate. Defaults to 0.

        Returns
        -------
        Pandas.Series
            Containing all of the values for the cell components at the indexed grid cell.

        Raises
        ------
        IndexError
            If the specified coordinates are our outside the bound of the environment.
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height or z < 0 or z >= self.depth:
            raise IndexError(f'Coordinate ({x},{y},{z}) is not within the bounds of the environment.')
        else:
            return self.cells.iloc[discrete_grid_pos_to_id(x, y, self.width, z, self.height)]

    @deprecated(reason='For not meeting standard python naming conventions. Use "get_cell" instead.')
    def getCell(self, x, y: int = 0, z: int = 0) -> pandas.Series:  # pragma: no cover
        """Deprecated. Use ``get_cell`` instead."""
        return self.get_cell(x, y, z)

    def _get_cell_pos_as_tuple(self, cell_pos) -> (int, int, int):
        """Returns the coordinates of a ``DiscreteWorld`` cell based in the type supplied by ``cell_pos``.

        The function accepts three types: ``int``, ``tuple`` or ``PositionComponent``.
        If ``int`` is supplied, it will be assumed to be the *unique identifier* of the cell (i.e. the value returned
        by ``discrete_grid_pos_to_id()``. If a ``tuple`` is supplied, it is assumed that it will be the coordinates of
        the cell (e.g. ``(2,5,3)``). If a ``PositionComponent`` is supplied, it's values will be truncated and turned
        into a 3d integer coordinate (i.e. A ``PositionComponent`` with value ``x = 2.5, y = 5.9, z = 3.1``) will be
        converted into coordinates ``(2,5,3)``.

        Parameters
        ----------
        cell_pos : int, tuple, PositionComponent
            The cell whose neighbours you want to get.

        Returns
        -------
        (int, int, int)
            The coordinates of the cell represented as a 3-tuple.

        Raises
        ------
        TypeError
            If the type of cell_pos is not ``int``, ``tuple`` or ``PositionComponent``.
        """
        if isinstance(cell_pos, int):
            return self.cells['pos'][cell_pos]
        elif isinstance(cell_pos, tuple):
            return cell_pos
        elif isinstance(cell_pos, PositionComponent):
            center = cell_pos.xyz()
            # Convert to int
            return int(center[0]), int(center[1]), int(center[2])
        else:
            raise TypeError(f'cell_pos of type {type(cell_pos)} is not supported. Use an int, tuple or '
                            f'PositionComponent instead')

    def get_moore_neighbours(self, cell_pos, radius: int = 1, incl_center: bool = False, ret_type: type = int) -> list:
        """Returns a list of all cells within the specified moore neighbourhood.
        If incl_center = true the supplied cell will also be included in that list.

        The function accepts three types: ``int``, ``tuple`` or ``PositionComponent``.
        If ``int`` is supplied, it will be assumed to be the *unique identifier* of the cell (i.e. the value returned
        by ``discrete_grid_pos_to_id()``. If a ``tuple`` is supplied, it is assumed that it will be the coordinates of
        the cell (e.g. ``(2,5,3)``). If a ``PositionComponent`` is supplied, it's values will be truncated and turned
        into a 3d integer coordinate (i.e. A ``PositionComponent`` with value ``x = 2.5, y = 5.9, z = 3.1``) will be
        converted into coordinates ``(2,5,3)``.

        The same functionality applied to the ``ret_type`` parameters. By default a list of integers containing the
        *unique identifiers* of the neighbouring cells are returned. If ``tuple`` is supplied, the function will return
        the 3d coordinates of the neighbouring will be returned.

        Parameters
        ----------
        cell_pos : int, tuple, PositionComponent
            The cell whose neighbours you want to get.
        radius : int, Optional
            The size of the Moore neighbourhood. Defaults to ``1``.
        incl_center : bool, Optional
            Flags whether you want the supplied ``cell_pos`` to be included in the returned ``list``
        ret_type : type, Optional
            The representation of the neighbouring cells, Defaults to ``int`` but may also be ``tuple``.

        Returns
        -------
        list
            A list of neighbouring cells in the representation specified by ``ret_type``. Defaults to a list of ``int``.

        Raises
        ------
        TypeError
            If the type of cell_pos is not ``int``, ``tuple`` or ``PositionComponent`` or if the type of ``ret_type`` is
            not ``int`` or ``tuple``.
        """
        center = self._get_cell_pos_as_tuple(cell_pos)
        # Get search bounds
        if self.width > 0:
            xlower_bound = max(0, center[0] - radius)
            xupper_bound = min(self.width, center[0] + radius + 1)
        else:
            xlower_bound, xupper_bound = 0, 1

        if self.height > 0:
            ylower_bound = max(0, center[1] - radius)
            yupper_bound = min(self.height, center[1] + radius + 1)
        else:
            ylower_bound, yupper_bound = 0, 1

        if self.depth > 0:
            zlower_bound = max(0, center[2] - radius)
            zupper_bound = min(self.depth, center[2] + radius + 1)
        else:
            zlower_bound, zupper_bound = 0, 1

        def if_int(env, x, y, z):
            return discrete_grid_pos_to_id(x, y, env.width, z, env.height)

        def if_tuple(env, x, y, z):
            return x, y, z

        if ret_type == int:
            ret_func = if_int
        elif ret_type == tuple:
            ret_func = if_tuple
        else:
            raise TypeError(f'ret_type of type {ret_type} is not supported. Use an int or tuple instead.')

        neighbours = []
        for z in range(zlower_bound, zupper_bound):
            for y in range(ylower_bound, yupper_bound):
                for x in range(xlower_bound, xupper_bound):
                    val = ret_func(self, x, y, z)
                    if center[0] == x and center[1] == y and center[2] == z:
                        if incl_center:
                            neighbours.append(val)
                    else:
                        neighbours.append(val)

        return neighbours

    def get_neumann_neighbours(self, cell_pos, radius: int = 1, incl_center: bool = False, ret_type: type = int) -> list:
        """Returns a list of all cells within the specified von Neumann neighbourhood.
        If incl_center = true the supplied cell will also be included in that list.

        The function accepts three types: ``int``, ``tuple`` or ``PositionComponent``.
        If ``int`` is supplied, it will be assumed to be the *unique identifier* of the cell (i.e. the value returned
        by ``discrete_grid_pos_to_id()``. If a ``tuple`` is supplied, it is assumed that it will be the coordinates of
        the cell (e.g. ``(2,5,3)``). If a ``PositionComponent`` is supplied, it's values will be truncated and turned
        into a 3d integer coordinate (i.e. A ``PositionComponent`` with value ``x = 2.5, y = 5.9, z = 3.1``) will be
        converted into coordinates ``(2,5,3)``.

        The same functionality applied to the ``ret_type`` parameters. By default a list of integers containing the
        *unique identifiers* of the neighbouring cells are returned. If ``tuple`` is supplied, the function will return
        the 3d coordinates of the neighbouring will be returned.

        Parameters
        ----------
        cell_pos : int, tuple, PositionComponent
            The cell whose neighbours you want to get.
        radius : int, Optional
            The size of the Moore neighbourhood. Defaults to ``1``.
        incl_center : bool, Optional
            Flags whether you want the supplied ``cell_pos`` to be included in the returned ``list``
        ret_type : type, Optional
            The representation of the neighbouring cells, Defaults to ``int`` but may also be ``tuple``.

        Returns
        -------
        list
            A list of neighbouring cells in the representation specified by ``ret_type``. Defaults to a list of ``int``.

        Raises
        ------
        TypeError
            If the type of cell_pos is not ``int``, ``tuple`` or ``PositionComponent`` or if the type of ``ret_type`` is
            not ``int`` or ``tuple``.
        """
        center = self._get_cell_pos_as_tuple(cell_pos)
        # Get search bounds
        if self.width > 0:
            xlower_bound = max(0, center[0] - radius)
            xupper_bound = min(self.width, center[0] + radius + 1)
        else:
            xlower_bound, xupper_bound = 0, 1

        if self.height > 0:
            ylower_bound = max(0, center[1] - radius)
            yupper_bound = min(self.height, center[1] + radius + 1)
        else:
            ylower_bound, yupper_bound = 0, 1

        if self.depth > 0:
            zlower_bound = max(0, center[2] - radius)
            zupper_bound = min(self.depth, center[2] + radius + 1)
        else:
            zlower_bound, zupper_bound = 0, 1

        def if_int(env, x, y, z):
            return discrete_grid_pos_to_id(x, y, env.width, z, env.height)

        def if_tuple(env, x, y, z):
            return x, y, z

        if ret_type == int:
            ret_func = if_int
        elif ret_type == tuple:
            ret_func = if_tuple
        else:
            raise TypeError(f'ret_type of type {ret_type} is not supported. Use an int or tuple instead.')

        neighbours = []
        for z in range(zlower_bound, zupper_bound):
            for y in range(ylower_bound, yupper_bound):
                for x in range(xlower_bound, xupper_bound):
                    if abs(x - center[0]) + abs(y - center[1]) + abs(z - center[2]) < radius + 1:  # Calc Manhattan
                        val = ret_func(self, x, y, z)
                        if center[0] == x and center[1] == y and center[2] == z:
                            if incl_center:
                                neighbours.append(val)
                        else:
                            neighbours.append(val)
        return neighbours

    def get_neighbours(self, cell_pos, radius: int = 1, incl_center: bool = False, ret_type: type = int,
                       mode: str = 'moore') -> list:
        """Returns a list of all cells within the specified neighbourhood.
        If incl_center = true the supplied cell will also be included in that list. Both Moore and Von Neumann
        neighbourhoods are supported.

        The function accepts three types: ``int``, ``tuple`` or ``PositionComponent``.
        If ``int`` is supplied, it will be assumed to be the *unique identifier* of the cell (i.e. the value returned
        by ``discrete_grid_pos_to_id()``. If a ``tuple`` is supplied, it is assumed that it will be the coordinates of
        the cell (e.g. ``(2,5,3)``). If a ``PositionComponent`` is supplied, it's values will be truncated and turned
        into a 3d integer coordinate (i.e. A ``PositionComponent`` with value ``x = 2.5, y = 5.9, z = 3.1``) will be
        converted into coordinates ``(2,5,3)``.

        The same functionality applied to the ``ret_type`` parameters. By default a list of integers containing the
        *unique identifiers* of the neighbouring cells are returned. If ``tuple`` is supplied, the function will return
        the 3d coordinates of the neighbouring will be returned.

        Parameters
        ----------
        cell_pos : int, tuple, PositionComponent
            The cell whose neighbours you want to get.
        radius : int, Optional
            The size of the Moore neighbourhood. Defaults to ``1``.
        incl_center : bool, Optional
            Flags whether you want the supplied ``cell_pos`` to be included in the returned ``list``
        ret_type : type, Optional
            The representation of the neighbouring cells, Defaults to ``int`` but may also be ``tuple``.
        mode : str
            The type of neighbourhood to return. Can either be ``'moore'`` or ``'neumann'``. Defaults to ``'moore'`.

        Returns
        -------
        list
            A list of neighbouring cells in the representation specified by ``ret_type``. Defaults to a list of ``int``.

        Raises
        ------
        TypeError
            If the type of cell_pos is not ``int``, ``tuple`` or ``PositionComponent`` or if the type of ``ret_type`` is
            not ``int`` or ``tuple``.
        KeyError
            If the ``mode`` supplied is not ``'moore'`` or ``'neumann'``.
        """
        if mode == 'moore':
            return self.get_moore_neighbours(cell_pos, radius, incl_center, ret_type)
        elif mode == 'neumann':
            return self.get_neumann_neighbours(cell_pos, radius, incl_center, ret_type)
        else:
            raise KeyError(f'Mode {mode} unrecognized. Use either "moore" or "neumann".')


class LineWorld(DiscreteWorld):
    """LineWorld is a discrete environment with only 1 axis (x-axis). It is a simplified version of its parent
    ``DiscreteWorld``.

    A LineWorld's dimensions are defined by a ``width`` property.

    Attributes
    ----------
    width : int
        The width of the environment. This attribute can be thought of as the spacial extent of the x-axis.
    """

    def __init__(self, model: Model, width: int, id: str = 'ENVIRONMENT'):
        """Initializes a ``LineWorld`` object.

        Parameters
        ----------
        model : Model
            The model the environment belongs to.
        width : int
            The width of the ``LineWorld``.
        id : str, Optional
            id of the ``LineWorld``.

        Raises
        ------
        IndexError
            If the ``width`` of the environment is negative.
        """

        if width < 1:
            raise IndexError("Cannot create a LineWorld with a negative width.")

        super().__init__(model, width, 0, 0, id)

    def get_dimensions(self) -> int:
        """Gets the dimension of the ``LineWorld``.
        Returns:
        int
            The ``width`` of the ``LineWorld``.
        """
        return self.width


class GridWorld(DiscreteWorld):
    """GridWorld is a discrete environment with 2 axes (x and y). It is a simplified version of its parent
    ``DiscreteWorld``.

    A GridWorld's dimensions are defined by a ``width`` and ``height`` properties.

    Attributes
    ----------
    width : int
        The width of the environment. This attribute can be thought of as the spacial extent of the x-axis.
    height : int
        The height of the environment. This attribute can be thought of as the spacial extent of the y-axis.
    """

    def __init__(self, model: Model, width: int, height: int, id: str = 'ENVIRONMENT'):

        if width < 1 or height < 1:
            raise IndexError("Cannot create a GridWorld with a negative width or height.")

        super().__init__(model, width, height, 0, id=id)

    def get_dimensions(self) -> (int, int):
        """Gets the dimension of the ``GridWorld``.
        Returns:
        (int, int)
            The ``width`` and ``height`` of the ``GridWorld``.
        """
        return self.width, self.height
