import logging
import pytest

from ECAgent.Core import *
# Unit testing for src framework

class TestEnvironment:

    def test__init__(self):
        model = Model()
        assert len(model.environment.components) == 0
        assert len(model.environment.agents) == 0
        assert model.environment.model is model
        assert model.environment.id == "ENVIRONMENT"

    def test_add_agent(self):
        model = Model()
        agent = Agent("a1", model)

        model.environment.add_agent(agent)

        assert len(model.environment.agents) == 1
        assert model.environment.get_agent(agent.id) == agent

        with pytest.raises(DuplicateAgentError):
            model.environment.add_agent(agent)

    def test_remove_agent(self):
        model = Model()
        agent = Agent("a1", model)

        model.environment.add_agent(agent)
        model.environment.remove_agent(agent.id)

        assert len(model.environment.agents) == 0

        with pytest.raises(AgentNotFoundError):
            model.environment.remove_agent(agent.id)

    def test_get_agent(self):
        model = Model()
        agent = Agent("a1", model)

        # Not found with no error
        assert model.environment.get_agent(agent.id) is None

        # Not found with error
        with pytest.raises(AgentNotFoundError):
            model.environment.get_agent(agent.id, True)

        # Found
        model.environment.add_agent(agent)
        assert model.environment.get_agent(agent.id) == agent

    def test_get_random_agent(self):

        env = Environment(None)

        assert env.get_random_agent() is None

        model = Model()
        agent1 = Agent("a1", model)
        agent2 = Agent("a2", model)

        assert model.environment.get_random_agent() is None

        model.environment.add_agent(agent1)

        assert model.environment.get_random_agent() is agent1

        model.environment.add_agent(agent2)

        random_agent = model.environment.get_random_agent()
        assert random_agent is agent1 or random_agent is agent2

        # Test Component filter
        class CustomComponent(Component):

            def __init__(self, a, m):
                super().__init__(a, m)

        # Test for case in which no agents meet filter requirements

        assert model.environment.get_random_agent(CustomComponent) is None

        # Test case where agent does meet requirement
        agent1.add_component(CustomComponent(agent1, model))
        assert model.environment.get_random_agent(CustomComponent) is agent1

        # Test case with Tag
        agent1.tag = 1
        assert model.environment.get_random_agent(tag=1) is agent1

    def test_get_agents(self):
        model = Model()

        # Test empty list is returned when non agents occupy the environment
        assert model.environment.get_agents() == []

        # Test list when no filter is supplied but agents do occupy the environment

        agent1 = Agent("a1", model)
        agent2 = Agent("a2", model)

        model.environment.add_agent(agent1)
        model.environment.add_agent(agent2)

        assert model.environment.get_agents() == [agent1, agent2]

        # Test component filter when no agents meet the filter
        assert model.environment.get_agents(Component) == []

        # Test component filter when some agents meet the filter
        agent1.add_component(Component(agent1, model))
        assert model.environment.get_agents(Component) == [agent1]

        # Test tag filter
        agent1.tag = 1
        assert model.environment.get_agents(tag=1) == [agent1]

    def test_set_model(self):
        model = Model()

        env = Environment(None)
        assert env.model is None

        env.set_model(model)
        assert env.model is model

    def test__len__(self):
        env = Environment(None)

        # Test Empty case
        assert len(env) == 0

        # Test once agent has been added
        env.add_agent(Agent("a1", None))
        assert len(env) == 1

    def test__iter__(self):
        env = Environment(None)

        # Test Empty case
        i = 0
        for _ in env:
            i+=1

        assert i == 0

        # Test once agent has been added
        env.add_agent(Agent("a1", None))
        i = 0
        for _ in env:
            i+=1

        assert i == 1

    def test_shuffle(self):

        model = Model()

        a1 = Agent("a1", model)
        a1.add_component(Component(self, model))
        model.environment.add_agent(a1)
        model.environment.add_agent(Agent("a2", model))

        # Test with no template
        assert len(model.environment.shuffle()) == 2

        # Test with template
        assert len(model.environment.shuffle(Component)) == 1


