import pytest

from ECAgent.Core import *
from ECAgent.Environments import *


def test_discreteGridPostoID():
    assert (4 * 3 * 5) + (2 * 3) + 1 == discreteGridPosToID(1, 2, 3, 4, 5)


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

    def test_getPosition(self):
        pos = PositionComponent(None, None, 1, 2, 3)
        assert pos.getPosition() == (1, 2, 3)

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


class TestLineWorld:

    def test__init__(self):
        # Test failed initialization
        with pytest.raises(Exception):
            LineWorld(-1, Model())

        # Test default init()
        model = Model()
        env = LineWorld(5, model)
        assert env.width == 5
        assert len(env.cells['pos']) == 5
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        for i in range(len(env.cells['pos'])):
            assert env.cells['pos'][i] == i

    def test_addAgent(self):
        model = Model()
        model.environment = LineWorld(5, model)
        agent = Agent("a1", model)

        # Test case when agent is added outside of the environment's dimensions [<0]
        with pytest.raises(Exception):
            model.environment.addAgent(agent, -1)

        # Test case when agent is added outside of the environment's dimensions [>width]
        with pytest.raises(Exception):
            model.environment.addAgent(agent, 5)

        # Test default case
        model.environment.addAgent(agent)
        assert len(model.environment.agents) == 1
        assert model.environment.getAgent(agent.id) == agent
        assert agent[PositionComponent].x == 0

        # Test when agent is added twice
        with pytest.raises(Exception):
            model.environment.addAgent(agent)

        # Test case when position is specified
        model.environment.removeAgent(agent.id)

        model.environment.addAgent(agent, xPos=2)
        assert len(model.environment.agents) == 1
        assert model.environment.getAgent(agent.id) == agent
        assert agent[PositionComponent].x == 2

    def test_addCellComponent(self):

        def generator(id: int, df):
            return id

        env = LineWorld(5, Model())

        env.addCellComponent('test_comp', generator)

        assert len(env.cells['test_comp']) == 5

    def test_removeAgent(self):
        model = Model()
        model.environment = LineWorld(5, model)
        agent = Agent("a1", model)
        model.environment.addAgent(agent)
        model.environment.removeAgent(agent.id)
        # Test removal
        assert len(model.environment.agents) == 0
        assert agent[PositionComponent] is None
        # Test removal when agent doesn't exist in the environment
        with pytest.raises(Exception):
            model.environment.removeAgent(agent.id)

    def test_setModel(self):
        model = Model()
        temp = Model()
        env = LineWorld(5, temp)

        assert env.model is temp

        env.setModel(model)
        assert env.model is model

    def test_getAgentsAt(self):
        model = Model()
        model.environment = LineWorld(5, model)
        agent = Agent("a1", model)
        agent2 = Agent("a2", model)

        model.environment.addAgent(agent, 0)
        model.environment.addAgent(agent2, 2)

        # Test empty case
        assert model.environment.getAgentsAt(4) == []

        # Test non empty case
        assert model.environment.getAgentsAt(0) == [agent]

        # Test Leeway case
        assert model.environment.getAgentsAt(0, leeway=2) == [agent, agent2]

    def test_getDimensions(self):
        env = LineWorld(5, Model())

        assert env.getDimensions() == 5

    def test_getCell(self):
        env = LineWorld(5, Model())

        assert env.getCell(-1) is None
        assert env.getCell(5) is None
        assert env.getCell(0) is not None

    def test_getNeighbours(self):
        model = Model()
        lineworld = LineWorld(5, model)

        # Test default case
        neighbours = lineworld.getNeighbours(2)
        assert neighbours[0] == 1
        assert neighbours[1] == 3

        # Test variable range case
        neighbours = lineworld.getNeighbours(2, radius=3)
        assert neighbours[0] == 0
        assert neighbours[1] == 1
        assert neighbours[2] == 3
        assert neighbours[3] == 4

        # Test moore = true
        neighbours = lineworld.getNeighbours(2, moore=True)
        assert neighbours[0] == 1
        assert neighbours[1] == 2
        assert neighbours[2] == 3

    def test_move(self):
        model = Model()
        model.environment = LineWorld(5, model)
        agent = Agent("a1", model)
        agent2 = Agent("a2", model)

        model.environment.addAgent(agent, 0)
        model.environment.addAgent(agent2, 4)

        # Test out of bounds on the left
        model.environment.move(agent, -1)
        assert agent[PositionComponent].x == 0

        # Test valid move to the right
        model.environment.move(agent, 2)
        assert agent[PositionComponent].x == 2

        # Test outs of bounds on the right
        model.environment.move(agent2, 1)
        assert agent2[PositionComponent].x == 4

        # Test valid move to the left
        model.environment.move(agent2, -2)
        assert agent2[PositionComponent].x == 2

        # Test if updates reflect in environment
        assert len(model.environment.getAgentsAt(2)) == 2

        # Test without component
        agent3 = Agent('a3', model)
        with pytest.raises(ComponentNotFoundError):
            model.environment.move(agent3, 1)

    def test_move_to(self):
        model = Model()
        model.environment = LineWorld(5, model)
        agent = Agent("a1", model)

        model.environment.addAgent(agent, 0)

        # Test out of bounds
        with pytest.raises(IndexError):
            model.environment.move_to(agent, -1)

        # Test valid move
        model.environment.move_to(agent, 2)
        assert agent[PositionComponent].x == 2

        # Test without component
        agent2 = Agent('a2', model)
        with pytest.raises(ComponentNotFoundError):
            model.environment.move_to(agent2, 1)


