import itertools as itt

# from multiprocessing import Pool
# from sys import maxsize

# from ECAgent.Core import Model
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    # Type,
    Union,
)


class ParameterList:
    """This class allows for the construction of parameter sets which can be used by ``ECAgent.Batching`` functionality.

    Each parameter added to the ``ParameterList`` can be a single value or a list of values. When the parameter list is
    built, the list will contain unique parameter sets for all values included in a parameter.

    For example::
        import ECAgent.Batching as batching

        p_list = batching.ParameterList()  # Create ParameterList

        # Add a parameter with one value
        p_list.add_parameter("size", 10)
        # Add a parameter with multiple values
        p_list.add_parameter("num_agents", [10, 20, 30, 40, 50])

        # Build parameter list
        p_set = p_list.build()

        # p_set will contain the following parameter sets:
        [
            {"size": 10, "num_agents: 10},
            {"size": 10, "num_agents: 20},
            {"size": 10, "num_agents: 30},
            {"size": 10, "num_agents: 40},
            {"size": 10, "num_agents: 50}
        ]
    """

    def __init__(self, parameters: Optional[Dict[str, Union[Any, Iterable[Any]]]] = None):
        """ Creates a ParameterList object.

        Parameters
        ----------
        parameters : Optional[Dict[str, Union[Any, Iterable[Any]]]]
            An optional dictionary that contains the parameters that will be converted into a parameter set.
            Defaults to ``None`` which results in an empty ParameterList object.

        Raises
        ------
        AttributeError
            If any of the keys in ``parameters`` are not of type ``str``.
        """
        self._parameters = {}
        if parameters is not None:
            for key in parameters:
                if type(key) != str:
                    raise AttributeError(f"All parameter keys must of type str found {type(key)} instead.")
                else:
                    self._parameters[key] = parameters[key]

    def add_parameter(self, name: str, values: Union[Any, Iterable[Any]]):
        """ Adds a parameter to the ``ParameterList``. May either be a single value (i.e. ``10``) or an iterable
        (e.g. ``[1, 2, 4, 4]``).

        Parameters
        ----------
        name : str
            The name of the parameter.
        values : Union[Any, Iterable[Any]]
            The values the parameter may take on.

        Raises
        ------
        AttributeError
            If ``name`` is not of type ``str``.
        KeyError
            If parameter with ``name`` already exists within the ``ParameterList``.
        """
        if type(name) != str:
            raise AttributeError(f"All parameter keys must of type str found {type(name)} instead.")

        if name in self._parameters:
            raise KeyError(f"Parameter with name {name} already exists within the ParameterList.")

        self._parameters[name] = values

    def remove_parameter(self, name: str):
        """Removes a parameter from the ``ParameterList``.

        Parameters
        ----------
        name : str
            The name of the parameter to remove.

        Raises
        ------
        KeyError
            If ``name`` is not a valid parameter name.
        """
        if name not in self._parameters:
            raise KeyError(f"Parameter with name {name} does not exist in the ParameterList.")
        del self._parameters[name]

    def build(self) -> List[Dict[str, Any]]:
        """Builds and returns a parameter set from the ``ParameterList`` object.

        Returns
        -------
        List[Dict[str, Any]]
            containing dictionaries describing all experiments to investigate.
        """
        param_list = []
        for key, value in self._parameters.items():
            if type(value) == str:  # Strings are iterable but we treat them as a single value
                args = [(key, value)]
            else:
                try:
                    args = [(key, v) for v in value]
                except TypeError:
                    args = [(key, value)]
            param_list.append(args)
        result = [dict(kwargs) for kwargs in itt.product(*param_list)]
        return result
