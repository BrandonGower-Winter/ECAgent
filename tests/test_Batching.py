import pytest

import ECAgent.Batching as batching


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