class TestGridWorld:

    def test__init__(self):
        # Test failed initialization
        with pytest.raises(Exception):
            GridWorld(0, 5, Model())

        with pytest.raises(Exception):
            GridWorld(5, 0, Model())

        # Test default init()

        model = Model()
        env = GridWorld(5, 5, model)
        assert env.width == 5
        assert env.height == 5
        assert len(env.cells['pos']) == 25
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        for x in range(5):
            for y in range(5):
                assert env.cells['pos'][discreteGridPosToID(x, y, 5)] == (x, y)

    def test_addAgent(self):
        model = Model()
        model.environment = GridWorld(5, 5, model)
        agent = Agent("a1", model)

        # Test case when agent is added outside of the environment's dimensions [<0]
        with pytest.raises(Exception):
            model.environment.addAgent(agent, xPos=-1, yPos=0)

        with pytest.raises(Exception):
            model.environment.addAgent(agent, xPos=0, yPos=-1)

        # Test case when agent is added outside of the environment's dimensions [>width]
        with pytest.raises(Exception):
            model.environment.addAgent(agent, xPos=5, yPos=0)

        with pytest.raises(Exception):
            model.environment.addAgent(agent, xPos=0, yPos=5)

        # Test default case
        model.environment.addAgent(agent)
        assert len(model.environment.agents) == 1
        assert model.environment.getAgent(agent.id) is agent
        assert agent[PositionComponent].x == 0
        assert agent[PositionComponent].y == 0

        # Test when agent is added twice
        with pytest.raises(Exception):
            model.environment.addAgent(agent)

        # Test case when position is specified
        model.environment.removeAgent(agent.id)

        model.environment.addAgent(agent, xPos=2, yPos=2)
        assert len(model.environment.agents) == 1
        assert model.environment.getAgent(agent.id) is agent
        assert agent[PositionComponent].x == 2
        assert agent[PositionComponent].y == 2

    def test_addCellComponent(self):

        def generator(pos: (int, int), df):
            return discreteGridPosToID(pos[0], pos[1])

        env = GridWorld(5, 5, Model())

        env.addCellComponent('unique_id', generator)

        assert len(env.cells['unique_id']) == 25

    def test_removeAgent(self):
        model = Model()
        model.environment = GridWorld(5, 5, model)
        agent = Agent("a1", model)
        model.environment.addAgent(agent)
        model.environment.removeAgent(agent.id)
        # Test removal
        assert len(model.environment.agents) == 0
        assert agent[PositionComponent] is None
        # Test removal when agent doesn't exist in t
        with pytest.raises(Exception):
            model.environment.removeAgent(agent.id)

    def test_getAgentsAt(self):
        model = Model()
        model.environment = GridWorld(5, 5, model)
        agent = Agent("a1", model)
        agent2 = Agent("a2", model)

        model.environment.addAgent(agent, 0, 0)
        model.environment.addAgent(agent2, 2, 2)

        # Test empty case
        assert model.environment.getAgentsAt(5, 5) == []

        # Test non empty case
        assert model.environment.getAgentsAt(0, 0) == [agent]

        # Test Leeway case
        assert model.environment.getAgentsAt(0, 0, 2, 2) == [agent, agent2]

    def test_setModel(self):
        model = Model()
        temp = Model()
        env = GridWorld(5, 5, temp)

        assert env.model is temp

        env.setModel(model)
        assert env.model is model

    def test_getDimensions(self):
        env = GridWorld(3,5, Model())

        assert env.getDimensions() == (3,5)

    def test_getCell(self):
        env = GridWorld(5, 5, Model())

        assert env.getCell(-1, 0) is None
        assert env.getCell(5, 0) is None
        assert env.getCell(0, -1) is None
        assert env.getCell(0, 5) is None
        assert env.getCell(0, 0) is not None

    def test_getNeighbours(self):
        model = Model()
        gridworld = GridWorld(3, 3, model)

        # Test default case
        neighbours = gridworld.getNeighbours((1, 1))
        assert neighbours[0] == 0
        assert neighbours[1] == 1
        assert neighbours[2] == 2

        assert neighbours[3] == 3
        assert neighbours[4] == 5

        assert neighbours[5] == 6
        assert neighbours[6] == 7
        assert neighbours[7] == 8

        # Test variable range case
        neighbours = gridworld.getNeighbours((1, 1), radius=1)
        assert neighbours[0] == 0
        assert neighbours[1] == 1
        assert neighbours[2] == 2

        assert neighbours[3] == 3
        assert neighbours[4] == 5

        assert neighbours[5] == 6
        assert neighbours[6] == 7
        assert neighbours[7] == 8

        # Test moore = true
        neighbours = gridworld.getNeighbours((1, 1), moore=True)

        assert neighbours[0] == 0
        assert neighbours[1] == 1
        assert neighbours[2] == 2

        assert neighbours[3] == 3
        assert neighbours[4] == 4
        assert neighbours[5] == 5

        assert neighbours[6] == 6
        assert neighbours[7] == 7
        assert neighbours[8] == 8

    def test_move(self):
        model = Model()
        model.environment = GridWorld(5, 5, model)
        agent = Agent("a1", model)
        agent2 = Agent("a2", model)

        model.environment.addAgent(agent, 0, 0)
        model.environment.addAgent(agent2, 4, 4)

        # Test Default case
        model.environment.move(agent)
        assert agent[PositionComponent].x == 0
        assert agent[PositionComponent].y == 0

        # Test out of bounds on the left
        model.environment.move(agent, -1, -1)
        assert agent[PositionComponent].x == 0
        assert agent[PositionComponent].y == 0

        # Test valid move to the right
        model.environment.move(agent, 2, 2)
        assert agent[PositionComponent].x == 2
        assert agent[PositionComponent].y == 2

        # Test outs of bounds on the right
        model.environment.move(agent2, 1, 1)
        assert agent2[PositionComponent].x == 4
        assert agent2[PositionComponent].y == 4

        # Test valid move to the left
        model.environment.move(agent2, -2, -2)
        assert agent2[PositionComponent].x == 2
        assert agent2[PositionComponent].y == 2

        # Test if updates reflect in environment
        assert len(model.environment.getAgentsAt(2,2)) == 2

        # Test without component
        agent3 = Agent('a3', model)
        with pytest.raises(ComponentNotFoundError):
            model.environment.move(agent3)

    def test_move_to(self):
        model = Model()
        model.environment = GridWorld(5, 5, model)
        agent = Agent("a1", model)

        model.environment.addAgent(agent, 0, 0)

        # Test Default case
        model.environment.move_to(agent)
        assert agent[PositionComponent].x == 0
        assert agent[PositionComponent].y == 0

        # Test out of bounds
        with pytest.raises(IndexError):
            model.environment.move_to(agent, -1, -1)

        # Test valid move
        model.environment.move_to(agent, 2, 2)
        assert agent[PositionComponent].x == 2
        assert agent[PositionComponent].y == 2

        # Test without component
        agent2 = Agent('a2', model)
        with pytest.raises(ComponentNotFoundError):
            model.environment.move_to(agent2)