class TestModel:

    def test__init__(self):
        model = Model()
        assert model.environment is not None
        assert model.systems is not None
        assert model.random is not None
        assert model.logger is not None
        assert model.logger.level == logging.INFO

        logger = logging.getLogger('TEST')
        logger.setLevel(logging.DEBUG)

        model = Model(seed=30, logger=logger)
        assert model.environment is not None
        assert model.systems is not None
        assert model.random.randint(25, 50) == 42
        assert model.logger is logger
        assert model.logger.level == logging.DEBUG

    def test__getattr__(self):
        model = Model()

        # Test Error Case
        with pytest.raises(AttributeError):
            model.not_an_attribute

        # Test timestep
        model.execute()
        assert model.timestep == model.systems.timestep

    def test_set_environment(self):
        model = Model()
        new_env = Environment(model)

        model.set_environment(new_env)
        assert model.environment is new_env

    def test_execute(self):
        model = Model()

        # Type Error
        with pytest.raises(TypeError):
            model.execute('2')

        # Value Error
        with pytest.raises(ValueError):
            model.execute(-1)

        # Valid single step
        model.execute()
        assert model.systems.timestep == 1

        # Valid multistep
        model.execute(2)
        assert model.systems.timestep == 3


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

    def test_clean_up(self):
        model = Model()
        s1 = System("s1", model)
        model.systems.add_system(s1)

        s1.clean_up()
        assert s1.id not in model.systems.systems

    def test_execute(self):
        s1 = System("s1",None)

        with pytest.raises(NotImplementedError):
            s1.execute()


class TestSystemManager:

    def test__init__(self):
        model = Model()

        sys_man = SystemManager(model)
        assert sys_man.model == model
        assert sys_man.timestep == 0
        assert len(sys_man.systems) == 0
        assert len(sys_man.executionQueue) == 0
        assert len(sys_man.componentPools) == 0

    def test_add_system(self):
        model = Model()
        s1 = System("s1", model)

        # Test adding to the end of the queue.
        model.systems.add_system(s1)
        assert len(model.systems.executionQueue) == 1

        # Test adding duplicate system.
        with pytest.raises(KeyError):
            model.systems.add_system(s1)

        # Test adding to the beginning of the queue
        s2 = System("s2", model, priority=10)
        model.systems.add_system(s2)
        assert len(model.systems.executionQueue) == 2
        assert model.systems.executionQueue[0].id == s2.id

    def test_remove_system(self):
        model = Model()
        s1 = System("s1", model)

        # Test Error
        with pytest.raises(SystemNotFoundError):
            model.systems.remove_system(s1.id)

        model.systems.add_system(s1)
        model.systems.remove_system(s1.id)
        assert s1.id not in model.systems.systems

    def test_execute_systems(self):

        class TestSystem(System):

            def __init__(self, id: str, model: Model, priority, freq, start, end):
                super().__init__(id, model, priority, freq, start, end)
                self.counter = 0

            def execute(self):
                self.counter += 1

        model = Model()
        s1 = TestSystem("s1", model, 0, 1, 0, 10)
        model.systems.add_system(s1)
        s2 = TestSystem("s2", model, 0, 3, 4, 10000)
        model.systems.add_system(s2)

        for _ in range(12):
            model.systems.execute_systems()

        assert model.systems.timestep == 12
        assert s1.counter == 11
        assert s2.counter == 3

    def test_register_component(self):
        model = Model()
        s1 = System("s1", model)
        model.systems.add_system(s1)

        assert Component not in model.systems.componentPools.keys()

        agent1 = Agent("a1", model)
        component1 = Component(agent1, model)
        agent1.add_component(component1)

        model.environment.add_agent(agent1)

        assert len(model.systems.componentPools[Component]) == 1
        assert model.systems.componentPools[Component][0] == component1

        agent2 = Agent("a2", model)
        component2 = Component(agent2, model)
        agent2.add_component(component2)

        model.environment.add_agent(agent2)

        assert len(model.systems.componentPools[Component]) == 2
        assert model.systems.componentPools[Component][0] == component1
        assert model.systems.componentPools[Component][1] == component2

        with pytest.raises(KeyError):
            model.systems.register_component(component1)

    def test_deregister_component(self):
        model = Model()
        s1 = System("s1", model)
        model.systems.add_system(s1)

        assert Component not in model.systems.componentPools.keys()

        agent1 = Agent("a1", model)
        component1 = Component(agent1, model)
        agent1.add_component(component1)
        model.environment.add_agent(agent1)

        agent2 = Agent("a2", model)
        component2 = Component(agent2, model)
        agent2.add_component(component2)
        model.environment.add_agent(agent2)

        # deregister component 2 for basic remove check
        model.systems.deregister_component(component2)

        assert len(model.systems.componentPools[Component]) == 1
        assert component2 not in model.systems.componentPools[Component]
        # deregister a component that doesn't exist in the pool
        with pytest.raises(KeyError):
            model.systems.deregister_component(component2)
        # Empty the component pool. This deletes the pool
        model.systems.deregister_component(component1)
        assert Component not in model.systems.componentPools.keys()
        # Try delete from a pool that doesn't exist
        with pytest.raises(KeyError):
            model.systems.deregister_component(component1)

    def test_get_components(self):
        model = Model()
        s1 = System("s1", model)
        model.systems.add_system(s1)

        assert model.systems.getComponents(Component) is None

        agent1 = Agent("a1", model)
        component1 = Component(agent1, model)
        agent1.add_component(component1)

        agent2 = Agent("a2", model)
        component2 = Component(agent2, model)
        agent2.add_component(component2)

        model.environment.add_agent(agent1)
        model.environment.add_agent(agent2)

        components = model.systems.getComponents(Component)

        assert len(components) == 2
        assert components[0] == component1
        assert components[1] == component2


