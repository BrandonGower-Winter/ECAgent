import pytest

from ECAgent.Core import *
from ECAgent.Environments import *


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


class TestLineWorld:

    def test__init__(self):
        # Test failed initialization
        with pytest.raises(Exception):
            LineWorld(-1, Model())

        # Test default init()
        model = Model()
        env = LineWorld(5, model)
        assert env.width == 5
        assert len(env.cells) == 5
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        for i in range(len(env.cells)):
            assert env.cells[i].model is model
            assert env.cells[i].id == 'CELL_' + str(i)
            assert env.cells[i].hasComponent(PositionComponent) and env.cells[i][PositionComponent].x == i

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

        def generator(cell: Agent):
            cell.addComponent(Component(cell, cell.model))

        env = LineWorld(5, Model())

        env.addCellComponent(generator)

        for cell in env.cells:
            assert cell.hasComponent(Component)

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
        # Test for all cells:
        for x in range(5):
            assert env.cells[x].model is temp

        env.setModel(model)
        assert env.model is model

        # Test for all model for all cells
        for x in range(5):
            assert env.cells[x].model is model
            assert env.cells[x].hasComponent(PositionComponent) and env.cells[x][PositionComponent].x == x

    def test_getAgentsAt(self):
        model = Model()
        model.environment = LineWorld(5, model)
        agent = Agent("a1", model)

        model.environment.addAgent(agent, 0)

        # Test empty case
        assert model.environment.getAgentsAt(4) == []

        # Test non empty case
        assert model.environment.getAgentsAt(0) == [agent]

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
        neighbours = lineworld.getNeighbours(lineworld.getCell(2))
        print([cell[PositionComponent].x for cell in neighbours])
        assert neighbours[0] is lineworld.cells[1]
        assert neighbours[1] is lineworld.cells[3]

        # Test variable range case
        neighbours = lineworld.getNeighbours(lineworld.getCell(2), radius=3)
        assert neighbours[0] is lineworld.cells[0]
        assert neighbours[1] is lineworld.cells[1]
        assert neighbours[2] is lineworld.cells[3]
        assert neighbours[3] is lineworld.cells[4]

        # Test moore = true
        neighbours = lineworld.getNeighbours(lineworld.getCell(2), moore=True)
        assert neighbours[0] is lineworld.cells[1]
        assert neighbours[1] is lineworld.cells[2]
        assert neighbours[2] is lineworld.cells[3]


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
        assert len(env.cells) == 25
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        for i in range(len(env.cells)):
            assert env.cells[i].model is model
            assert env.cells[i].id == 'CELL_' + str(i)
            assert env.cells[i].hasComponent(PositionComponent)


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
        assert model.environment[agent.id] is agent
        assert agent[PositionComponent].x == 0
        assert agent[PositionComponent].y == 0

        # Test when agent is added twice
        with pytest.raises(Exception):
            model.environment.addAgent(agent)

        # Test case when position is specified
        model.environment.removeAgent(agent.id)

        model.environment.addAgent(agent, xPos=2, yPos=2)
        assert len(model.environment.agents) == 1
        assert model.environment[agent.id] is agent
        assert agent[PositionComponent].x == 2
        assert agent[PositionComponent].y == 2

    def test_addCellComponent(self):

        def generator(cell: Agent):
            cell.addComponent(Component(cell, cell.model))

        env = GridWorld(5, 5, Model())

        env.addCellComponent(generator)

        for cell in env.cells:
            assert cell.hasComponent(Component)

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

        model.environment.addAgent(agent, 0, 0)

        # Test empty case
        assert model.environment.getAgentsAt(5,5) == []

        # Test non empty case
        assert model.environment.getAgentsAt(0,0) == [agent]

    def test_setModel(self):
        model = Model()
        temp = Model()
        env = GridWorld(5, 5, temp)

        assert env.model is temp
        # Test for all cells:
        for x in range(25):
            assert env.cells[x].model is temp

        env.setModel(model)
        assert env.model is model

        # Test for all model for all cells
        for x in range(25):
            assert env.cells[x].model is model
            xPos = x % 5
            yPos = x // 5
            assert env.cells[x][PositionComponent].x == xPos and env.cells[x][PositionComponent].y == yPos

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
        assert len(env.cells) == 125
        assert env.id == 'ENVIRONMENT'
        assert env.model is model
        assert len(env.agents) == 0

        for i in range(len(env.cells)):
            assert env.cells[i].model is model
            assert env.cells[i].id == 'CELL_' + str(i)
            assert env.cells[i].hasComponent(PositionComponent)

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

        def generator(cell: Agent):
            cell.addComponent(Component(cell, cell.model))

        env = CubeWorld(5, 5, 5, Model())

        env.addCellComponent(generator)

        for cell in env.cells:
            assert cell.hasComponent(Component)

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
        # Test for all cells:
        for x in range(125):
            assert env.cells[x].model is temp

        env.setModel(model)
        assert env.model is model

        # Test for all model for all cells
        for x in range(125):
            assert env.cells[x].model is model
            assert env.cells[x].hasComponent(PositionComponent)

    def test_getAgentsAt(self):
        model = Model()
        model.environment = CubeWorld(5, 5, 5, model)
        agent = Agent("a1", model)

        model.environment.addAgent(agent, 0, 0, 0)

        # Test empty case
        assert model.environment.getAgentsAt(5, 5, 5) == []

        # Test non empty case
        assert model.environment.getAgentsAt(0, 0, 0) == [agent]

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