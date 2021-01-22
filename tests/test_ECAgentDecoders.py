import pytest

from ECAgent.Core import *
from ECAgent.Decode import *


class TestIDecodable:

    def test_decode(self):

        with pytest.raises(NotImplementedError):
            IDecodable.decode({})


class DummyClass:
    int = 1


class TestDecoder:

    def test_str_to_class(self):
        print(sys.modules)
        assert Decoder.str_to_class('DummyClass', 'test_ECAgentDecoders') is DummyClass
        assert Decoder.str_to_class('NotARealClass', 'test_ECAgentDecoders') is None

    def test__init__(self):
        decoder = Decoder()

        assert decoder.iterations == -1
        assert decoder.epochs == -1
        assert decoder.custom_params == {}

    def test_decode(self):

        with pytest.raises(NotImplementedError):
            decoder = Decoder()
            decoder.decode('filepath')


class DummyModel(Model, IDecodable):

    def __init__(self, seed: int = None):
        super(DummyModel, self).__init__(seed)

    @staticmethod
    def decode(params: dict):
        return DummyModel(params.get('seed'))


class DummySystem(System, IDecodable):

    def __init__(self, id: str, model: Model, priority: int = 0,
                 frequency: int = 1, start=0, end=10000):
        super(DummySystem, self).__init__(id, model, priority, frequency, start, end)

    def execute(self):
        print(self.model.systemManager.timestep)

    @staticmethod
    def decode(params: dict):
        return DummySystem(**params)


class DummyComponent(Component):

    def __init__(self, agent, model, wealth):
        super().__init__(agent, model)

        self.wealth = model.random.randrange(0,10)


class DummyAgent(Agent, IDecodable):

    def __init__(self, id: str, model: Model, wealth):
        super().__init__(id, model)
        self.addComponent(DummyComponent(self, model, wealth))

    @staticmethod
    def decode(params: dict):
        return DummyAgent(params['id_prefix'] + str(params['agent_index']), params['model'],
                         params['components']['DummyComponent']['wealth'])


class TestJsonDecoder:

    def test__init__(self):
        decoder = JsonDecoder()

        assert decoder.iterations == -1
        assert decoder.epochs == -1
        assert decoder.custom_params == {}

    def test_decode(self):
        decoder = JsonDecoder()

        model = decoder.decode('./DummyScripts/Data/PyTestDecoder.json')

        assert decoder.iterations == 10
        assert decoder.epochs == 0
        assert decoder.custom_params == {}

        # Test System
        assert len(model.systemManager.systems) == 1
        assert 'testsys' in model.systemManager.systems
        assert model.systemManager.systems['testsys'].priority == 0
        assert model.systemManager.systems['testsys'].model is model

        # Test Agents
        assert len(model.environment.agents) == 10
        for agent in model.environment.agents:
            assert model.environment.agents[agent].hasComponent(DummyComponent)
            assert model.environment.agents[agent].id.startswith('ta')
            assert model.environment.agents[agent].model is model
