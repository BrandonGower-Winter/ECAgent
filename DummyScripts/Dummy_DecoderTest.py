from ECAgent.Core import Model
from ECAgent.Decode import IDecodable,JsonDecoder


class TestModel(Model, IDecodable):

    def __init__(self, seed: int = None):
        super(TestModel, self).__init__(seed)
        print(seed)

    @staticmethod
    def decode(params: dict):
        return TestModel(params.get('seed'))


if __name__ == '__main__':
    decoder = JsonDecoder()
    model = decoder.decode('Data/TestDecode.json')

    print('Iter.', decoder.iterations)
    print('Epochs', decoder.epochs)
    print('Custom_params', decoder.custom_params)