class TestCubeWorld:

    def test__init__(self):
        # Test failed initialization
        with pytest.raises(Exception):
            CubeWorld(0, 5, 5, Model())

        with pytest.raises(Exception):
            CubeWorld(5, 0, 5, Model())

        with pytest.raises(Exception):
            CubeWorld(5, 5, 0, Model())

        # Test default init()
        model = Model()
        env = CubeWorld(5, 5, 5, model)
        assert env.width == 5
        assert env.height == 5
        assert env.depth == 5
        assert len(env.cells['pos']) == 125
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        for i in range(len(env.cells['pos'])):
            pos = env.cells['pos'][i]
            assert discreteGridPosToID(pos[0], pos[1], 5, pos[2], 5) == i

    def test_addAgent(self):
        model = Model()
        model.environment = CubeWorld(5, 5, 5, model)
        agent = Agent("a1", model)

        # Test case when agent is added outside of the environment's dimensions [<0]
        with pytest.raises(Exception):
            model.environment.addAgent(agent, -1, 0, 0)

        with pytest.raises(Exception):
            model.environment.addAgent(agent, 0, -1, 0)

        with pytest.raises(Exception):
            model.environment.addAgent(agent, 0, 0, -1)

        # Test case when agent is added outside of the environment's dimensions [>width]
        with pytest.raises(Exception):
            model.environment.addAgent(agent, 5, 0, 0)

        with pytest.raises(Exception):
            model.environment.addAgent(agent, 0, 5, 0)

        with pytest.raises(Exception):
            model.environment.addAgent(agent, 0, 0, 5)

        # Test default case
        model.environment.addAgent(agent)
        assert len(model.environment.agents) == 1
        assert model.environment.getAgent(agent.id) == agent
        assert agent[PositionComponent].x == 0 and agent[PositionComponent].y == 0 and agent[PositionComponent].z == 0

        # Test when agent is added twice
        with pytest.raises(Exception):
            model.environment.addAgent(agent)

        # Test case when position is specified
        model.environment.removeAgent(agent.id)

        model.environment.addAgent(agent, 1, 2, 3)
        assert len(model.environment.agents) == 1
        assert model.environment.getAgent(agent.id) == agent
        assert agent[PositionComponent].x == 1 and agent[PositionComponent].y == 2 and agent[PositionComponent].z == 3

    def test_addCellComponent(self):

        def generator(pos: (int, int, int), pd):
            return discreteGridPosToID(pos[0], pos[1], 5, pos[2], 5)

        env = CubeWorld(5, 5, 5, Model())

        env.addCellComponent('unique_id', generator)

        assert len(env.cells['unique_id']) == 125

    def test_removeAgent(self):
        model = Model()
        model.environment = CubeWorld(5, 5, 5, model)
        agent = Agent("a1", model)
        model.environment.addAgent(agent)
        model.environment.removeAgent(agent.id)
        # Test removal
        assert len(model.environment.agents) == 0
        assert agent[PositionComponent] is None
        # Test removal when agent doesn't exist in t
        with pytest.raises(Exception):
            model.environment.removeAgent(agent.id)

    def test_setModel(self):
        model = Model()
        temp = Model()
        env = CubeWorld(5, 5, 5, temp)

        assert env.model is temp

        env.setModel(model)
        assert env.model is model

    def test_getAgentsAt(self):
        model = Model()
        model.environment = CubeWorld(5, 5, 5, model)
        agent = Agent("a1", model)
        agent2 = Agent("a2", model)

        model.environment.addAgent(agent, 0, 0, 0)
        model.environment.addAgent(agent2, 2, 2, 2)

        # Test empty case
        assert model.environment.getAgentsAt(5, 5, 5) == []

        # Test non empty case
        assert model.environment.getAgentsAt(0, 0, 0) == [agent]

        # Test Leeway case
        assert model.environment.getAgentsAt(0, 0, 0, 2, 2, 2) == [agent, agent2]

    def test_getDimensions(self):
        env = CubeWorld(1, 2, 3, Model())

        assert env.getDimensions() == (1, 2, 3)

    def test_getCell(self):
        env = CubeWorld(5, 5, 5, Model())

        assert env.getCell(-1, 0, 0) is None
        assert env.getCell(5, 0, 0) is None
        assert env.getCell(0, -1, 0) is None
        assert env.getCell(0, 5, 0) is None
        assert env.getCell(0, 0, -1) is None
        assert env.getCell(0, 0, 5) is None
        assert env.getCell(0, 0, 0) is not None

    def test_getNeighbours(self):
        model = Model()
        cubeworld = CubeWorld(3, 3, 3, model)

        # Test default case
        neighbours = cubeworld.getNeighbours((0, 0, 0))
        assert neighbours[0] == 1
        assert neighbours[1] == discreteGridPosToID(0, 1, cubeworld.width, 0, cubeworld.height)
        assert neighbours[2] == discreteGridPosToID(1, 1, cubeworld.width, 0, cubeworld.height)
        assert neighbours[3] == discreteGridPosToID(0, 0, cubeworld.width, 1, cubeworld.height)
        assert neighbours[4] == discreteGridPosToID(1, 0, cubeworld.width, 1, cubeworld.height)
        assert neighbours[5] == discreteGridPosToID(0, 1, cubeworld.width, 1, cubeworld.height)
        assert neighbours[6] == discreteGridPosToID(1, 1, cubeworld.width, 1, cubeworld.height)

        # Test variable range case
        neighbours = cubeworld.getNeighbours((0, 0, 0), radius=1)
        assert neighbours[0] == 1
        assert neighbours[1] == discreteGridPosToID(0, 1, cubeworld.width, 0, cubeworld.height)
        assert neighbours[2] == discreteGridPosToID(1, 1, cubeworld.width, 0, cubeworld.height)
        assert neighbours[3] == discreteGridPosToID(0, 0, cubeworld.width, 1, cubeworld.height)
        assert neighbours[4] == discreteGridPosToID(1, 0, cubeworld.width, 1, cubeworld.height)
        assert neighbours[5] == discreteGridPosToID(0, 1, cubeworld.width, 1, cubeworld.height)
        assert neighbours[6] == discreteGridPosToID(1, 1, cubeworld.width, 1, cubeworld.height)


        # Test moore = true
        neighbours = cubeworld.getNeighbours((0, 0, 0), moore=True)
        assert neighbours[0] == 0
        assert neighbours[1] == 1
        assert neighbours[2] == discreteGridPosToID(0, 1, cubeworld.width, 0, cubeworld.height)
        assert neighbours[3] == discreteGridPosToID(1, 1, cubeworld.width, 0, cubeworld.height)
        assert neighbours[4] == discreteGridPosToID(0, 0, cubeworld.width, 1, cubeworld.height)
        assert neighbours[5] == discreteGridPosToID(1, 0, cubeworld.width, 1, cubeworld.height)
        assert neighbours[6] == discreteGridPosToID(0, 1, cubeworld.width, 1, cubeworld.height)
        assert neighbours[7] == discreteGridPosToID(1, 1, cubeworld.width, 1, cubeworld.height)

    def test_move(self):
        model = Model()
        model.environment = CubeWorld(5, 5, 5, model)
        agent = Agent("a1", model)
        agent2 = Agent("a2", model)

        model.environment.addAgent(agent, 0, 0, 0)
        model.environment.addAgent(agent2, 4, 4, 4)

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
        assert len(model.environment.getAgentsAt(2,2,2)) == 2

        # Test without component
        agent3 = Agent('a3', model)
        with pytest.raises(ComponentNotFoundError):
            model.environment.move(agent3)

    def test_move_to(self):
        model = Model()
        model.environment = CubeWorld(5, 5, 5, model)
        agent = Agent("a1", model)

        model.environment.addAgent(agent, 0, 0, 0)

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