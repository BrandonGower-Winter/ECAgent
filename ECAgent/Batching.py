import itertools as itt
import statistics as stats

from multiprocessing import Pool
from sys import maxsize

from ECAgent.Core import Model
from enum import IntEnum
from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
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


def _build_model_from_kwargs(model_cls: Type[Model], kwargs: dict) -> Model:
    """Builds a Model from a specified keyword-argument.

    Parameters
    ----------
    model_cls : Type[Model]
        The type of the model to be built.
    kwargs : dict
        The keyword-arguments to specify when building the model.

    Returns
    -------
    Model
        The built model of type ``model_cls`` using ``kwargs``.
    """
    return model_cls(**kwargs)


def _run_model_for_batch(model_cls: Type[Model], kwargs: dict, collectors: Optional[Union[str, Iterable[str]]] = None,
                         max_timesteps: Optional[int] = maxsize) -> Union[None, Dict[str, List[Any]], List[Any]]:
    """Builds and runs a model.

    Parameters
    ----------
    model_cls : Type[Model]
        The class of the model to build.
    kwargs : dict
        The keyword-arguments for the model.
    collectors : Optional[Union[str, Iterable[str]]]
        The name of the collectors whose data will be returned. Defaults to ``None``.
    max_timesteps : Optional[int]
        The maximum number of steps to run the model for. Defaults to ``sys.maxsize``.

    Returns
    -------
    Union[None, Dict[str, List[Any]], List[Any]]:
        The data collected by the specified collectors (if any).
    """
    model = _build_model_from_kwargs(model_cls, kwargs)  # Build Model
    while model.is_running() and model.systems.timestep < max_timesteps:  # Run Model
        model.execute()

    if collectors is None:  # No Data Collection
        return None
    elif type(collectors) == str:  # In the case of one collector
        return model.systems[collectors].records
    else:  # Collector is an Iterable
        return {model.systems[collector].id: model.systems[collector].records for collector in collectors}


# Batch Run
def batch_run(model_cls: Type[Model], parameters: Union[ParameterList, Dict[str, Union[Any, Iterable[Any]]]],
              collectors: Optional[Union[str, List[str]]] = None,
              processes: Optional[int] = 1, max_timesteps: int = maxsize,
              repetitions: int = 1) -> Union[None, Dict[str, List[Any]], List[Any]]:
    """Method for executing models in batches over user-specified parameter sets. This function supports the use of a
    dictionary or ``ParameterList`` as input.

    For example::

        batch_run(ExampleModel, {'num_agents': [10, 20, 30], 'env_size': [10, 20]})

    Is equivalent to::

        p_list = ParameterList()
        p_list.add_parameter('num_agent', [10, 20, 30])
        p_list.add_parameter('env_size', [10, 20])

        batch_run(ExampleModel, p_list)

    Both of which will create and run models of type ``ExampleModel`` for each of the following parameters::

        [
            {'num_agents': 10, 'env_size': 10},
            {'num_agents': 10, 'env_size': 20},
            {'num_agents': 20, 'env_size': 10},
            {'num_agents': 20, 'env_size': 20},
            {'num_agents': 30, 'env_size': 10},
            {'num_agents': 30, 'env_size': 20},
        ]

    The function also allows users to specify the name(s) of any data ``Collector`` systems whose ``records`` property
    will be returned. This value can either be a ``str`` or ``Iterable``::

        # For a single collector
        data = batch_run(
            ExampleModel,
            {'num_agents': [10, 20, 30], 'env_size': [10, 20]},
            collectors='collector_name'
        )

        # For multiple collectors
        data = batch_run(
            ExampleModel,
            {'num_agents': [10, 20, 30], 'env_size': [10, 20]},
            collectors=['collector1', 'collector2']
        )


    Parameters
    ----------
    model_cls : Type[Model]
        The class of the model to build.
    parameters: Union[ParameterList, Dict[str, Union[Any, Iterable[Any]]]]
        The set of parameters to build and run models with. May be a ``ParameterList`` or ``dict``.
    collectors : Optional[Union[str, Iterable[str]]]
        The name of the collectors whose data will be returned. Defaults to ``None``.
    processes : Optional[int]
        The number of processes to spawn to run models on. Defaults to ``1``.
    max_timesteps : Optional[int]
        The maximum number of steps to run the model for. Defaults to ``sys.maxsize``.
    repetitions : Optional[int]
        The number of times to repeat each parameter set. Defaults to ``1``.

    Returns
    -------
    Union[None, Dict[str, List[Any]], List[Any]]:
        The data collected by the specified collectors (if any). If no collector is specified, function
        returns ``None``. If one collector is specified, a list containing the records of each model's collector is
        returned. If multiple collectors are specified, a list containing dictionaries of each models collectors'
        records are returned.
    """
    if not (collectors is None or type(collectors) == str or isinstance(collectors, Iterable)):
        raise AttributeError(
            f"'collectors' argument must be of type None, str or Iterable. Encountered type {type(collectors)}."
        )
    # Build Parameter List
    simulation_kwargs = parameters.build() if type(parameters) == ParameterList else ParameterList(parameters).build()
    skwargs_with_repetition = simulation_kwargs * repetitions

    # results array
    results = []

    run_model = partial(
        _run_model_for_batch,
        model_cls,
        collectors=collectors,
        max_timesteps=max_timesteps
    )

    # For model arguments
    if processes == 1:
        for run in skwargs_with_repetition:
            data = run_model(run)
            if data is not None:
                results.append(data)
    else:
        with Pool(processes) as pool:
            for data in pool.imap_unordered(run_model, skwargs_with_repetition):
                if data is not None:
                    results.append(data)

    return results


