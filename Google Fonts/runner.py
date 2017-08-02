from unittest import TextTestRunner
from result import GlyphsTestResult


class GlyphsTestRunner(TextTestRunner):
    """Simple test runner which is suitable for type designers"""

    description = """Google Fonts QA
~~~~~~~~~~~~~~~

Tests to ensure .glyphs file follow the Google Fonts specification.

The Google Fonts specification:
https://github.com/googlefonts/gf-docs/blob/master/ProjectChecklist.md

Quick start guide for Glyphs:
https://github.com/googlefonts/gf-docs/blob/master/QuickStartGlyphs.md


A fix script which will attempt to update the font to match the
specification can be found in the same directory as this script.
Google Fonts > Fix fonts for GF spec

    """
    def run(self, test):
        result = GlyphsTestResult()
        test(result)
        all_tests = result.testsRun
        failed_tests = len(result.failures)
        passed_tests = all_tests - failed_tests
        result.printErrors()
        run = result.testsRun
        self.stream.writeln(self.description)
        self.stream.writeln('=' * 80)
        self.stream.writeln("TESTS RUN: %s | PASSED: %s | FAILED: %s" % (
            all_tests,
            passed_tests,
            failed_tests
            )
        )
        self.stream.writeln('=' * 80)
        self.stream.writeln('\n')
        
        if passed_tests != all_tests:
            for failed_test in result.failures:
                title, fix_text = failed_test
                self.stream.writeln('=' * 80)
                self.stream.writeln('FAIL: ' + title)
                self.stream.writeln('-' * 80)
                self.stream.writeln(''.join(fix_text))
                self.stream.writeln('\n')
        else:
            self.stream.writeln('All checks passed!')

        return result
