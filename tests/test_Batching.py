import pytest

import ECAgent.Core as core
import ECAgent.Batching as batching
import ECAgent.Collectors as collectors

class TestParameterList:

    def test__init__(self):

        # Default case
        p_list = batching.ParameterList()
        assert len(p_list._parameters) == 0

        # Raise Attribute Error Case
        with pytest.raises(AttributeError):
            p_list = batching.ParameterList({32: "invalid key"})

        # Case with valid dictionary:
        p_list = batching.ParameterList({"value": 44, "list": (1, 2, 3, 4)})
        assert len(p_list._parameters) == 2
        assert p_list._parameters["value"] == 44
        assert p_list._parameters["list"] == (1, 2, 3, 4)

    def test_add_parameter(self):

        p_list = batching.ParameterList()

        # Error case
        with pytest.raises(AttributeError):
            p_list.add_parameter(32,  "invalid key")

        # Valid cases with both single value and iterable
        p_list.add_parameter("value", 44)
        p_list.add_parameter("list", (1, 2, 3, 4))
        assert len(p_list._parameters) == 2
        assert p_list._parameters["value"] == 44
        assert p_list._parameters["list"] == (1, 2, 3, 4)

        # Error case with duplicate key
        with pytest.raises(KeyError):
            p_list.add_parameter("value", 44)

    def test_remove_parameter(self):

        p_list = batching.ParameterList({"value": 44})

        # Valid Case
        p_list.remove_parameter("value")

        assert len(p_list._parameters) == 0

        # Error Case
        with pytest.raises(KeyError):
            p_list.remove_parameter("value")

    def test_build(self):
        p_list = batching.ParameterList({"value": 44, "string": "xyz"})

        # Test basic case:
        p_set = p_list.build()
        assert len(p_set) == 1
        assert p_set[0]["value"] == 44
        assert p_set[0]["string"] == "xyz"

        # Test with multiple values
        p_list.add_parameter("list", (0, 1, 2, 3, 4))
        p_set = p_list.build()
        assert len(p_set) == 5

        for i in range(5):
            assert p_set[i]["value"] == 44
            assert p_set[i]["string"] == "xyz"
            assert p_set[i]["list"] == i


class CustomSystem(core.System):
    def execute(self):
        if self.model.systems.timestep == self.model.timesteps:  # Hacky solution which assumes CustomModel is used.
            self.model.complete()


class CustomCollector(collectors.Collector):
    def collect(self):
        self.records.append(1)


class CustomModel(core.Model):
    def __init__(self, num_agents: int = 0, timesteps: int = 10, collect: int = 0):
        super().__init__()
        self.num_agents = num_agents
        self.timesteps = timesteps
        self.systems.add_system(CustomSystem("custom_system", self))
        for i in range(collect):
            self.systems.add_system(CustomCollector(f'c{i}', self))


def test_build_model_from_kwargs():
    model = batching._build_model_from_kwargs(CustomModel, {'num_agents': 5, 'timesteps': 5})
    assert model.num_agents == 5
    assert model.timesteps == 5


def test_run_model():
    params = {'num_agents': 5, 'timesteps': 20, 'collect': 0}
    # Default Case with max timesteps
    assert batching._run_model(CustomModel, params, max_timesteps=10) is None

    # 1 Collector case
    params = {'num_agents': 5, 'timesteps': 20, 'collect': 1}
    assert len(batching._run_model(CustomModel, params, collectors='c0', max_timesteps=10)) == 10

    # Collector with early stop
    params = {'num_agents': 5, 'timesteps': 5, 'collect': 1}
    assert len(batching._run_model(CustomModel, params, collectors='c0', max_timesteps=10)) == 5

    # 2 Collectors case
    params = {'num_agents': 5, 'timesteps': 20, 'collect': 2}
    data = batching._run_model(CustomModel, params, collectors=['c0', 'c1'], max_timesteps=10)
    assert len(data) == 2
    assert len(data['c0']) == 10
    assert len(data['c1']) == 10


def test_batch_run():
    params = {'num_agents': 5, 'timesteps': 20, 'collect': 0}

    # Raise error
    with pytest.raises(AttributeError):
        batching.batch_run(CustomModel, params, collectors=34, max_timesteps=10)

    # Dict with no collection and 1 process
    assert len(batching.batch_run(CustomModel, params, None, max_timesteps=10)) == 0

    # Dict with 1 collector and 1 process
    params = {'num_agents': 5, 'timesteps': [10, 20], 'collect': 1}
    data = batching.batch_run(CustomModel, params, 'c0', max_timesteps=10)
    assert len(data) == 2
    assert len(data[0]) == 10
    assert len(data[1]) == 10

    # Dict with 2 collectors and 2 processes
    params = {'num_agents': [5, 10, 20], 'timesteps': [10, 20], 'collect': 2}
    data = batching.batch_run(CustomModel, params, ['c0', 'c1'], processes=2, max_timesteps=10)
    assert len(data) == 6
    for i in range(6):
        assert len(data[i]) == 2
        assert len(data[i]['c0']) == 10
        assert len(data[i]['c1']) == 10

    # Dict with 2 collectors, 2 repetitions and 2 processes
    params = {'num_agents': [5, 10, 20], 'timesteps': [10, 20], 'collect': 2}
    data = batching.batch_run(CustomModel, params, ['c0', 'c1'], processes=2, max_timesteps=10, repetitions=2)
    assert len(data) == 12
    for i in range(12):
        assert len(data[i]) == 2
        assert len(data[i]['c0']) == 10
        assert len(data[i]['c1']) == 10
