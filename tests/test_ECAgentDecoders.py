import pytest

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
