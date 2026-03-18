import unittest
import sys


def run_unit_tests(verbosity=2):
    from tests.unit.test_database import (
        TestSQLiteDatabaseOperations,
        TestAuditLogOperations,
        TestMongoDBPatientRecords
    )
    from tests.unit.test_auth import (
        TestAuthenticationFunctions,
        TestEmailValidation,
        TestInputSanitization,
        TestPasswordValidation
    )

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestSQLiteDatabaseOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestAuditLogOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestMongoDBPatientRecords))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestEmailValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestInputSanitization))
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordValidation))

    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)


def run_functional_tests(verbosity=2):
    from tests.functional.test_workflows import (
        TestUserRegistrationWorkflow,
        TestLoginAndAuthenticationWorkflow,
        TestPatientRecordWorkflow,
        TestRoleBasedAccessControlWorkflow,
        TestSecurityWorkflow
    )

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestUserRegistrationWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestLoginAndAuthenticationWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestPatientRecordWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestRoleBasedAccessControlWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityWorkflow))

    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)


def run_integration_tests(verbosity=2):
    from tests.integration.test_interactions import (
        TestAuthenticationDatabaseIntegration,
        TestAuditLoggingIntegration,
        TestPatientRecordDatabaseIntegration,
        TestAPIIntegrationWithDatabase,
        TestEndToEndUserJourney
    )

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationDatabaseIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAuditLoggingIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPatientRecordDatabaseIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIIntegrationWithDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndUserJourney))

    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)


def run_all_tests(verbosity=2):
    print("=" * 70)
    print("RUNNING ALL TESTS")
    print("=" * 70)

    print("\n" + "=" * 70)
    print("UNIT TESTS")
    print("=" * 70)
    unit_result = run_unit_tests(verbosity)

    print("\n" + "=" * 70)
    print("FUNCTIONAL TESTS")
    print("=" * 70)
    functional_result = run_functional_tests(verbosity)

    print("\n" + "=" * 70)
    print("INTEGRATION TESTS")
    print("=" * 70)
    integration_result = run_integration_tests(verbosity)

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    total_unit = unit_result.testsRun
    total_func = functional_result.testsRun
    total_integ = integration_result.testsRun
    total_tests = total_unit + total_func + total_integ

    failed_unit = len(unit_result.failures) + len(unit_result.errors)
    failed_func = len(functional_result.failures) + len(functional_result.errors)
    failed_integ = len(integration_result.failures) + len(integration_result.errors)
    total_failed = failed_unit + failed_func + failed_integ

    print(f"\nUnit Tests:        {total_unit} tests, {failed_unit} failures")
    print(f"Functional Tests:  {total_func} tests, {failed_func} failures")
    print(f"Integration Tests: {total_integ} tests, {failed_integ} failures")
    print(f"\nTOTAL:             {total_tests} tests, {total_failed} failures")
    print("=" * 70)

    return total_failed == 0


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run tests for Patient Record Management System')
    parser.add_argument(
        '--type',
        choices=['all', 'unit', 'functional', 'integration'],
        default='all',
        help='Type of tests to run'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()
    verbosity = 2 if args.verbose else 1

    if args.type == 'unit':
        result = run_unit_tests(verbosity)
        success = result.wasSuccessful()
    elif args.type == 'functional':
        result = run_functional_tests(verbosity)
        success = result.wasSuccessful()
    elif args.type == 'integration':
        result = run_integration_tests(verbosity)
        success = result.wasSuccessful()
    else:
        success = run_all_tests(verbosity)

    sys.exit(0 if success else 1)

