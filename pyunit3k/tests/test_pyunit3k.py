# Copyright (c) 2008 Jonathan M. Lange. See LICENSE for details.

"""Tests for extensions to the base test library."""

from pyunit3k import TestCase, TestResult, change_test_id


class LoggingResult(TestResult):
    """TestResult that logs its event to a list."""

    def __init__(self, log):
        self._events = log
        super(LoggingResult, self).__init__()

    def startTest(self, test):
        self._events.append('startTest')
        super(LoggingResult, self).startTest(test)

    def stopTest(self, test):
        self._events.append('stopTest')
        super(LoggingResult, self).stopTest(test)

    def addFailure(self, *args):
        self._events.append('addFailure')
        super(LoggingResult, self).addFailure(*args)

    def addError(self, *args):
        self._events.append('addError')
        super(LoggingResult, self).addError(*args)

    def addSuccess(self, *args):
        self._events.append('addSuccess')
        super(LoggingResult, self).addSuccess(*args)


class TestAssertions(TestCase):
    """Test assertions in TestCase."""

    def raiseError(self, exceptionFactory, *args, **kwargs):
        raise exceptionFactory(*args, **kwargs)

    def test_formatTypes_single(self):
        # Given a single class, _formatTypes returns the name.
        class Foo:
            pass
        self.assertEqual('Foo', self._formatTypes(Foo))

    def test_formatTypes_multiple(self):
        # Given multiple types, _formatTypes returns the names joined by
        # commas.
        class Foo:
            pass
        class Bar:
            pass
        self.assertEqual('Foo, Bar', self._formatTypes([Foo, Bar]))

    def test_assertRaises(self):
        # assertRaises asserts that a callable raises a particular exception.
        self.assertRaises(RuntimeError, self.raiseError, RuntimeError)

    def test_assertRaises_fails_when_no_error_raised(self):
        # assertRaises raises self.failureException when it's passed a
        # callable that raises no error.
        ret = ('orange', 42)
        try:
            self.assertRaises(RuntimeError, lambda: ret)
        except self.failureException, e:
            # We expected assertRaises to raise this exception.
            self.assertEqual(
                '%s not raised, %r returned instead.'
                % (self._formatTypes(RuntimeError), ret), str(e))
        else:
            self.fail('Expected assertRaises to fail, but it did not.')

    def test_assertRaises_fails_when_different_error_raised(self):
        # assertRaises re-raises an exception that it didn't expect.
        self.assertRaises(
            ZeroDivisionError,
            self.assertRaises,
                RuntimeError, self.raiseError, ZeroDivisionError)

    def test_assertRaises_returns_the_raised_exception(self):
        # assertRaises returns the exception object that was raised. This is
        # useful for testing that exceptions have the right message.

        # This contraption stores the raised exception, so we can compare it
        # to the return value of assertRaises.
        raisedExceptions = []
        def raiseError():
            try:
                raise RuntimeError('Deliberate error')
            except RuntimeError, e:
                raisedExceptions.append(e)
                raise

        exception = self.assertRaises(RuntimeError, raiseError)
        self.assertEqual(1, len(raisedExceptions))
        self.assertTrue(
            exception is raisedExceptions[0],
            "%r is not %r" % (exception, raisedExceptions[0]))

    def test_assertRaises_with_multiple_exceptions(self):
        # assertRaises((ExceptionOne, ExceptionTwo), function) asserts that
        # function raises one of ExceptionTwo or ExceptionOne.
        expectedExceptions = (RuntimeError, ZeroDivisionError)
        self.assertRaises(
            expectedExceptions, self.raiseError, expectedExceptions[0])
        self.assertRaises(
            expectedExceptions, self.raiseError, expectedExceptions[1])

    def test_assertRaises_with_multiple_exceptions_failure_mode(self):
        # If assertRaises is called expecting one of a group of exceptions and
        # a callable that doesn't raise an exception, then fail with an
        # appropriate error message.
        expectedExceptions = (RuntimeError, ZeroDivisionError)
        failure = self.assertRaises(
            self.failureException,
            self.assertRaises, expectedExceptions, lambda: None)
        self.assertEqual(
            '%s not raised, None returned instead.'
            % self._formatTypes(expectedExceptions), str(failure))

    def assertFails(self, message, function, *args, **kwargs):
        """Assert that function raises a failure with the given message."""
        failure = self.assertRaises(
            self.failureException, function, *args, **kwargs)
        self.assertEqual(message, str(failure))

    def test_assertIn_success(self):
        # assertIn(needle, haystack) asserts that 'needle' is in 'haystack'.
        self.assertIn(3, range(10))
        self.assertIn('foo', 'foo bar baz')
        self.assertIn('foo', 'foo bar baz'.split())

    def test_assertIn_failure(self):
        # assertIn(needle, haystack) fails the test when 'needle' is not in
        # 'haystack'.
        self.assertFails('3 not in [0, 1, 2]', self.assertIn, 3, [0, 1, 2])
        self.assertFails(
            '%r not in %r' % ('qux', 'foo bar baz'),
            self.assertIn, 'qux', 'foo bar baz')

    def test_assertNotIn_success(self):
        # assertNotIn(needle, haystack) asserts that 'needle' is not in
        # 'haystack'.
        self.assertNotIn(3, [0, 1, 2])
        self.assertNotIn('qux', 'foo bar baz')

    def test_assertNotIn_failure(self):
        # assertNotIn(needle, haystack) fails the test when 'needle' is in
        # 'haystack'.
        self.assertFails('3 in [1, 2, 3]', self.assertNotIn, 3, [1, 2, 3])
        self.assertFails(
            '%r in %r' % ('foo', 'foo bar baz'),
            self.assertNotIn, 'foo', 'foo bar baz')

    def test_assertIsInstance(self):
        # assertIsInstance asserts that an object is an instance of a class.

        class Foo:
            """Simple class for testing assertIsInstance."""

        foo = Foo()
        self.assertIsInstance(foo, Foo)

    def test_assertIsInstance_multiple_classes(self):
        # assertIsInstance asserts that an object is an instance of one of a
        # group of classes.

        class Foo:
            """Simple class for testing assertIsInstance."""

        class Bar:
            """Another simple class for testing assertIsInstance."""

        foo = Foo()
        self.assertIsInstance(foo, (Foo, Bar))
        self.assertIsInstance(Bar(), (Foo, Bar))

    def test_assertIsInstance_failure(self):
        # assertIsInstance(obj, klass) fails the test when obj is not an
        # instance of klass.

        class Foo:
            """Simple class for testing assertIsInstance."""

        self.assertFails(
            '42 is not an instance of %s' % self._formatTypes(Foo),
            self.assertIsInstance, 42, Foo)

    def test_assertIsInstance_failure_multiple_classes(self):
        # assertIsInstance(obj, (klass1, klass2)) fails the test when obj is
        # not an instance of klass1 or klass2.

        class Foo:
            """Simple class for testing assertIsInstance."""

        class Bar:
            """Another simple class for testing assertIsInstance."""

        self.assertFails(
            '42 is not an instance of %s' % self._formatTypes([Foo, Bar]),
            self.assertIsInstance, 42, (Foo, Bar))


