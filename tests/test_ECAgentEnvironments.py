import numpy as np
import pytest

from ECAgent.Core import *
from ECAgent.Environments import *


def test_discrete_grid_pos_to_id():
    assert (4 * 3 * 5) + (2 * 3) + 1 == discrete_grid_pos_to_id(1, 2, 3, 4, 5)


class TestPositionComponent:

    def test__init__(self):
        model = Model()
        agent = Agent("a1", model)

        # Test default case
        pos = PositionComponent(agent,model)

        assert pos.x == 0.0
        assert pos.y == 0.0
        assert pos.z == 0.0
        assert pos.model is model
        assert pos.agent is agent

    def test_get_position(self):
        pos = PositionComponent(None, None, 1, 2, 3)
        assert pos.get_position() == (1, 2, 3)

    def test_shorthands(self):
        pos = PositionComponent(None, None, 1, 2, 3)
        assert pos.xy() == (1, 2)
        assert pos.xz() == (1, 3)
        assert pos.yz() == (2, 3)
        assert pos.xyz() == (1, 2, 3)


def test_distance():
    a = PositionComponent(None, None, 2, 5, 3)
    b = PositionComponent(None, None, 0, 7, 4)
    assert -0.0005 < distance(a , b) - 3 < 0.0005


def test_distance_sqr():
    a = PositionComponent(None, None, 2, 5, 3)
    b = PositionComponent(None, None, 0, 7, 4)
    assert -0.0005 < distance_sqr(a , b) - 9 < 0.0005


class TestConstantGenerator:

    def test__init__(self):
        generator = ConstantGenerator(5)
        assert generator.value == 5

    def test__call__(self):
        generator = ConstantGenerator(5)
        assert generator(None, None) == 5


class TestLookupGenerator:

    def test__init__(self):
        table = [5, 5, 5]
        generator = LookupGenerator(table)
        assert generator.table == table

    def test__call__(self):

        one_d = [1, 2, 3]

        two_d = [[1, 2, 3],
                 [4, 5, 6]]

        three_d = [
            [
                [1,2,3],
                [4, 5, 6]
            ],
            [
                [7, 8, 9],
                [10, 11, 12]
            ]
        ]

        generator = LookupGenerator(one_d)
        assert generator(1, None) == 2

        generator = LookupGenerator(two_d)
        assert generator((1,1), None) == 5

        generator = LookupGenerator(three_d)
        assert generator((1,1,1), None) == 11


