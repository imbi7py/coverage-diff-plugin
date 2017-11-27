from ._implementation import DiffCoveragePlugin


def coverage_init(reg, options):
    reg.add_file_tracer(DiffCoveragePlugin.frompath(options['diff']))
