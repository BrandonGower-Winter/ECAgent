from timeit import default_timer as timer

from ECAgent.Environments import *


class TestModel(Model):

    def __init__(self):
        super().__init__()
        self.environment = GridWorld(400, 400, self)


if __name__ == '__main__':
    start = timer()
    model = TestModel()

    print(timer() - start)