class ScoreMode(IntEnum):
    """Enum that determines which metric should be used for evaluation when performing a parameter tuning process (e.g.
    a ``grid_search.

    Values are::

        MIN = 0  # Return parameter set that returned the lowest score.
        MAX = 1  # Return parameter set that returned the highest score.
        MIN_MEAN = 2  # Return parameter set that returned the lowest score (averaged across all repetitions).
        MAX_MEAN = 3  # Return parameter set that returned the highest score (averaged across all repetitions).
        MIN_SUM = 4  # Return parameter set that returned the lowest score total across all repetitions.
        MAX_SUM = 5  # Return parameter set that returned the highest score total across all repetitions.
        MIN_VARIANCE = 6  # Return parameter set that returned the lowest variance in score across all repetitions.
        MAX_VARIANCE = 7  # Return parameter set that returned the highest variance in score across all repetitions.
    """
    MIN = 0
    MAX = 1
    MIN_MEAN = 2
    MAX_MEAN = 3
    MIN_SUM = 4
    MAX_SUM = 5
    MIN_VARIANCE = 6
    MAX_VARIANCE = 7


def _run_model_for_search(model_cls: Type[Model], score_func: Callable[[Model], float], repetitions: int,
                          parameters: Dict[str, Any], max_timesteps: int = maxsize) -> Dict[str, Any]:
    """Run model for Search Tasks (e.g. ``grid_search``).

    Parameters
    ----------
    model_cls : Type[Model]
        Type of model to instantiate.
    score_func : Callable[[Model], float]
        Callable object that evaluates a model and returns its score.
    repetitions : int
        Number of times to evaluate the model with the same parameters.
    parameters : Dict[str, Any]
        The parameters used to construct the model.
    max_timesteps : int
        The maximum number of timesteps to run the model for. Defaults to ``sys.maxsize``.

    Returns
    -------
    Dict[str, Any]
        The parameter set that was executed. It contains a ``'records'`` key which contains the scores obtained by the
        parameter set.
    """
    records = []
    for _ in range(repetitions):  # For each repetition
        model = _build_model_from_kwargs(model_cls, parameters)  # Build Model
        while model.is_running() and model.systems.timestep < max_timesteps:  # Run Model
            model.execute()

        records.append(score_func(model))  # Add result to records

    parameters['records'] = records
    return parameters


def _score_model_for_search(records: Iterable[float], mode: ScoreMode) -> float:
    """Returns the final score for a set of records.

    Parameters
    ----------
    records : Iterable[float]
        The values to evaluate.
    mode : ScoreMode
        Which type of score to apply.

    Returns
    -------
    float
        The final score obtained by the set of records.

    Raises
    ------
    ValueError
        If invalid ``ScoreMode`` value is used.
    """
    if mode == ScoreMode.MIN:
        return min(records)
    elif mode == ScoreMode.MAX:
        return max(records)
    elif mode == ScoreMode.MIN_MEAN or mode == ScoreMode.MAX_MEAN:
        return stats.mean(records)
    elif mode == ScoreMode.MIN_SUM or mode == ScoreMode.MAX_SUM:
        return sum(records)
    elif mode == ScoreMode.MIN_VARIANCE or mode == ScoreMode.MAX_VARIANCE:
        return stats.variance(records)

    raise ValueError(f"Invalid value of {mode} mode chosen. Value must come from ScoreMode.")


