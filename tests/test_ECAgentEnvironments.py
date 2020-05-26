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


class TestLineWorld:

    def test__init__(self):
        # Test failed initialization
        with pytest.raises(Exception):
            LineWorld(-1)

        # Test default init()

        env = LineWorld(5)
        assert env.width == 5
        assert len(env.cells) == 5
        assert env.id == 'ENVIRONMENT'
        assert env.model is None
        assert len(env.agents) == 0

        for i in range(len(env.cells)):
            assert env.cells[i].model is None
            assert env.cells[i].id

    def test_addAgent(self):
        model = Model(LineWorld(5))
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

        model.environment.addAgent(agent, 2)
        assert len(model.environment.agents) == 1
        assert model.environment.getAgent(agent.id) == agent
        assert agent[PositionComponent].x == 2

    def test_removeAgent(self):
        model = Model(LineWorld(5))
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
        env = LineWorld(5)

        assert env.model is not model
        # Test for all cells:
        for x in range(5):
            assert env.cells[x].model is None

        env.setModel(model)
        assert env.model is model

        # Test for all model for all cells
        for x in range(5):
            assert env.cells[x].model is model

    def test_getAgentsAt(self):
        model = Model(LineWorld(5))
        agent = Agent("a1", model)

        model.environment.addAgent(agent, 0)

        # Test empty case
        assert model.environment.getAgentsAt(4) == []

        # Test non empty case
        assert model.environment.getAgentsAt(0) == [agent]
