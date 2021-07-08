from sys import maxsize
from ECAgent.Core import System, Model


class Collector(System):
    """ This is the Collector base class. Collectors are, by default, Systems and behave the same way.
     The collector base class adds a 'records' list property. This property holds all of the data collected
     by the collector.
     When writing your own collector, override the collect() method not the execute() method. The Collector base
     class automatically calls the collect() method whenever the execute() method is called. If you do need to override
     the execute method, make sure you also call the collect() method to follow the intended behaviour of a Collector
     object."""
    def __init__(self, id: str, model: Model, priority=-1, frequency=1, start=0, end=maxsize):
        super().__init__(id, model, priority, frequency, start, end)

        self.records = []

    def execute(self):
        """ This overrides the Systems base execution method. It simply calls the collect method"""
        self.collect()

    def collect(self):
        """The collect method. This method is overridden to define the data collection behaviour of your Custom
        Collector."""
        pass


class AgentCollector(Collector):
    """This is a collector system specifically designed to iterate through every iteration whenever the system is
    executed. The AgentCollector defaults its systemID to 'AgentCollector'. If you are using multiple agent collectors,
    you must give them unique ids.

    An AgentCollector can be supplied with custom lambdas for both agent specific operations as well as composite data
    collection. The agentFunc must be a function that accepts an agent as input like so:
        def myCustomCollectionFunc(agent):
            return data

    The result of that function is then stored in a dict that uses the agent's id as a key. If None is returned, the
    collector simply skips that agent.

    If you want to collect composite/aggregate data about the model (like a gini-index), supplying the compositeFunc
    property with a lambda that returns a dict of all of the composite data will do the trick. The function might look
    like so:

        def myCustomCompositeFunction(agents)
            return {}

    The dict returned is then used to update the dict of that record. Returning None will not update the dict.
    To see the agent collector in action, see the Environment and Data Collection tutorial."""

    def __init__(self, model: Model, agentFunc, compositeFunc=None, includeTimstep=False, id="AgentCollector",
                 priority=-1, frequency=1, start=0, end=maxsize):
        super().__init__(id, model, priority, frequency, start, end)

        self.agentFunc = agentFunc
        self.compositeFunc = compositeFunc
        self.includeTimestep = includeTimstep

    def collect(self):
        """ The AgentCollector Collect() function iterates through every agent, a, in the model.environments.agents dict
        calling the agentFunc lambda like so agentFunc(a). The result of that call is then stored in a temporary dict
        that is later added to the records list. If includeTimestep is True, the collector will also the record the
        value of the current timestep in the tmpDict.
        After calling agentFunc(a) for all agents, the compositeFunc is called and supplied with a dict of all agents.
        The dict returned from the compositeFunc(agents) operation is then used to update the tmpDict.
        A record will not be appended to the records list if the tmpDict is empty."""

        # Create Empty record
        tmpDict = {}

        # Include timestep value in record
        if self.includeTimestep:
            tmpDict['timestep'] = self.model.systemManager.timestep

        # Loop through all agents in the environment
        for agentKey in self.model.environment.agents:
            result = self.agentFunc(self.model.environment.agents[agentKey])

            # If the result from the agentFunc is not None, add result to the dict
            if result is not None:
                tmpDict[agentKey] = result

        # Call compositeFunc
        if self.compositeFunc is not None:
            comp_result = self.compositeFunc(self.model.environment.agents)

            # Add comp_result to lambda if not None
            if comp_result is not None:
                tmpDict.update(comp_result)

        # Add record if tmpDict is not empty
        if len(tmpDict) > 0:
            self.records.append(tmpDict)


class FileCollector(Collector):
    """This is the base class for Collectors that want to write to files. The base implementation simply writes the
    records of the collector to the specified file name.
    When implementing your own FileCollector, you may need to override two methods:
    - The collect() method (As you would if you were writing your own non file-based collector).
    - The write_records() method which describes how your collector writes content to a file."""

    def __init__(self, id: str, model: Model, filename: str, priority=-1, frequency=1, start=0, end=maxsize,
                 filemode: str = 'a', write_count: int = 0, clear_records_on_write: bool = True):
        super().__init__(id, model, priority, frequency, start, end)

        self.filename = filename
        self.filemode = filemode
        self.write_count = write_count
        self.last_write = 0
        self.clear_records_on_write = clear_records_on_write

    def execute(self):
        super().execute()
        self.last_write += 1  # Increase counter since we collected data

        if self.write_count < self.last_write:
            self.write_records()
            self.last_write = 0

            if self.clear_records_on_write:
                self.records.clear()

    def write_records(self):
        """Loops through all of the self.records and writes their contents to a file specified by the self.filename
        property."""
        file = open(self.filename, self.filemode)

        for record in self.records:
            file.write(record)

        file.close()
