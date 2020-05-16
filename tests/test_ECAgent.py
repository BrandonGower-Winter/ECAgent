import pytest
from src.ECAgent.Core import *

# Unit testing for src framework


class TestEnvironment:

    def test__init__(self):
        void_env = Environment()
        assert len(void_env.agents) == 0

    def test_addAgent(self):
        model = Model(Environment())
        agent = Agent("a1", model)

        model.environment.addAgent(agent)

        assert len(model.environment.agents) == 1
        assert model.environment.getAgent(agent.id) == agent

        with pytest.raises(Exception):
            model.environment.addAgent(agent)

    def test_removeAgent(self):
        model = Model(Environment())
        agent = Agent("a1", model)

        model.environment.addAgent(agent)
        model.environment.removeAgent(agent.id)

        assert len(model.environment.agents) == 0

        with pytest.raises(Exception):
            model.environment.removeAgent(agent.id)

    def test_getAgent(self):
        model = Model(Environment())
        agent = Agent("a1", model)

        assert model.environment.getAgent(agent.id) is None

        model.environment.addAgent(agent)
        assert model.environment.getAgent(agent.id) == agent

    def test_getRandomAgent(self):
        model = Model(Environment())
        agent1 = Agent("a1", model)
        agent2 = Agent("a2", model)

        assert model.environment.getRandomAgent() is None

        model.environment.addAgent(agent1)

        assert model.environment.getRandomAgent() == agent1

        model.environment.addAgent(agent2)

        random_agent = model.environment.getRandomAgent()
        assert random_agent == agent1 or random_agent == agent2


class TestModel:

    def test__init__(self):
        env = Environment()
        model = Model(env)
        assert model.environment == env
        assert model.systemManager is not None


class TestComponent:

    def test__init__(self):
        model = Model(Environment())
        component = Component("a1", "s1", model)

        assert component.model == model
        assert component.agentID == "a1"
        assert component.systemID == "s1"


class TestSystem:

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
        assert sys_man.timestep == 0
        assert len(sys_man.systems) == 0
        assert len(sys_man.executionQueue) == 0
        assert len(sys_man.componentPools) == 0

    # TO DO rest of functions

    def test_getComponents(self):
        model = Model(Environment())
        s1 = System("s1", model)
        model.systemManager.addSystem(s1)

        assert model.systemManager.getComponents("s1") is None

        agent1 = Agent("a1", model)
        component1 = Component(agent1.id, s1.id, model)
        agent1.addComponent(component1)

        agent2 = Agent("a2", model)
        component2 = Component(agent2.id, s1.id, model)
        agent2.addComponent(component2)

        components = model.systemManager.getComponents("s1")

        assert len(components) == 2
        assert components[0] == component1
        assert components[1] == component2


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

    def test_getComponent(self):
        model = Model(Environment())
        agent = Agent("a1", model)
        s1 = System("s1", model)
        model.systemManager.addSystem(s1)

        # Checks  to see if getting a component that doesn't exist returns None
        assert agent.getComponent(Component) is None

        component = Component(agent.id, "s1", model)
        agent.addComponent(component)
        # Check to see if getting a component that does exist returns the component
        assert agent.getComponent(Component) == component
