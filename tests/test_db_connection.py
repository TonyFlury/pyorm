#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Test Suite for test_db_connection.py

Summary : 
    <summary of module/class being tested>
Use Case : 
    As a pyorm Developer I want Reusable generic database connection system So that My code can make the most efficient use of resources

Testable Statements :
    Can I control share connections handles within a thread
    Can I control shareing connections between thread
    
    Test Series 
    300* : test Core connection functionality
"""
import sys
import inspect
import unittest
import click

from pyorm.db.engine._core import EngineCore
from collections import defaultdict

from threading import Thread

from pathlib import Path

from pyorm.db.models._core import _Field

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '29 Jul 2017'


class DummyEngine(EngineCore):
    _step = 0

    def __init__(self, db_path, shared=True, unique_per_thread=True):
        super().__init__(db_path, shared=shared, unique_per_thread=unique_per_thread)

    def get_db_handle(self):
        DummyEngine._step += 1
        return DummyEngine._step

    @classmethod
    def reset(cls):
        cls._step = 0
        super().reset()

    # Dummy methods to match abstract methods - they don't need to do anything here.
    def column_constraint(self, field: _Field):
        pass

    def column_name(self, field: _Field):
        pass

    def column_type(self, field: _Field):
        pass

    def start(self):
        pass

class ConnectionCoreTest(unittest.TestCase):

    def setUp(self):
        DummyEngine.reset()

    def tearDown(self):
        pass

    def test_300_000_connection_basic_info(self):
        """Test that the EngineCore object retains key information"""
        db_file = 'database.db'

        con1 = DummyEngine(db_path=Path(db_file))
        self.assertFalse(con1.is_connected(), 'Connection instance reports as connected')
        self.assertEqual(str(con1.db_path), db_file, 'path recorded incorrectly')
        self.assertIsNone(con1.handle, 'Connection reference exists')

    def test_300_001_single_connection(self):
        """Test that the 'get_db_handle method is called correctly"""

        c1 = DummyEngine(db_path=Path('database.db'))
        self.assertFalse(c1.is_connected(), 'Connection instance reports as connected')

        con1_ref = c1.connect()
        self.assertTrue(c1.is_connected(), 'Connection instance reports as disconnected')

        self.assertEqual(con1_ref, 1, 'Expected handle ref of 1 from get_db_handle() method')
        self.assertEqual(con1_ref, c1.handle, 'Unexpected value of handle property')

    def test_300_002_two_connections_on_same_file(self):
        """Shared connections same file, same thread - connections will be the same """

        c1 = DummyEngine(db_path=Path('database.db'))
        c2 = DummyEngine(db_path=Path('database.db'))

        con1_ref = c1.connect()
        self.assertTrue(c1.is_connected(), 'Connection instance reports as disconnected')
        con2_ref = c2.connect()
        self.assertTrue(c1.is_connected(), 'Connection instance reports as disconnected')

        self.assertEqual(con1_ref, con2_ref, 'Connection not shared as expected')

    def test_300_003_two_connect_calls_on_same_Connection(self):
        """Shared connections same file, same thread - connections will be the same """

        c1 = DummyEngine(db_path=Path('database.db'))

        con1_ref = c1.connect()
        self.assertTrue(c1.is_connected(), 'Connection instance reports as disconnected')

        con2_ref = c1.connect() # SHould return the same handle ref
        self.assertTrue(c1.is_connected(), 'Connection instance reports as disconnected')

        self.assertEqual(con1_ref, con2_ref, 'Connection not shared as expected')

    def test_300_004_two_connections_on_different_files(self):
        """Shared connections different files, same thread - connections will be different"""
        db_file = 'database.db'

        c1 = DummyEngine(db_path=Path('database1.db'))
        c2 = DummyEngine(db_path=Path('database2.db'))

        con1_ref = c1.connect()
        self.assertTrue(c1.is_connected(), 'Connection instance reports as disconnected')

        con2_ref = c2.connect()
        self.assertTrue(c1.is_connected(), 'Connection instance reports as disconnected')

        self.assertNotEqual(con1_ref, con2_ref, 'Connection has been shared - incorrectly')

    def test_300_005_two_connections_on_same_file_not_shared(self):
        """Not Shared connections same file, same thread - connections will be different"""

        c1 = DummyEngine(db_path=Path('database.db'), shared=False)
        c2 = DummyEngine(db_path=Path('database.db'), shared=False)

        con1_ref = c1.connect()
        self.assertTrue(c1.is_connected(), 'Connection instance reports as disconnected')

        con2_ref = c2.connect()
        self.assertTrue(c1.is_connected(), 'Connection instance reports as disconnected')

        self.assertNotEqual(con1_ref, con2_ref, 'Connection has been shared - incorrectly')

    def test_300_006_two_connections_on_same_file_two_threads(self):
        """Not Shared connections same file, two threads - connections will be different"""
        db_file = 'database.db'
        connections = set()

        def testing( db_path):
            con = DummyEngine(db_path=Path(db_path), unique_per_thread=True)
            connections.add(con.connect())
            self.assertTrue(con.is_connected(), 'Connection instance reports as disconnected')

        t1 = Thread(target=testing,kwargs={'db_path':db_file})
        t2 = Thread(target=testing,kwargs={'db_path':db_file})
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertSetEqual(connections,{1,2},'Unexpected handle values from threads')

    def test_300_007_two_connections_on_same_file_two_threads(self):
        """Shared connections same file, two threads - connections will be different"""
        db_file = 'database.db'
        connections = defaultdict(int)

        def testing( db_path):
            con = DummyEngine(db_path=Path(db_path), unique_per_thread=False)
            connections[con.connect()] += 1
            self.assertTrue(con.is_connected(), 'Connection instance reports as disconnected')

        t1 = Thread(target=testing,kwargs={'db_path':db_file})
        t2 = Thread(target=testing,kwargs={'db_path':db_file})
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertDictEqual(connections,{1:2}, 'Sharing between threads not working')

    def test_300_010_single_connection_disconnects(self):
        """Test that the disconnect method returns correct value when a single connect is made"""
        connection = DummyEngine(db_path='database.db')
        connect_ref = connection.connect()

        status = connection.disconnect()

        # Single handle - only one use - so status must be True
        self.assertTrue(status, 'Unexpected return value from disconnect')
        self.assertIsNone(connection.handle, 'Unexpected not None value from handle property')

    def test_300_011_single_connection_two_disconnects(self):
        """Test that the disconnect method returns correct value when called twice on after a single connect is made"""
        connection = DummyEngine(db_path='database.db')
        connect_ref = connection.connect()

        status = connection.disconnect()

        # Single handle - only one use - so status must be True
        self.assertTrue(status, 'Unexpected return value from disconnect')
        self.assertIsNone(connection.handle, 'Unexpected not None value from handle property')

        status = connection.disconnect()

        # Single handle - only one use - so status must be False
        self.assertFalse(status, 'Unexpected return value from disconnect on 2nd call')
        self.assertIsNone(connection.handle, 'Unexpected not None value from handle property')

    def test_300_012_two_calls_to_connect_disconnects(self):
        """Test that the disconnect method returns correctly after two connect attempts"""
        connection = DummyEngine(db_path='database.db')
        connect_ref1 = connection.connect()
        connect_ref2 = connection.connect()

        self.assertEqual(connect_ref1, connect_ref2)

        # Two connections attempts - first disconnect should return False
        status = connection.disconnect()
        self.assertFalse(status)
        self.assertIsNotNone(connection.handle)

        # 2nd disconnect attempt - 2nd disconnect should return True
        status = connection.disconnect()
        self.assertTrue(status)
        self.assertIsNone(connection.handle)

    def test_300_013_two_ConnectionCore_objects(self):
        """Test that the disconnect method returns the correct value when two Connection objects are sharing same handle"""
        connection1 = DummyEngine(db_path='database.db')
        connection2 = DummyEngine(db_path='database.db')
        connect_ref1 = connection1.connect()
        connect_ref2 = connection2.connect()

        self.assertEqual(connect_ref1, connect_ref2)
        status = connection1.disconnect()

        # Two connections attempts - first disconnect should return False
        self.assertFalse(status)

        # 2nd disconnect attempt - 2nd disconnect should return True
        status = connection2.disconnect()
        self.assertTrue(status)

    def test_300_014_two_different_ConnectionCore_objects(self):
        """Test that the disconnect method returns the correct value when two Connection objects are not sharing"""
        connection1 = DummyEngine(db_path='database.db', shared=False)
        connection2 = DummyEngine(db_path='database.db', shared=False)
        connect_ref1 = connection1.connect()
        connect_ref2 = connection2.connect()

        self.assertNotEqual(connect_ref1, connect_ref2)

        status = connection1.disconnect()
        # Two connections attempts - first disconnect should return False
        self.assertTrue(status)

        # 2nd disconnect attempt - 2nd disconnect should return True
        status = connection2.disconnect()
        self.assertTrue(status)


def load_tests(loader, tests=None, pattern=None):
    classes = [cls for name, cls in inspect.getmembers(sys.modules[__name__],
                                                       inspect.isclass)
               if issubclass(cls, unittest.TestCase)]

    classes.sort(key=lambda cls_: cls_.setUp.__code__.co_firstlineno)
    suite = unittest.TestSuite()
    for test_class in classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite


@click.command()
@click.option('-v', '--verbose', default=2, help='Level of output', count=True)
@click.option('-s', '--silent', is_flag=True, default=False)
def main(verbose, silent):
    verbose = 0 if silent else verbose

    ldr = unittest.TestLoader()
    test_suite = load_tests(ldr)
    unittest.TextTestRunner(verbosity=verbose).run(test_suite)


if __name__ == '__main__':
    main()
