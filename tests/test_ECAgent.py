import pytest
from src.ECAgent.Core import *

# Unit testing for src framework


class TestEnvironment:

    def test__init__(self):
        void_env = Environment()
        assert len(void_env.agents) == 0


class TestModel:

    def test__init__(self):
        env = Environment()
        model = Model(env)

        assert model.timestep == 0
        assert model.environment == env
        assert model.systemManager is not None


class TestComponent:

    def test__init__(self):
        model = Model(Environment())
        component = Component("a1", "s1", model)

        assert component.model == model
        assert component.agentID == "a1"
        assert component.systemID == "s1"


class Test_System:

    def test__init__(self):
        model = Model(Environment())

        system = System("s1",model)
        assert system.model == model
        assert system.id == "s1"
        assert system.start == 0
        assert system.end == maxsize
        assert system.frequency == 1
        assert system.priority == 0


class test_SystemManager:

    def test__init__(self):
        model = Model(Environment())

        sys_man = SystemManager(model)
        assert sys_man.model == model
        assert len(sys_man.systems) == 0
        assert len(sys_man.executionQueue) == 0
        assert len(sys_man.componentPools) == 0

    # TO DO rest of functions

class TestAgent:

    def test__init__(self):
        model = Model(Environment())
        agent = Agent("a1", model)

        assert agent.model == model
        assert agent.id == "a1"
        assert len(agent.components) == 0

    def test_addComponent(self):
        model = Model(Environment())
        agent = Agent("a1", model)
        s1 = System("s1", model)
        model.systemManager.addSystem(s1)

        component = Component(agent.id,s1.id,model)

        agent.addComponent(component)
        assert len(agent.components) == 1

        with pytest.raises(Exception):
            agent.addComponent(component)

    def test_removeComponent(self):
        model = Model(Environment())
        agent = Agent("a1", model)
        s1 = System("s1", model)
        model.systemManager.addSystem(s1)

        component = Component(agent.id, "s1", model)
        agent.addComponent(component)

        agent.removeComponent(component)
        assert len(agent.components) == 0

        with pytest.raises(Exception):
            agent.removeComponent(component)