class TestAddCleanup(TestCase):
    """Tests for TestCase.addCleanup."""

    class LoggingTest(TestCase):
        """A test that logs calls to setUp, runTest and tearDown."""

        def setUp(self):
            self._calls = ['setUp']

        def brokenSetUp(self):
            # A tearDown that deliberately fails.
            self._calls = ['brokenSetUp']
            raise RuntimeError('Deliberate Failure')

        def runTest(self):
            self._calls.append('runTest')

        def tearDown(self):
            self._calls.append('tearDown')

    def setUp(self):
        self._result_calls = []
        self.test = TestAddCleanup.LoggingTest('runTest')
        self.logging_result = LoggingResult(self._result_calls)

    def assertLogEqual(self, messages):
        """Assert that the call log equals `messages`."""
        self.assertEqual(messages, self.test._calls)

    def logAppender(self, message):
        """Return a cleanup that appends `message` to the tests log.

        Cleanups are callables that are added to a test by addCleanup. To
        verify that our cleanups run in the right order, we add strings to a
        list that acts as a log. This method returns a cleanup that will add
        the given message to that log when run.
        """
        self.test._calls.append(message)

    def test_fixture(self):
        # A normal run of self.test logs 'setUp', 'runTest' and 'tearDown'.
        # This test doesn't test addCleanup itself, it just sanity checks the
        # fixture.
        self.test.run(self.logging_result)
        self.assertLogEqual(['setUp', 'runTest', 'tearDown'])

    def test_cleanup_run_before_tearDown(self):
        # Cleanup functions added with 'addCleanup' are called before tearDown
        # runs.
        self.test.addCleanup(self.logAppender, 'cleanup')
        self.test.run(self.logging_result)
        self.assertLogEqual(['setUp', 'runTest', 'cleanup', 'tearDown'])

    def test_add_cleanup_called_if_setUp_fails(self):
        # Cleanup functions added with 'addCleanup' are called even if setUp
        # fails. Note that tearDown has a different behavior: it is only
        # called when setUp succeeds.
        self.test.setUp = self.test.brokenSetUp
        self.test.addCleanup(self.logAppender, 'cleanup')
        self.test.run(self.logging_result)
        self.assertLogEqual(['brokenSetUp', 'cleanup'])

    def test_addCleanup_called_in_reverse_order(self):
        # Cleanup functions added with 'addCleanup' are called in reverse
        # order.
        #
        # One of the main uses of addCleanup is to dynamically create
        # resources that need some sort of explicit tearDown. Often one
        # resource will be created in terms of another, e.g.,
        #     self.first = self.makeFirst()
        #     self.second = self.makeSecond(self.first)
        #
        # When this happens, we generally want to clean up the second resource
        # before the first one, since the second depends on the first.
        self.test.addCleanup(self.logAppender, 'first')
        self.test.addCleanup(self.logAppender, 'second')
        self.test.run(self.logging_result)
        self.assertLogEqual(
            ['setUp', 'runTest', 'second', 'first', 'tearDown'])

    def test_tearDown_runs_after_cleanup_failure(self):
        # tearDown runs even if a cleanup function fails.
        self.test.addCleanup(lambda: 1/0)
        self.test.run(self.logging_result)
        self.assertLogEqual(['setUp', 'runTest', 'tearDown'])

    def test_cleanups_continue_running_after_error(self):
        # All cleanups are always run, even if one or two of them fail.
        self.test.addCleanup(self.logAppender, 'first')
        self.test.addCleanup(lambda: 1/0)
        self.test.addCleanup(self.logAppender, 'second')
        self.test.run(self.logging_result)
        self.assertLogEqual(
            ['setUp', 'runTest', 'second', 'first', 'tearDown'])

    def test_error_in_cleanups_are_captured(self):
        # If a cleanup raises an error, we want to record it and fail the the
        # test, even though we go on to run other cleanups.
        self.test.addCleanup(lambda: 1/0)
        self.test.run(self.logging_result)
        self.assertEqual(
            ['startTest', 'addError', 'stopTest'], self._result_calls)

    def test_keyboard_interrupt_not_caught(self):
        # If a cleanup raises KeyboardInterrupt, it gets reraised.
        def raiseKeyboardInterrupt():
            raise KeyboardInterrupt()
        self.test.addCleanup(raiseKeyboardInterrupt)
        self.assertRaises(
            KeyboardInterrupt, self.test.run, self.logging_result)

    def test_multipleErrorsReported(self):
        # Errors from all failing cleanups are reported.
        self.test.addCleanup(lambda: 1/0)
        self.test.addCleanup(lambda: 1/0)
        self.test.run(self.logging_result)
        self.assertEqual(
            ['startTest', 'addError', 'addError', 'stopTest'],
            self._result_calls)


class TestUniqueFactories(TestCase):
    """Tests for getUniqueString and getUniqueInteger."""

    def test_getUniqueInteger(self):
        # getUniqueInteger returns an integer that increments each time you
        # call it.
        one = self.getUniqueInteger()
        self.assertEqual(1, one)
        two = self.getUniqueInteger()
        self.assertEqual(2, two)

    def test_getUniqueString(self):
        # getUniqueString returns the current test name followed by a unique
        # integer.
        name_one = self.getUniqueString()
        self.assertEqual('%s-%d' % (self._testMethodName, 1), name_one)
        name_two = self.getUniqueString()
        self.assertEqual('%s-%d' % (self._testMethodName, 2), name_two)


class TestChangeTestId(TestCase):
    """Tests for change_test_id."""

    def test_change_id(self):
        class FooTestCase(TestCase):
            def test_foo(self):
                pass
        testCase = FooTestCase('test_foo')
        newName = self.getUniqueString()
        change_test_id(testCase, newName)
        self.assertEqual(newName, testCase.id())


def test_suite():
    from unittest import TestLoader
    return TestLoader().loadTestsFromName(__name__)
