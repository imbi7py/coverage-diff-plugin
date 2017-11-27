import coverage.plugin
import unidiff


class Trace(coverage.plugin.FileTracer):

    def __init__(self, filename):
        self.filename = filename

    def source_filename(self):
        return self.filename


class ReportDiff(coverage.plugin.FileReporter):

    def __init__(self, patch_set, filename):
        self.patch_set = patch_set
        self.filename = filename

    def get_excluded_lines(self):
        import pdb; pdb.set_trace()


class DiffCoveragePlugin(coverage.plugin.CoveragePlugin):

    def __init__(self, patch_set):
        self.patch_set = patch_set

    @classmethod
    def frompath(cls, path):
        with open(path) as f:
            return cls(unidiff.PatchSet(f))

    def file_tracer(self, filename):
        if filename.endswith((".py", ".pyc")):
            return Trace(filename)

    def file_reporter(self, filename):
        if filename.endswith((".py", ".pyc")):
            report = ReportDiff(self.patch_set, filename)
            return report