class TestAgent:

    def test__init__(self):
        model = Model()

        # Without tag
        agent = Agent("a1", model)

        assert agent.model == model
        assert agent.id == "a1"
        assert len(agent.components) == 0
        assert agent.tag == 0

        # With tag
        agent = Agent("a2", model, tag=1)

        assert agent.model == model
        assert agent.id == "a2"
        assert len(agent.components) == 0
        assert agent.tag == 1

    def test_add_component(self):
        model = Model()
        agent = Agent("a1", model)
        s1 = System("s1", model)
        model.systems.add_system(s1)

        component = Component(agent, model)

        agent.add_component(component)
        assert len(agent.components) == 1

        with pytest.raises(ValueError):
            agent.add_component(component)

    def test_remove_component(self):
        model = Model()
        agent = Agent("a1", model)
        s1 = System("s1", model)
        model.systems.add_system(s1)

        component = Component(agent, model)
        agent.add_component(component)

        agent.remove_component(Component)
        assert len(agent.components) == 0

        with pytest.raises(ComponentNotFoundError):
            agent.remove_component(Component)

    def test_get_component(self):
        model = Model()
        agent = Agent("a1", model)

        # Checks  to see if getting a component that doesn't exist returns None
        assert agent.get_component(Component) is None

        # Checks the same argument but it should throw an error instead.
        with pytest.raises(ComponentNotFoundError):
            agent.get_component(Component, True)

        component = Component(agent, model)
        agent.add_component(component)
        # Check to see if getting a component that does exist returns the component
        assert agent.get_component(Component) is component

    def test__getitem__(self):
        model = Model()
        agent = Agent("a1", model)

        # Checks  to see if getting a component that doesn't exist returns None
        assert agent[Component] is None

        component = Component(agent, model)
        agent.add_component(component)
        # Check to see if getting a component that does exist returns the component
        assert agent[Component] is component

    def test__len__(self):
        model = Model()
        agent = Agent("a1", model)

        # Test empty case
        assert len(agent) == 0

        # Test case when component is added
        agent.add_component(Component(agent, model))
        assert len(agent) == 1

    def test_has_component(self):
        model = Model()
        agent = Agent("a1", model)

        # False check
        assert not agent.has_component(Component)

        component = Component(agent, model)
        agent.add_component(component)
        # True check
        assert agent.has_component(Component)

        # Check for multiple components

        class CustomComponent(Component):

            def __init__(self, a, m):
                super().__init__(a, m)

        # Test on multiple components (with one or missing)
        assert not agent.has_component(Component, TestComponent)

        # Test should pass on multiple components
        agent.add_component(CustomComponent(agent,model))

        assert agent.has_component(Component, CustomComponent)

    def test__contains__(self):
        model = Model()
        agent = Agent("a1", model)

        # False check
        assert Component not in agent

        component = Component(agent, model)
        agent.add_component(component)
        # True check
        assert Component in agent


class TestAgentNotFoundError:

    def test__init__(self):
        model = Model()

        error = AgentNotFoundError('a', model.environment)

        assert error.a_id == 'a'
        assert error.environment == model.environment
        assert error.message == 'Agent "a" could not be found in Environment "ENVIRONMENT"'


class TestDuplicateAgentError:

    def test__init__(self):
        model = Model()

        error = DuplicateAgentError('a', model.environment)

        assert error.a_id == 'a'
        assert error.environment == model.environment
        assert error.message == 'Agent "a" already exists in Environment "ENVIRONMENT"'


class TestComponentNotFoundError:

    def test__init__(self):
        model = Model()
        agent = Agent('a', model)

        error = ComponentNotFoundError(agent, Component)

        assert error.agent is agent
        assert error.component_type == Component
        assert error.message == 'Agent a does not have a component of type <class \'ECAgent.Core.Component\'>.'


class TestSystemNotFoundError:

    def test__init__(self):

        error = SystemNotFoundError('s1')

        assert error.s_id == 's1'
        assert error.message == 'System with id "s1" does not exist.'
