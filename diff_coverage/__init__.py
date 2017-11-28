import sys
from ._implementation import DiffCoveragePlugin


def coverage_init(reg, options):
    if options['diff'] == '-':
        reg.add_file_tracer(DiffCoveragePlugin.fromStandardIn(sys.stdin))
    else:
        reg.add_file_tracer(DiffCoveragePlugin.frompath(options['diff']))
