# -*- coding: utf-8 -*-
from unittest import TestResult


class GlyphsTestResult(TestResult):
    """Customised Test Results which are readable to type designers"""
    def addFailure(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info()."""
        # print(dir(test), test.shortDescription())
        title = test.shortDescription()
        self.failures.append((title, (self._exc_info_to_string(err, test))))
        self._mirrorOutput = True

    def _exc_info_to_string(self, err, test):
        """Converts a sys.exc_info()-style tuple of values into a string."""
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        if exctype is test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
            msgLines = value
        else:
            msgLines = value

        if self.buffer:
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            print error
            if output:
                if not output.endswith('\n'):
                    output += '\n'
                msgLines.append(STDOUT_LINE % output)
            if error:
                if not error.endswith('\n'):
                    error += '\n'
                msgLines.append(STDERR_LINE % error)
        return ''.join(map(str, msgLines)).encode('utf-8')
