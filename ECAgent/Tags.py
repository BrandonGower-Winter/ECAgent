"""Tags Module for ECAgent
==========================

This library contains all "Tag" functionality. In ECAgent, a tag is a unique ``(int,str)`` pair that is used to
associate similar agents together. Tags are not always useful, but they shine when a model has multiple agent types that
share a lot of similar components (i.e. Where component template matching doesn't work). Tags may also be useful
when building containers of similar agent types.

Tags are stored in a ``TagLibrary``. By default a global ``TagLibrary`` exists that can be accessed  directly through
the  ``Tags`` module.

To add a tag to the global ``TagLibrary``, do the following::

    import ECAgent.Tags as Tags

    Tags.add_tag("Tag1")

This will register ``Tag1`` with the ``TagLibrary``. ``Tag1`` will then be assigned a unique integer value which can
be accessed as follows::

    Tags.Tag1

If you want to get the ``str`` representation of a tag::

    Tags.get_tag_name(Tags.Tag1)

Which will return ``"Tag1"``.

Creating a local TagLibrary
---------------------------

If you do not want to use the global TagLibrary to store tags, you can create a local TagLibrary by doing the
following::

    import ECAgent.Tags as Tags

    local_tags = Tags.TagLibrary()

You will then be able to use all of the functionality discussed previously. To add a tag::

    local_tags.add_tag("Tag1")

To get the unique integer value of a Tag::

    local_tags.Tag1

To get the ``str`` representation of a Tag::

    local_tags.get_tag_name(local_tags.Tag1)

Tags and Agents
---------------

Tags are not particularly useful by themselves. To assign a tag to an ``Agent``, you can either do it at
initialization::

    import ECAgent.Core as Core
    import ECAgent.Tags as Tags

    Tags.add_tag('PREY')

    model = Core.model()
    p1 = Core.Agent('p1', model, tag = Tags.PREY)
    model.environment.add_agent(p1)

Or you can assign it post-initialization::

    p1.tag = Tags.PREY

To get a list of all agents with a particular tag, use the ``Environment.get_agents`` method. Specifying the tag as
follows::

    prey = environment.getAgents(tag = Tags.PREY)
"""


class TagLibrary:

    """Tag Library Class. It stores a list of agent tags and their unique identifiers.

    Attributes
    ----------
    NONE : int
        The default tag for all agents. It always has a value of 0.
    """

    def __init__(self):
        self.NONE = 0
        self._tag_counter = 1
        self._tag_names = ['NONE']

    def __len__(self) -> int:
        """Returns the number of tags stored in the ``TagLibrary``

        *Note* that the ``NONE`` tag is included so the value returned will be least 1.

        Returns
        -------
        int
            The number of tags in the ``TagLibrary``
        """
        return self._tag_counter

    def add_tag(self, tag_name: str):
        """Adds a tag to the ``TagLibrary`` with the name ``tag_name``.

        Parameters
        ----------
        tag_name : str
            The name of the tag being created.

        Raises
        ------
        DuplicateTagError
            If a tag_name that already exists is used.
        """

        # Check for duplicates
        if tag_name in self.__dict__:
            raise DuplicateTagError(tag_name)
        else:
            self.__dict__[tag_name] = self._tag_counter
            self._tag_counter += 1
            self._tag_names.append(tag_name)

    def get_tag_name(self, tag_id: int) -> str:
        """Returns a ``str`` representation of a tag.

        Parameters
        ----------
        tag_id : int
            The id of the tag.

        Returns
        -------
        str
            The ``str`` representation of the tag.

        Raises
        ------
        TagNotFoundError
            If the tag cannot be found.
        """
        if tag_id < 0 or tag_id > self._tag_counter - 1:
            raise TagNotFoundError(tag_id)
        else:
            return self._tag_names[tag_id]


class DuplicateTagError(Exception):
    """Exception raised when a duplicate Tag is created.

    Attributes:
    -----------
    tag_name : str
        The name of tag created.
    message : str
        Explanation of error.
    """

    def __init__(self, tag_name: str):
        """
        Parameters
        ----------
        tag_name : str
            The name of tag created.
        """
        self.tag_name = tag_name
        self.message = f'Tag with name "{tag_name}" already exists.'
        super(DuplicateTagError, self).__init__(self.message)


class TagNotFoundError(Exception):
    """Exception raised when a Tag can't be found.

    Attributes:
    -----------
    tag_id : int | str
        The name of searched tag.
    message : str
        Explanation of error.
    """

    def __init__(self, tag_id):
        """
        Parameters
        ----------
        tag_id : int | str
            The id of searched tag.
        """
        self.tag_id = tag_id
        self.message = f'Tag with id "{tag_id}" does not exist.'
        super(TagNotFoundError, self).__init__(self.message)


_module_library = TagLibrary()


def add_tag(tag_name: str):
    """Adds a tag to the global ``TagLibrary`` with the name ``tag_name``.

    Parameters
    ----------
    tag_name : str
        The name of the tag being created.

    Raises
    ------
    DuplicateTagError
        If a tag_name that already exists is used.
    """
    _module_library.add_tag(tag_name)


def get_tag_name(tag_id: int) -> str:
    """Returns a ``str`` representation of a tag.

    The tag is searched for in the global ``TagLibrary``

    Parameters
    ----------
    tag_id : int
        The id of the tag.

    Returns
    -------
    str
        The ``str`` representation of the tag.

    Raises
    ------
    TagNotFoundError
        If the tag cannot be found.
    """
    return _module_library.get_tag_name(tag_id)


def __getattr__(tag_name: str) -> int:
    """Returns
    ----------
    int
        The unique id for a tag with a ``name == tag_name``.

    Raises
    ------
    TagNotFoundError
        If tag does not exist.
    """
    if tag_name not in _module_library.__dict__:
        raise TagNotFoundError(tag_name)
    else:
        return _module_library.__dict__[tag_name]
