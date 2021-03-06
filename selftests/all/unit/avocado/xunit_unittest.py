import argparse
import unittest
import os
import sys
from xml.dom import minidom
from tempfile import mkstemp

# simple magic for using scripts within a source tree
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
basedir = os.path.dirname(basedir)
if os.path.isdir(os.path.join(basedir, 'avocado')):
    sys.path.append(basedir)

from avocado.plugins import xunit
from avocado import test
from avocado import job


class ParseXMLError(Exception):
    pass


class _Stream(object):

    def start_file_logging(self, param1, param2):
        pass

    def stop_file_logging(self):
        pass

    def set_tests_info(self, info):
        pass

    def notify(self, event, msg):
        pass

    def add_test(self, state):
        pass

    def set_test_status(self, status, state):
        pass


class xUnitSucceedTest(unittest.TestCase):

    def setUp(self):
        self.tmpfile = mkstemp()
        args = argparse.Namespace()
        args.xunit_output = self.tmpfile[1]
        self.test_result = xunit.xUnitTestResult(stream=_Stream(), args=args)
        self.test_result.start_tests()
        self.test1 = test.Test(job=job.Job())
        self.test1.status = 'PASS'
        self.test1.time_elapsed = 1.23

    def tearDown(self):
        os.close(self.tmpfile[0])
        os.remove(self.tmpfile[1])

    def testAddSuccess(self):
        self.test_result.start_test(self.test1)
        self.test_result.end_test(self.test1.get_state())
        self.test_result.end_tests()
        self.assertTrue(self.test_result.xml)
        with open(self.test_result.output) as fp:
            xml = fp.read()
        try:
            dom = minidom.parseString(xml)
        except Exception, details:
            raise ParseXMLError("Error parsing XML: '%s'.\nXML Contents:\n%s" % (details, xml))
        self.assertTrue(dom)
        els = dom.getElementsByTagName('testcase')
        self.assertEqual(len(els), 1)


if __name__ == '__main__':
    unittest.main()
