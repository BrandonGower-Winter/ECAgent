import pytest

from ECAgent.Decode import *


class TestIDecodable:

    def test_decode(self):

        with pytest.raises(NotImplementedError):
            IDecodable.decode({})
