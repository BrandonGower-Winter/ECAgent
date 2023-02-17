import pytest

import ECAgent.Tags as Tags

class TestTagLibrary:

    def test__init__(self):
        tl = Tags.TagLibrary()

        assert tl.NONE == 0
        assert tl._tag_counter == 1
        assert len(tl._tag_names) == 1

    def test__len__(self):
        tl = Tags.TagLibrary()

        assert len(tl) == 1

    def test_test_add_tag(self):
        tl = Tags.TagLibrary()

        # Correct Case
        tl.add_tag('TEST1')
        assert tl.TEST1 == 1
        assert tl._tag_counter == 2
        assert len(tl) == 2 and tl._tag_names[1] == 'TEST1'

        # Duplicate Case
        with pytest.raises(Tags.DuplicateTagError):
            tl.add_tag('TEST1')

    def test_get_tag_name(self):
        tl = Tags.TagLibrary()

        # Default case
        assert tl.get_tag_name(tl.NONE) == 'NONE'

        # Underbounds
        with pytest.raises(Tags.TagNotFoundError):
            tl.get_tag_name(-1)

        # Overbounds
        with pytest.raises(Tags.TagNotFoundError):
            tl.get_tag_name(1)


def test_get_tag_name():
    # This test comes first because test_add_tag adds a tag to the global TagLibrary
    # Default case
    assert Tags.get_tag_name(Tags.NONE) == 'NONE'

    # Underbounds
    with pytest.raises(Tags.TagNotFoundError):
        Tags.get_tag_name(-1)

    # Overbounds
    with pytest.raises(Tags.TagNotFoundError):
        Tags.get_tag_name(1)


def test_add_tag():
    # Correct Case
    Tags.add_tag('TEST1')
    assert Tags.TEST1 == 1
    assert Tags._module_library._tag_counter == 2
    assert len(Tags._module_library) == 2 and Tags._module_library._tag_names[1] == 'TEST1'

    # Duplicate Case
    with pytest.raises(Tags.DuplicateTagError):
        Tags.add_tag('TEST1')