class TestSpaceWorld:

    def test__init__(self):
        model = Model()

        # Test default with width
        env = SpaceWorld(model, 5)
        assert env.width == 5
        assert env.height == 0
        assert env.depth == 0
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        # Test default with width and height
        env = SpaceWorld(model, 5, 5)
        assert env.width == 5
        assert env.height == 5
        assert env.depth == 0
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        # Test default with width, height and depth
        env = SpaceWorld(model, 5, 5, 5)
        assert env.width == 5
        assert env.height == 5
        assert env.depth == 5
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

    def test_add_agent(self):
        model = Model()
        model.environment = SpaceWorld(model, 5, 5, 5)
        agent = Agent("a1", model)

        # Test case when agent is added outside of the environment's dimensions [<0]
        with pytest.raises(Exception):
            model.environment.add_agent(agent, -1, 0, 0)

        with pytest.raises(Exception):
            model.environment.add_agent(agent, 0, -1, 0)

        with pytest.raises(Exception):
            model.environment.add_agent(agent, 0, 0, -1)

        # Test case when agent is added outside of the environment's dimensions [>width]
        with pytest.raises(Exception):
            model.environment.add_agent(agent, 5, 0, 0)

        with pytest.raises(Exception):
            model.environment.add_agent(agent, 0, 5, 0)

        with pytest.raises(Exception):
            model.environment.add_agent(agent, 0, 0, 5)

        # Test default case
        model.environment.add_agent(agent)
        assert len(model.environment.agents) == 1
        assert model.environment.get_agent(agent.id) == agent
        assert agent[PositionComponent].x == 0 and agent[PositionComponent].y == 0 and agent[PositionComponent].z == 0

        # Test when agent is added twice
        with pytest.raises(DuplicateAgentError):
            model.environment.add_agent(agent)

        # Test case when position is specified
        model.environment.remove_agent(agent.id)

        model.environment.add_agent(agent, 1, 2, 3)
        assert len(model.environment.agents) == 1
        assert model.environment.get_agent(agent.id) == agent
        assert agent[PositionComponent].x == 1 and agent[PositionComponent].y == 2 and agent[PositionComponent].z == 3

        # Test when width is 0
        model = Model()
        model.environment = SpaceWorld(model, 0, 5, 5)
        agent = Agent("a1", model)
        model.environment.add_agent(agent, y_pos=2, z_pos=2)

        assert len(model.environment.agents) == 1
        assert model.environment.get_agent(agent.id) == agent
        assert agent[PositionComponent].x == 0 and agent[PositionComponent].y == 2 and agent[PositionComponent].z == 2

        # Test when height is 0
        model = Model()
        model.environment = SpaceWorld(model, 5, 0, 5)
        agent = Agent("a1", model)
        model.environment.add_agent(agent, x_pos=2, z_pos=2)

        assert len(model.environment.agents) == 1
        assert model.environment.get_agent(agent.id) == agent
        assert agent[PositionComponent].x == 2 and agent[PositionComponent].y == 0 and agent[PositionComponent].z == 2

        # Test when depth is 0
        model = Model()
        model.environment = SpaceWorld(model, 5, 5, 0)
        agent = Agent("a1", model)
        model.environment.add_agent(agent, x_pos=2, y_pos=2)

        assert len(model.environment.agents) == 1
        assert model.environment.get_agent(agent.id) == agent
        assert agent[PositionComponent].x == 2 and agent[PositionComponent].y == 2 and agent[PositionComponent].z == 0

    def test_remove_agent(self):
        model = Model()
        model.environment = DiscreteWorld(model, 5, 5, 5)
        agent = Agent("a1", model)
        model.environment.add_agent(agent)
        model.environment.remove_agent(agent.id)

        # Test removal
        assert len(model.environment.agents) == 0
        assert agent[PositionComponent] is None

        # Test removal when agent doesn't exist in t
        with pytest.raises(AgentNotFoundError):
            model.environment.remove_agent(agent.id)

    def test_get_agents_at(self):
        model = Model()
        model.environment = DiscreteWorld(model, 5, 5, 5)
        agent = Agent("a1", model)
        agent2 = Agent("a2", model)

        model.environment.add_agent(agent, 0, 0, 0)
        model.environment.add_agent(agent2, 2, 2, 2)

        # Test empty case
        assert model.environment.get_agents_at(5, 5, 5) == []

        # Test non empty case
        assert model.environment.get_agents_at(0, 0, 0) == [agent]

        # Test General Leeway case
        assert model.environment.get_agents_at(0, 0, 0, 2) == [agent, agent2]

        # Test Specific Leeway case
        assert model.environment.get_agents_at(0, 0, 0, 0, 2, 2, 2) == [agent, agent2]

        # Test Greater than Leeway case
        assert model.environment.get_agents_at(0, 0, 0, 2, 1, 1, 1) == [agent, agent2]

    def test_get_dimensions(self):
        env = SpaceWorld(Model(), 1, 2, 3)
        assert env.get_dimensions() == (1, 2, 3)

    def test_move(self):
        model = Model()
        model.environment = SpaceWorld(model, 5, 5, 5)
        agent = Agent("a1", model)
        agent2 = Agent("a2", model)

        model.environment.add_agent(agent, 0, 0, 0)
        model.environment.add_agent(agent2, 4, 4, 4)

        # Test Default case
        model.environment.move(agent)
        assert agent[PositionComponent].x == 0
        assert agent[PositionComponent].y == 0
        assert agent[PositionComponent].z == 0

        # Test out of bounds on the left
        model.environment.move(agent, -1, -1, -1)
        assert agent[PositionComponent].x == 0
        assert agent[PositionComponent].y == 0
        assert agent[PositionComponent].z == 0

        # Test valid move to the right
        model.environment.move(agent, 2, 2, 2)
        assert agent[PositionComponent].x == 2
        assert agent[PositionComponent].y == 2
        assert agent[PositionComponent].z == 2

        # Test outs of bounds on the right
        model.environment.move(agent2, 1, 1, 1)
        assert agent2[PositionComponent].x == 4
        assert agent2[PositionComponent].y == 4
        assert agent2[PositionComponent].z == 4

        # Test valid move to the left
        model.environment.move(agent2, -2, -2, -2)
        assert agent2[PositionComponent].x == 2
        assert agent2[PositionComponent].y == 2
        assert agent2[PositionComponent].z == 2

        # Test if updates reflect in environment
        assert len(model.environment.get_agents_at(2,2,2)) == 2

        # Test without component
        agent3 = Agent('a3', model)
        with pytest.raises(ComponentNotFoundError):
            model.environment.move(agent3)

    def test_move_to(self):
        model = Model()
        model.environment = SpaceWorld(model, 5, 5, 5)
        agent = Agent("a1", model)

        model.environment.add_agent(agent, 0, 0, 0)

        # Test Default case
        model.environment.move_to(agent)
        assert agent[PositionComponent].x == 0
        assert agent[PositionComponent].y == 0
        assert agent[PositionComponent].z == 0

        # Test out of bounds
        with pytest.raises(IndexError):
            model.environment.move_to(agent, -1, -1, -1)

        # Test valid move
        model.environment.move_to(agent, 2, 2, 2)
        assert agent[PositionComponent].x == 2
        assert agent[PositionComponent].y == 2
        assert agent[PositionComponent].z == 2

        # Test without component
        agent2 = Agent('a2', model)
        with pytest.raises(ComponentNotFoundError):
            model.environment.move_to(agent2)

        # Test with no x-dim
        model = Model()
        model.environment = SpaceWorld(model, 0, 5, 5)
        agent = Agent("a1", model)
        model.environment.add_agent(agent, 0, 0, 0)
        model.environment.move_to(agent, y=2, z=2)
        assert agent[PositionComponent].xyz() == (0, 2, 2)

        # Test with no y-dim
        model = Model()
        model.environment = SpaceWorld(model, 5, 0, 5)
        agent = Agent("a1", model)
        model.environment.add_agent(agent, 0, 0, 0)
        model.environment.move_to(agent, x=2, z=2)
        assert agent[PositionComponent].xyz() == (2, 0, 2)

        # Test with no z-dim
        model = Model()
        model.environment = SpaceWorld(model, 5, 5, 0)
        agent = Agent("a1", model)
        model.environment.add_agent(agent, 0, 0, 0)
        model.environment.move_to(agent, x=2, y=2)
        assert agent[PositionComponent].xyz() == (2, 2, 0)


