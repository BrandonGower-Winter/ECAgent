from ECAgent.Core import Agent
from ECAgent.Collectors import *

from unittest.mock import patch, mock_open


class TestCollector:

    def test__init__(self):
        model = Model()
        col = Collector("Collector", model)

        # Test default values
        assert col.id == "Collector"
        assert col.model is model
        assert col.start == 0
        assert col.end == maxsize
        assert col.frequency == 1
        assert col.priority == -1
        assert len(col.records) == 0

        # Test explicit values
        col = Collector("Collector", model, priority=100, start=0, end=maxsize, frequency=1)

        assert col.id == "Collector"
        assert col.model is model
        assert col.start == 0
        assert col.end == maxsize
        assert col.frequency == 1
        assert col.priority == 100
        assert len(col.records) == 0


class TestAgentCollector:

    def test__init__(self):

        def dummyFunc():
            pass

        model = Model()
        col = AgentCollector(model, dummyFunc)

        # Test default values
        assert col.id == "AgentCollector"
        assert col.model is model
        assert col.start == 0
        assert col.end == maxsize
        assert col.frequency == 1
        assert col.priority == -1
        assert len(col.records) == 0

        assert col.agentFunc is dummyFunc
        assert col.compositeFunc is None
        assert not col.includeTimestep

        # Test explicit values

        def dummyCompFunc():
            pass

        col = AgentCollector(model, dummyFunc, id="Collector", compositeFunc=dummyCompFunc,
                             priority=100, start=0, end=maxsize, frequency=1, includeTimstep=True)

        assert col.id == "Collector"
        assert col.model is model
        assert col.start == 0
        assert col.end == maxsize
        assert col.frequency == 1
        assert col.priority == 100
        assert len(col.records) == 0

        assert col.agentFunc is dummyFunc
        assert col.compositeFunc is dummyCompFunc
        assert col.includeTimestep

    def test_Collect(self):

        # Just Some setup:

        def dummyFuncNone(data):
            return None

        def dummyAgentFunc(agent):
            return 1

        def dummyCompositeFunc(agents):
            return {'value' : 1}

        #################

        model = Model()
        collector = AgentCollector(model, dummyFuncNone)

        # Test empty environment case works
        collector.execute()

        assert len(collector.records) == 0

        # test empty agentFunc returned
        model.environment.addAgent(Agent("a1",model))
        model.environment.addAgent(Agent("a2", model))

        collector.execute()

        assert len(collector.records) == 0

        # test includeTimestep

        collector.includeTimestep = True
        collector.execute()

        assert len(collector.records) == 1
        assert collector.records[0] == {'timestep': 0}

        # Test agent collection

        collector.includeTimestep = False
        collector.agentFunc = dummyAgentFunc
        collector.records.clear()

        collector.execute()

        assert len(collector.records) == 1
        assert collector.records[0] == {'a1': 1, 'a2': 1}

        # Test composite function returns None
        collector.agentFunc = dummyFuncNone
        collector.compositeFunc = dummyFuncNone
        collector.records.clear()

        collector.execute()

        assert len(collector.records) == 0

        # Test composite function
        collector.compositeFunc = dummyCompositeFunc

        collector.execute()

        assert len(collector.records) == 1
        assert collector.records[0] == {'value': 1}


class TestFileCollector:

    def test__init__(self):
        model = Model()
        col = FileCollector("Collector", model, 'test.txt')

        # Test default values
        assert col.id == "Collector"
        assert col.model is model
        assert col.start == 0
        assert col.end == maxsize
        assert col.frequency == 1
        assert col.priority == -1
        assert len(col.records) == 0

        assert col.filemode == 'a'
        assert col.filename == 'test.txt'
        assert col.clear_records_on_write
        assert col.write_count == 0
        assert col.last_write == 0

        # Test explicit values
        col = FileCollector("Collector", model, 'test.txt', priority=100, start=0, end=maxsize, frequency=1,
                            filemode='w', write_count=1, clear_records_on_write=False)

        assert col.id == "Collector"
        assert col.model is model
        assert col.start == 0
        assert col.end == maxsize
        assert col.frequency == 1
        assert col.priority == 100
        assert len(col.records) == 0

        assert col.filemode == 'w'
        assert col.filename == 'test.txt'
        assert not col.clear_records_on_write
        assert col.write_count == 1
        assert col.last_write == 0

    def test__write_records(self):
        model = Model()
        col = FileCollector("Collector", model, 'test.txt')

        m = mock_open()
        with patch("builtins.open", m, create=True):

            col.records.append(4)
            col.records.append(6)

            col.write_records()

        m.assert_called_once_with(col.filename, col.filemode)
        handle = m()

        handle.write.assert_any_call(4)
        handle.write.assert_any_call(6)

    def test__execute(self):

        model = Model()
        col = FileCollector("Collector", model, 'test.txt', write_count=1, clear_records_on_write=False)

        m = mock_open()

        col.records.append(4)
        col.records.append(6)

        with patch("builtins.open", m, create=True):
            col.execute()

            # By default, writing to a file should not be called
            assert not m.called
            assert col.last_write == 1

        # Change it to write every execution cycle
        col.write_count = 0

        # Test write to file but keep records
        m = mock_open()
        with patch("builtins.open", m, create=True):
            col.execute()

            m.assert_called_once_with(col.filename, col.filemode)
            handle = m()
            handle.write.assert_any_call(4)
            handle.write.assert_any_call(6)

            assert col.last_write == 0
            assert col.records == [4, 6]

        # Test write to file and clear records
        col.clear_records_on_write = True
        m = mock_open()
        with patch("builtins.open", m, create=True):
            col.execute()

            m.assert_called_once_with(col.filename, col.filemode)
            handle = m()
            handle.write.assert_any_call(4)
            handle.write.assert_any_call(6)

            assert col.last_write == 0
            assert col.records == []


