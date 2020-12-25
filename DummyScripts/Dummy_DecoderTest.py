from ECAgent.Core import Model, System
from ECAgent.Decode import IDecodable,JsonDecoder


class TestModel(Model, IDecodable):

    def __init__(self, seed: int = None):
        super(TestModel, self).__init__(seed)
        print(seed)

    @staticmethod
    def decode(params: dict):
        return TestModel(params.get('seed'))


class TestSystem(System, IDecodable):

    def __init__(self, id: str, model: Model, priority: int = 0,
                 frequency: int = 1, start=0, end=10000):
        super(TestSystem, self).__init__(id, model, priority, frequency, start, end)

    def execute(self):
        print(model.systemManager.timestep)

    @staticmethod
    def decode(params: dict):
        return TestSystem(**params)


if __name__ == '__main__':
    decoder = JsonDecoder()
    model = decoder.decode('Data/TestDecode.json')

    print('Iter.', decoder.iterations)
    print('Epochs', decoder.epochs)
    print('Custom_params', decoder.custom_params)

    print('TestSystem id:', model.systemManager.systems['testsys'].id)
    print('TestSystem priority:', model.systemManager.systems['testsys'].priority)

    for x in range(0, decoder.iterations):
        model.systemManager.executeSystems()
