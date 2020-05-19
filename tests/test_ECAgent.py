import pytest

from ECAgent.Core import *
# Unit testing for src framework


class TestEnvironment:

    def test__init__(self):
        model = Model()
        assert len(model.environment.agents) == 0
        assert model.environment.model == model

    def test_addAgent(self):
        model = Model()
        agent = Agent("a1", model)

        model.environment.addAgent(agent)

        assert len(model.environment.agents) == 1
        assert model.environment.getAgent(agent.id) == agent

        with pytest.raises(Exception):
            model.environment.addAgent(agent)

    def test_removeAgent(self):
        model = Model()
        agent = Agent("a1", model)

        model.environment.addAgent(agent)
        model.environment.removeAgent(agent.id)

        assert len(model.environment.agents) == 0

        with pytest.raises(Exception):
            model.environment.removeAgent(agent.id)

    def test_getAgent(self):
        model = Model()
        agent = Agent("a1", model)

        assert model.environment.getAgent(agent.id) is None

        model.environment.addAgent(agent)
        assert model.environment.getAgent(agent.id) == agent

    def test_getRandomAgent(self):

        env = Environment()

        assert env.getRandomAgent() is None

        model = Model()
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
        model = Model()
        assert model.environment is not None
        assert model.systemManager is not None
        assert model.random is not None

        env = Environment()
        model = Model(environment=env,seed=30)
        assert model.environment == env
        assert model.systemManager is not None
        assert model.random.randint(25, 50) == 42


class TestComponent:

    def test__init__(self):
        model = Model()
        agent = Agent("a1", model)
        component = Component(agent, model)

        assert component.model == model
        assert component.agent == agent


class TestSystem:

    def test__init__(self):
        model = Model()

        system = System("s1",model)
        assert system.model == model
        assert system.id == "s1"
        assert system.start == 0
        assert system.end == maxsize
        assert system.frequency == 1
        assert system.priority == 0


class Test_SystemManager:

    def test__init__(self):
        model = Model()

        sys_man = SystemManager(model)
        assert sys_man.model == model
        assert sys_man.timestep == 0
        assert len(sys_man.systems) == 0
        assert len(sys_man.executionQueue) == 0
        assert len(sys_man.componentPools) == 0

    # TO REST OF THE LOGIC
    def test_executeSystems(self):
        model = Model()
        s1 = System("s1", model)
        model.systemManager.addSystem(s1)
        s1 = System("s2", model)
        model.systemManager.addSystem(s1)

        model.systemManager.executeSystems()
        assert model.systemManager.timestep == 1


    def test_registerComponent(self):
        model = Model()
        s1 = System("s1", model)
        model.systemManager.addSystem(s1)

        assert Component not in model.systemManager.componentPools.keys()

        agent1 = Agent("a1", model)
        component1 = Component(agent1, model)
        agent1.addComponent(component1)

        assert len(model.systemManager.componentPools[Component]) == 1
        assert model.systemManager.componentPools[Component][0] == component1

        agent2 = Agent("a2", model)
        component2 = Component(agent2, model)
        agent2.addComponent(component2)

        assert len(model.systemManager.componentPools[Component]) == 2
        assert model.systemManager.componentPools[Component][0] == component1
        assert model.systemManager.componentPools[Component][1] == component2

        with pytest.raises(Exception):
            model.systemManager.registerComponent(component1)

    def test_deregisterComponent(self):
        model = Model()
        s1 = System("s1", model)
        model.systemManager.addSystem(s1)

        assert Component not in model.systemManager.componentPools.keys()

        agent1 = Agent("a1", model)
        component1 = Component(agent1, model)
        agent1.addComponent(component1)

        agent2 = Agent("a2", model)
        component2 = Component(agent2, model)
        agent2.addComponent(component2)

        # deregister component 2 for basic remove check
        model.systemManager.deregisterComponent(component2)

        assert len(model.systemManager.componentPools[Component]) == 1
        assert component2 not in model.systemManager.componentPools[Component]
        # deregister a component that doesn't exist in the pool
        with pytest.raises(Exception):
            model.systemManager.deregisterComponent(component2)
        # Empty the component pool. This delete the pool
        model.systemManager.deregisterComponent(component1)
        assert Component not in model.systemManager.componentPools.keys()
        # Try delete from a pool that doesn't exist
        with pytest.raises(Exception):
            model.systemManager.deregisterComponent(component1)

    def test_getComponents(self):
        model = Model()
        s1 = System("s1", model)
        model.systemManager.addSystem(s1)

        assert model.systemManager.getComponents(Component) is None

        agent1 = Agent("a1", model)
        component1 = Component(agent1, model)
        agent1.addComponent(component1)

        agent2 = Agent("a2", model)
        component2 = Component(agent2, model)
        agent2.addComponent(component2)

        components = model.systemManager.getComponents(Component)

        assert len(components) == 2
        assert components[0] == component1
        assert components[1] == component2


class TestAgent:

    def test__init__(self):
        model = Model()
        agent = Agent("a1", model)

        assert agent.model == model
        assert agent.id == "a1"
        assert len(agent.components) == 0

    def test_addComponent(self):
        model = Model()
        agent = Agent("a1", model)
        s1 = System("s1", model)
        model.systemManager.addSystem(s1)

        component = Component(agent, model)

        agent.addComponent(component)
        assert len(agent.components) == 1

        with pytest.raises(Exception):
            agent.addComponent(component)

    def test_removeComponent(self):
        model = Model()
        agent = Agent("a1", model)
        s1 = System("s1", model)
        model.systemManager.addSystem(s1)

        component = Component(agent, model)
        agent.addComponent(component)

        agent.removeComponent(component)
        assert len(agent.components) == 0

        with pytest.raises(Exception):
            agent.removeComponent(component)

    def test_getComponent(self):
        model = Model()
        agent = Agent("a1", model)
        s1 = System("s1", model)
        model.systemManager.addSystem(s1)

        # Checks  to see if getting a component that doesn't exist returns None
        assert agent.getComponent(Component) is None

        component = Component(agent, model)
        agent.addComponent(component)
        # Check to see if getting a component that does exist returns the component
        assert agent.getComponent(Component) == component

    def test_hasComponent(self):
        model = Model()
        agent = Agent("a1", model)

        # False check
        assert not agent.hasComponent(Component)

        component = Component(agent, model)
        agent.addComponent(component)
        # True check
        assert agent.hasComponent(Component)