class TestDiscreteWorld:

    def test__init__(self):

        model = Model()

        # Test default with width
        env = DiscreteWorld(model, 5)
        assert env.width == 5
        assert env.height == 0
        assert env.depth == 0
        assert len(env.cells['pos']) == 5
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        for i in range(len(env.cells['pos'])):
            pos = env.cells['pos'][i]
            assert discrete_grid_pos_to_id(pos[0]) == i

        # Test default with width and height
        env = DiscreteWorld(model, 5, 5)
        assert env.width == 5
        assert env.height == 5
        assert env.depth == 0
        assert len(env.cells['pos']) == 25
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        for i in range(len(env.cells['pos'])):
            pos = env.cells['pos'][i]
            assert discrete_grid_pos_to_id(pos[0], pos[1], 5) == i

        # Test default with width, height and depth
        env = DiscreteWorld(model, 5, 5, 5)
        assert env.width == 5
        assert env.height == 5
        assert env.depth == 5
        assert len(env.cells['pos']) == 125
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        for i in range(len(env.cells['pos'])):
            pos = env.cells['pos'][i]
            assert discrete_grid_pos_to_id(pos[0], pos[1], 5, pos[2], 5) == i

    def test_add_cell_component(self):

        env = DiscreteWorld(Model(), 5, 5, 5)

        # Test default generator
        def generator(pos: (int, int, int), pd):
            return discrete_grid_pos_to_id(pos[0], pos[1], 5, pos[2], 5)

        env.add_cell_component('default', generator)
        for i in range(125):
            assert env.cells['default'][i] == i

        # Test list
        data = [i for i in range(125)]
        env.add_cell_component('list', data)
        for i in range(125):
            assert env.cells['list'][i] == i

        # Test numpy array
        data = np.arange(125, dtype=int)
        env.add_cell_component('numpy', data)
        for i in range(125):
            assert env.cells['numpy'][i] == i

    def test_remove_cell_component(self):
        env = DiscreteWorld(Model(), 5,)

        # Test error case
        with pytest.raises(ComponentNotFoundError):
            env.remove_cell_component('test')

        # Test default case
        env.add_cell_component('test', ConstantGenerator(0))
        assert 'test' in env.cells
        env.remove_cell_component('test')
        assert 'test' not in env.cells

    def test_get_cell(self):
        env = DiscreteWorld(Model(), 5, 5, 5)

        # Test error cases
        with pytest.raises(IndexError):
            env.get_cell(-1, 0, 0)

        with pytest.raises(IndexError):
            env.get_cell(5, 0, 0)

        with pytest.raises(IndexError):
            env.get_cell(0, -1, 0)

        with pytest.raises(IndexError):
            env.get_cell(0, 5, 0)

        with pytest.raises(IndexError):
            env.get_cell(0, 0, -1)

        with pytest.raises(IndexError):
            env.get_cell(0, 0, 5)

        # Test non error case
        assert env.get_cell(1, 1, 1).equals(env.cells.iloc[31])

    def test_get_cell_as_tuple(self):

        model = Model()
        env = DiscreteWorld(model, 3, 3, 3)
        # Test int case
        assert env._get_cell_pos_as_tuple(discrete_grid_pos_to_id(1, 1, 3, 1, 3)) == (1,1,1)

        # Test tuple case
        assert env._get_cell_pos_as_tuple((1, 1, 1)) == (1, 1, 1)

        # Test PositionComponent case
        assert  env._get_cell_pos_as_tuple(PositionComponent(None, None, 1, 1, 1)) == (1, 1, 1)

        # Test wrong type case
        with pytest.raises(TypeError):
            env.get_moore_neighbours('(1, 1, 1)')

    def test_get_moore_neighbours(self):
        model = Model()
        env = DiscreteWorld(model, 3, 3, 3)

        def test_111(neighbours):
            assert len(neighbours) == 26
            assert neighbours[0] == discrete_grid_pos_to_id(0, 0, env.width, 0, env.height)
            assert neighbours[1] == discrete_grid_pos_to_id(1, 0, env.width, 0, env.height)
            assert neighbours[2] == discrete_grid_pos_to_id(2, 0, env.width, 0, env.height)
            assert neighbours[3] == discrete_grid_pos_to_id(0, 1, env.width, 0, env.height)
            assert neighbours[4] == discrete_grid_pos_to_id(1, 1, env.width, 0, env.height)
            assert neighbours[5] == discrete_grid_pos_to_id(2, 1, env.width, 0, env.height)
            assert neighbours[6] == discrete_grid_pos_to_id(0, 2, env.width, 0, env.height)
            assert neighbours[7] == discrete_grid_pos_to_id(1, 2, env.width, 0, env.height)
            assert neighbours[8] == discrete_grid_pos_to_id(2, 2, env.width, 0, env.height)

            assert neighbours[9] == discrete_grid_pos_to_id(0, 0, env.width, 1, env.height)
            assert neighbours[10] == discrete_grid_pos_to_id(1, 0, env.width, 1, env.height)
            assert neighbours[11] == discrete_grid_pos_to_id(2, 0, env.width, 1, env.height)
            assert neighbours[12] == discrete_grid_pos_to_id(0, 1, env.width, 1, env.height)
            # Center
            assert neighbours[13] == discrete_grid_pos_to_id(2, 1, env.width, 1, env.height)
            assert neighbours[14] == discrete_grid_pos_to_id(0, 2, env.width, 1, env.height)
            assert neighbours[15] == discrete_grid_pos_to_id(1, 2, env.width, 1, env.height)
            assert neighbours[16] == discrete_grid_pos_to_id(2, 2, env.width, 1, env.height)

            assert neighbours[17] == discrete_grid_pos_to_id(0, 0, env.width, 2, env.height)
            assert neighbours[18] == discrete_grid_pos_to_id(1, 0, env.width, 2, env.height)
            assert neighbours[19] == discrete_grid_pos_to_id(2, 0, env.width, 2, env.height)
            assert neighbours[20] == discrete_grid_pos_to_id(0, 1, env.width, 2, env.height)
            assert neighbours[21] == discrete_grid_pos_to_id(1, 1, env.width, 2, env.height)
            assert neighbours[22] == discrete_grid_pos_to_id(2, 1, env.width, 2, env.height)
            assert neighbours[23] == discrete_grid_pos_to_id(0, 2, env.width, 2, env.height)
            assert neighbours[24] == discrete_grid_pos_to_id(1, 2, env.width, 2, env.height)
            assert neighbours[25] == discrete_grid_pos_to_id(2, 2, env.width, 2, env.height)

        def test_111_tuple(neighbours):
            assert len(neighbours) == 26
            assert neighbours[0] == (0, 0, 0)
            assert neighbours[1] == (1, 0, 0)
            assert neighbours[2] == (2, 0, 0)
            assert neighbours[3] == (0, 1, 0)
            assert neighbours[4] == (1, 1, 0)
            assert neighbours[5] == (2, 1, 0)
            assert neighbours[6] == (0, 2, 0)
            assert neighbours[7] == (1, 2, 0)
            assert neighbours[8] == (2, 2, 0)

            assert neighbours[9] == (0, 0, 1)
            assert neighbours[10] == (1, 0, 1)
            assert neighbours[11] == (2, 0, 1)
            assert neighbours[12] == (0, 1, 1)
            # Center
            assert neighbours[13] == (2, 1, 1)
            assert neighbours[14] == (0, 2, 1)
            assert neighbours[15] == (1, 2, 1)
            assert neighbours[16] == (2, 2, 1)

            assert neighbours[17] == (0, 0, 2)
            assert neighbours[18] == (1, 0, 2)
            assert neighbours[19] == (2, 0, 2)
            assert neighbours[20] == (0, 1, 2)
            assert neighbours[21] == (1, 1, 2)
            assert neighbours[22] == (2, 1, 2)
            assert neighbours[23] == (0, 2, 2)
            assert neighbours[24] == (1, 2, 2)
            assert neighbours[25] == (2, 2, 2)

        def test_111_with_center(neighbours):
            assert len(neighbours) == 27
            assert neighbours[0] == discrete_grid_pos_to_id(0, 0, env.width, 0, env.height)
            assert neighbours[1] == discrete_grid_pos_to_id(1, 0, env.width, 0, env.height)
            assert neighbours[2] == discrete_grid_pos_to_id(2, 0, env.width, 0, env.height)
            assert neighbours[3] == discrete_grid_pos_to_id(0, 1, env.width, 0, env.height)
            assert neighbours[4] == discrete_grid_pos_to_id(1, 1, env.width, 0, env.height)
            assert neighbours[5] == discrete_grid_pos_to_id(2, 1, env.width, 0, env.height)
            assert neighbours[6] == discrete_grid_pos_to_id(0, 2, env.width, 0, env.height)
            assert neighbours[7] == discrete_grid_pos_to_id(1, 2, env.width, 0, env.height)
            assert neighbours[8] == discrete_grid_pos_to_id(2, 2, env.width, 0, env.height)

            assert neighbours[9] == discrete_grid_pos_to_id(0, 0, env.width, 1, env.height)
            assert neighbours[10] == discrete_grid_pos_to_id(1, 0, env.width, 1, env.height)
            assert neighbours[11] == discrete_grid_pos_to_id(2, 0, env.width, 1, env.height)
            assert neighbours[12] == discrete_grid_pos_to_id(0, 1, env.width, 1, env.height)
            assert neighbours[13] == discrete_grid_pos_to_id(1, 1, env.width, 1, env.height)
            assert neighbours[14] == discrete_grid_pos_to_id(2, 1, env.width, 1, env.height)
            assert neighbours[15] == discrete_grid_pos_to_id(0, 2, env.width, 1, env.height)
            assert neighbours[16] == discrete_grid_pos_to_id(1, 2, env.width, 1, env.height)
            assert neighbours[17] == discrete_grid_pos_to_id(2, 2, env.width, 1, env.height)

            assert neighbours[18] == discrete_grid_pos_to_id(0, 0, env.width, 2, env.height)
            assert neighbours[19] == discrete_grid_pos_to_id(1, 0, env.width, 2, env.height)
            assert neighbours[20] == discrete_grid_pos_to_id(2, 0, env.width, 2, env.height)
            assert neighbours[21] == discrete_grid_pos_to_id(0, 1, env.width, 2, env.height)
            assert neighbours[22] == discrete_grid_pos_to_id(1, 1, env.width, 2, env.height)
            assert neighbours[23] == discrete_grid_pos_to_id(2, 1, env.width, 2, env.height)
            assert neighbours[24] == discrete_grid_pos_to_id(0, 2, env.width, 2, env.height)
            assert neighbours[25] == discrete_grid_pos_to_id(1, 2, env.width, 2, env.height)
            assert neighbours[26] == discrete_grid_pos_to_id(2, 2, env.width, 2, env.height)

        # Test int case
        test_111(env.get_moore_neighbours(discrete_grid_pos_to_id(1, 1, 3, 1, 3)))

        # Test tuple case
        test_111(env.get_moore_neighbours((1, 1, 1)))

        # Test PositionComponent case
        test_111(env.get_moore_neighbours(PositionComponent(None, None, 1, 1, 1)))

        # Test wrong type case
        with pytest.raises(TypeError):
            env.get_moore_neighbours('(1, 1, 1)')

        # With tuples returned
        test_111_tuple(env.get_moore_neighbours((1,1,1), ret_type=tuple))

        # With incompatible return type
        with pytest.raises(TypeError):
            env.get_moore_neighbours((1,1,1), ret_type=str)

        # Test with center
        test_111_with_center(env.get_moore_neighbours((1, 1, 1), incl_center=True))

        # Test no y z dimension
        env = DiscreteWorld(model, 3, 0, 0)
        neighbours = env.get_moore_neighbours(1, ret_type=tuple)
        assert len(neighbours) == 2
        assert neighbours[0] == (0, 0, 0)
        assert neighbours[1] == (2, 0, 0)

        # Test no x dimension
        env = DiscreteWorld(model, 0, 0, 3)
        neighbours = env.get_moore_neighbours(1, ret_type=tuple)
        assert len(neighbours) == 2
        assert neighbours[0] == (0, 0, 0)
        assert neighbours[1] == (0, 0, 2)

        # Test boundary
        env = DiscreteWorld(model, 3, 3, 0)
        neighbours = env.get_moore_neighbours(0, ret_type=tuple)
        assert len(neighbours) == 3
        assert neighbours[0] == (1, 0, 0)
        assert neighbours[1] == (0, 1, 0)
        assert neighbours[2] == (1, 1, 0)

    def test_get_neumann_neighbours(self):
        model = Model()
        env = DiscreteWorld(model, 3, 3, 3)

        def test_111(neighbours):
            assert len(neighbours) == 6
            assert neighbours[0] == discrete_grid_pos_to_id(1, 1, env.width, 0, env.height)
            assert neighbours[1] == discrete_grid_pos_to_id(1, 0, env.width, 1, env.height)
            assert neighbours[2] == discrete_grid_pos_to_id(0, 1, env.width, 1, env.height)
            assert neighbours[3] == discrete_grid_pos_to_id(2, 1, env.width, 1, env.height)
            assert neighbours[4] == discrete_grid_pos_to_id(1, 2, env.width, 1, env.height)
            assert neighbours[5] == discrete_grid_pos_to_id(1, 1, env.width, 2, env.height)

        def test_111_tuple(neighbours):
            assert len(neighbours) == 6
            assert neighbours[0] == (1, 1, 0)
            assert neighbours[1] == (1, 0, 1)
            assert neighbours[2] == (0, 1, 1)
            assert neighbours[3] == (2, 1, 1)
            assert neighbours[4] == (1, 2, 1)
            assert neighbours[5] == (1, 1, 2)

        def test_111_with_center(neighbours):
            assert len(neighbours) == 7
            assert neighbours[0] == discrete_grid_pos_to_id(1, 1, env.width, 0, env.height)
            assert neighbours[1] == discrete_grid_pos_to_id(1, 0, env.width, 1, env.height)
            assert neighbours[2] == discrete_grid_pos_to_id(0, 1, env.width, 1, env.height)
            assert neighbours[3] == discrete_grid_pos_to_id(1, 1, env.width, 1, env.height)
            assert neighbours[4] == discrete_grid_pos_to_id(2, 1, env.width, 1, env.height)
            assert neighbours[5] == discrete_grid_pos_to_id(1, 2, env.width, 1, env.height)
            assert neighbours[6] == discrete_grid_pos_to_id(1, 1, env.width, 2, env.height)

        # Test int case
        test_111(env.get_neumann_neighbours(discrete_grid_pos_to_id(1, 1, 3, 1, 3)))

        # Test tuple case
        test_111(env.get_neumann_neighbours((1, 1, 1)))

        # Test PositionComponent case
        test_111(env.get_neumann_neighbours(PositionComponent(None, None, 1, 1, 1)))

        # Test wrong type case
        with pytest.raises(TypeError):
            env.get_neumann_neighbours('(1, 1, 1)')

        # With tuples returned
        test_111_tuple(env.get_neumann_neighbours((1,1,1), ret_type=tuple))

        # With incompatible return type
        with pytest.raises(TypeError):
            env.get_neumann_neighbours((1,1,1), ret_type=str)

        # Test with center
        test_111_with_center(env.get_neumann_neighbours((1, 1, 1), incl_center=True))

        # Test no y z dimension
        env = DiscreteWorld(model, 3, 0, 0)
        neighbours = env.get_neumann_neighbours(1, ret_type=tuple)
        assert len(neighbours) == 2
        assert neighbours[0] == (0, 0, 0)
        assert neighbours[1] == (2, 0, 0)

        # Test no x dimension
        env = DiscreteWorld(model, 0, 0, 3)
        neighbours = env.get_neumann_neighbours(1, ret_type=tuple)
        assert len(neighbours) == 2
        assert neighbours[0] == (0, 0, 0)
        assert neighbours[1] == (0, 0, 2)

        # Test boundary
        env = DiscreteWorld(model, 3, 3, 0)
        neighbours = env.get_neumann_neighbours(0, ret_type=tuple)
        assert len(neighbours) == 2
        assert neighbours[0] == (1, 0, 0)
        assert neighbours[1] == (0, 1, 0)

        # With r = 2
        env = DiscreteWorld(model, 3, 3, 0)
        neighbours = env.get_neumann_neighbours(0, radius=2, ret_type=tuple)
        assert len(neighbours) == 5
        assert neighbours[0] == (1, 0, 0)
        assert neighbours[1] == (2, 0, 0)
        assert neighbours[2] == (0, 1, 0)
        assert neighbours[3] == (1, 1, 0)
        assert neighbours[4] == (0, 2, 0)

    def test_neighbours(self):
        model = Model()
        env = DiscreteWorld(model, 3, 3, 0)

        # Test Moore
        neighbours = env.get_neighbours(0, ret_type=tuple)
        assert len(neighbours) == 3
        assert neighbours[0] == (1, 0, 0)
        assert neighbours[1] == (0, 1, 0)
        assert neighbours[2] == (1, 1, 0)

        # Test Neumann
        neighbours = env.get_neighbours(0, ret_type=tuple, mode='neumann')
        assert len(neighbours) == 2
        assert neighbours[0] == (1, 0, 0)
        assert neighbours[1] == (0, 1, 0)

        # Test error
        with pytest.raises(KeyError):
            env.get_neighbours(0, mode='fail')


class TestLineWorld:

    def test__init__(self):
        # Test failed initialization
        with pytest.raises(IndexError):
            LineWorld(Model(), -1)

        # Test default init()
        model = Model()
        env = LineWorld(model, 5)
        assert env.width == 5
        assert len(env.cells['pos']) == 5
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        for i in range(len(env.cells['pos'])):
            assert env.cells['pos'][i] == (i, 0, 0)

    def test_get_dimensions(self):
        env = LineWorld(Model(), 5)
        assert env.get_dimensions() == 5


class TestGridWorld:

    def test__init__(self):
        # Test failed initialization
        with pytest.raises(IndexError):
            GridWorld(Model(), 0, 5)

        with pytest.raises(IndexError):
            GridWorld(Model(), 5, 0)

        # Test default init()

        model = Model()
        env = GridWorld(model, 5, 5)
        assert env.width == 5
        assert env.height == 5
        assert len(env.cells['pos']) == 25
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        for x in range(5):
            for y in range(5):
                assert env.cells['pos'][discrete_grid_pos_to_id(x, y, 5)] == (x, y, 0)

    def test_get_dimensions(self):
        env = GridWorld(Model(), 3, 5)
        assert env.get_dimensions() == (3,5)
