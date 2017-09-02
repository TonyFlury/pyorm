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
import inspect
import sys
import unittest
from collections import defaultdict
from pathlib import Path
from threading import Thread, get_ident

import click

from .DummyEngine import DummyEngine

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '29 Jul 2017'

class ConnectionCoreTest(unittest.TestCase):

    def setUp(self):
        DummyEngine.reset()

    def tearDown(self):
        pass

    def test_300_000_connection_basic_info(self):
        """Test that the EngineCore object retains key information"""
        db_file = 'database.db'

        con1 = DummyEngine(db_path=Path(db_file))

        self.assertEqual(str(con1.db_path), db_file, 'path recorded incorrectly')

    def test_300_001_single_connection(self):
        """Test that the 'get_connection method is called correctly"""

        c1 = DummyEngine(db_path=Path('database.db'))

        con1_ref = c1.connect()

        self.assertEqual(con1_ref._handle.value(), 1, 'Expected.connection ref of 1 from get_connection() method')

    def test_300_002_two_connections_on_same_file(self):
        """Shared connections same file, same thread - connections will be the same """

        c1 = DummyEngine(db_path=Path('database.db'))
        c2 = DummyEngine(db_path=Path('database.db'))

        con1_ref = c1.connect()
        con2_ref = c2.connect()

        self.assertIs(con1_ref, con2_ref, 'Connection not shared as expected')

    def test_300_003_two_connect_calls_on_same_Connection(self):
        """Shared connections same file, same thread - connections will be the same """

        c1 = DummyEngine(db_path=Path('database.db'))

        con1_ref = c1.connect()
        con2_ref = c1.connect() # SHould return the same.connection ref

        self.assertIs(con1_ref, con2_ref, 'Connection not shared as expected')

    def test_300_004_two_connect_calls_on_same_Engine_not_shared(self):
        """Shared connections same file, same thread - connections will be the same """

        c1 = DummyEngine(db_path=Path('database.db'), shared=False)

        con1_ref = c1.connect()

        con2_ref = c1.connect()

        self.assertIsNot(con1_ref, con2_ref, 'Connection not shared as expected')

    def test_300_005_two_connections_on_different_files(self):
        """Shared connections different files, same thread - connections will be different"""
        db_file = 'database.db'

        c1 = DummyEngine(db_path=Path('database1.db'))
        c2 = DummyEngine(db_path=Path('database2.db'))

        con1_ref = c1.connect()
        con2_ref = c2.connect()

        self.assertIsNot(con1_ref, con2_ref, 'Connection has been shared - incorrectly')

    def test_300_006_two_connections_on_same_file_not_shared(self):
        """Not Shared connections same file, same thread - connections will be different"""

        c1 = DummyEngine(db_path=Path('database.db'), shared=False)
        c2 = DummyEngine(db_path=Path('database.db'), shared=False)

        con1_ref = c1.connect()
        con2_ref = c2.connect()

        self.assertIsNot(con1_ref, con2_ref, 'Connection has been shared - incorrectly')

    def test_300_007_two_connections_on_same_file_back_to_back(self):
        """Try to open & close two connections back to back"""

        engine = DummyEngine(db_path=':memory:')

        con1_ref = engine.connect()
        self.assertEqual([x for x in engine.open_connections(':memory:')],[(get_ident(),con1_ref)])
        con1_ref.close()
        self.assertEqual([x for x in engine.open_connections(':memory:')],[])

        con2_ref = engine.connect()
        self.assertEqual([x for x in engine.open_connections(':memory:')],[(get_ident(),con2_ref)])
        con2_ref.close()
        self.assertEqual([x for x in engine.open_connections(':memory:')],[])

    def test_300_026_two_connections_on_same_file_two_threads(self):
        """Not Shared connections same file, two threads - connections will be different"""
        db_file = 'database.db'
        connections = []

        def testing( db_path):
            inst = DummyEngine(db_path=Path(db_path), unique_per_thread=True)
            connections.append(inst.connect())

        t1 = Thread(target=testing,kwargs={'db_path':db_file})
        t2 = Thread(target=testing,kwargs={'db_path':db_file})
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertIsNot(connections[0],connections[1], 'Unexpected.connection values from threads')

    def test_300_027_two_connections_on_same_file_two_threads(self):
        """Shared connections same file, two threads - connections will be same"""
        db_file = 'database.db'
        connections_list, connection_count = [], defaultdict(int)

        def testing( db_path):
            con = DummyEngine(db_path=Path(db_path), unique_per_thread=False)
            connections_list.append(con.connect())
            connection_count[con.connect()] += 1

        t1 = Thread(target=testing,kwargs={'db_path':db_file})
        t2 = Thread(target=testing,kwargs={'db_path':db_file})
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(connections_list[0],connections_list[1], 'Sharing between threads not working')
        self.assertEqual(connection_count[connections_list[0]], 2, 'Sharing between threads not working')

    def test_300_050_single_connection_disconnects(self):
        """Test that the disconnect method returns correct value when a single connect is made"""
        connection = DummyEngine(db_path='database.db')
        connect_ref = connection.connect()

        connect_ref.close()

        connect_ref.handle.close.assert_called_once_with()

    def test_300_051_single_connection_two_disconnects(self):
        """Test that the disconnect method returns correct value when called twice on after a single connect is made"""
        connection = DummyEngine(db_path='database.db')
        connect_ref = connection.connect()

        connect_ref.close()
        connect_ref.handle.close.assert_called_once_with()

        connect_ref.close()
        connect_ref.handle.close.assert_called_once_with()

    def test_300_052_two_calls_to_connect_disconnects(self):
        """Test that the disconnect method returns correctly after two connect attempts"""
        engine_inst = DummyEngine(db_path='database.db')
        connect_ref1 = engine_inst.connect()
        connect_ref2 = engine_inst.connect()

        self.assertEqual(connect_ref1, connect_ref2)

        # Two connections attempts - first disconnect should return False
        connect_ref1.close()
        connect_ref1.handle.close.assert_not_called()

        # 2nd disconnect attempt - 2nd disconnect should return True
        connect_ref2.close()
        connect_ref2.handle.close.assert_called_once_with()

    def test_300_053_two_ConnectionCore_objects(self):
        """Test that the disconnect method returns the correct value when two Connection objects are sharing same.connection"""
        engine_inst1 = DummyEngine(db_path='database.db')
        engine_inst2 = DummyEngine(db_path='database.db')
        connect_ref1 = engine_inst1.connect()
        connect_ref2 = engine_inst2.connect()

        self.assertEqual(connect_ref1, connect_ref2)
        connect_ref1.close()
        connect_ref1.handle.close.assert_not_called()

        # 2nd disconnect attempt - 2nd disconnect should return True
        connect_ref2.close()
        connect_ref2.handle.close.assert_called_once_with()

    def test_300_054_two_different_ConnectionCore_objects(self):
        """Test that the disconnect method returns the correct value when two Connection objects are not sharing"""
        connection1 = DummyEngine(db_path='database.db', shared=False)
        connection2 = DummyEngine(db_path='database.db', shared=False)
        connect_ref1 = connection1.connect()
        connect_ref2 = connection2.connect()

        self.assertNotEqual(connect_ref1, connect_ref2)

        connect_ref1.close()
        connect_ref1.handle.close.assert_called_once_with()

        connect_ref2.close()
        connect_ref2.handle.close.assert_called_once_with()


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
