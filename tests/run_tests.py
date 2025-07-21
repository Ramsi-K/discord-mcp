import unittest
import os
import sys

# Add the parent directory to the path so we can import the server_registry package
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the test modules
from tests.test_server_registry import TestServerRegistry

if __name__ == "__main__":
    # Create a test suite
    test_suite = unittest.TestSuite()

    # Add the test cases
    test_suite.addTest(unittest.makeSuite(TestServerRegistry))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())