def grid_search(model_cls: Type[Model], parameters: Union[ParameterList, Dict[str, Union[Any, Iterable[Any]]]],
                score_func: Callable[[Model], float], processes: Optional[int] = 1, max_timesteps: int = maxsize,
                repetitions: int = 1, mode: ScoreMode = ScoreMode.MIN) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Method for performing a Grid Search for a model over user-specified parameter sets. A callable object must also
    be specified. It should accept a ``Model`` as input and return a ``float`` that represents the score of the model::

        def score_example(model : Model) -> float
            score = # Add logic to calculate score here.
            return score.

    The ``score_func`` determines the type of model behaviour that will be searched for. Consider a scenario where you
    want to find which parameters maximize the number of prey in a ``PredatorPrey`` model, a reasonable scoring function
    might count the number of prey agents and return that as the score for a given parameter set.

    This function supports the use of a dictionary or ``ParameterList`` as input. For example::

        grid_search(ExampleModel, {'num_agents': [10, 20, 30], 'env_size': [10, 20]}, score_example)

    Is equivalent to::

        p_list = ParameterList()
        p_list.add_parameter('num_agent', [10, 20, 30])
        p_list.add_parameter('env_size', [10, 20])

        grid_search(ExampleModel, p_list, score_example)

    Both of which will create and run models of type ``ExampleModel`` for each of the following parameters::

        [
            {'num_agents': 10, 'env_size': 10},
            {'num_agents': 10, 'env_size': 20},
            {'num_agents': 20, 'env_size': 10},
            {'num_agents': 20, 'env_size': 20},
            {'num_agents': 30, 'env_size': 10},
            {'num_agents': 30, 'env_size': 20},
        ]

    Once the Grid Search is complete, the function will return the best parameter set as well a list of all parameter
    sets investigated::

        p_best, p_list = grid_search(ExampleModel, {'num_agents': [10, 20, 30], 'env_size': [10, 20]}, score_example)

    To get the scores obtained by each run of a parameter set as well as the overall score obtained, you may access
    their ``'records'`` and ``'score'`` values::

        p_best['score']   # Returns the final score of the parameter set.
        p_best['records]  # Returns the scores obtained for repetition of the parameter set.

    Parameters
    ----------
    model_cls : Type[Model]
        The class of the model to build.
    parameters: Union[ParameterList, Dict[str, Union[Any, Iterable[Any]]]]
        The set of parameters to build and run models with. May be a ``ParameterList`` or ``dict``.
    score_func : Callable[[Model], float]
        Callable object that determines the score of the model.
    processes : Optional[int]
        The number of processes to spawn to run models on. Defaults to ``1``.
    max_timesteps : Optional[int]
        The maximum number of steps to run the model for. Defaults to ``sys.maxsize``.
    repetitions : Optional[int]
        The number of times to repeat each parameter set. Defaults to ``1``.
    mode : ScoreMode
        The function to use when evaluating the score(s) of each model. Defaults to ``ScoreMode.MIN``.

    Returns
    -------
    Tuple[Dict[str, Any], List[Dict[str, Any]]]
        Tuple containing the best parameter set found as the first element and a list of all parameter sets evaluated
        as the second element.
    """

    # Build Parameter List
    simulation_kwargs = parameters.build() if type(parameters) == ParameterList else ParameterList(parameters).build()

    # results array
    results = []

    run_model = partial(
        _run_model_for_search,
        model_cls,
        score_func,
        repetitions,
        max_timesteps=max_timesteps
    )

    # For model arguments
    if processes == 1:
        for run in simulation_kwargs:
            results.append(run_model(run))
    else:
        with Pool(processes) as pool:
            for data in pool.imap(run_model, simulation_kwargs):
                results.append(data)

    # Calculate best result
    is_min = mode % 2 == 0  # Note: May not work in future if more search modes are added that aren't min-max searches
    index = -1
    target_score = maxsize if is_min else -maxsize
    for i, result in enumerate(results):
        result['score'] = _score_model_for_search(result['records'], mode)
        if (is_min and result['score'] < target_score) or (not is_min and result['score'] > target_score):
            index, target_score = i, result['score']

    return results[index], results  # Return best parameter and summary of all results.
