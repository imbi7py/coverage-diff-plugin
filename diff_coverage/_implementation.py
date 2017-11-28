import attr
import collections
import os
import coverage.plugin
import coverage.python
import inspect
import unidiff


class Trace(coverage.plugin.FileTracer):

    def __init__(self, filename):
        self.filename = filename

    def source_filename(self):
        return self.filename


class ReportDiff(coverage.python.PythonFileReporter):

    def __init__(self, lineRegistry, filename, *args):
        super(ReportDiff, self).__init__(filename, *args)
        self._lineRegistry = lineRegistry
        self._linesInDiff = None

    def _getLinesInDiff(self):
        if not self._linesInDiff:
            self._linesInDiff = set(
                self._lineRegistry.linesForFilename(self.filename)
            )
        return self._linesInDiff

    def lines(self):
        return super(ReportDiff, self).lines() & self._getLinesInDiff()

    def excluded_lines(self):
        return super(ReportDiff, self).lines() - self._getLinesInDiff()


@attr.s
class NewLinesInPatchSet(object):
    _patchSet = attr.ib()
    _index = attr.ib()

    @_index.default
    def _(self):
        index = {}
        for patchedFile in self._patchSet:
            for hunk in patchedFile:
                for line in hunk:
                    if line.is_added:
                        index.setdefault(
                            patchedFile.path, [],
                        ).append(line.target_line_no)
        return index

    _namesTrie = attr.ib()

    @_namesTrie.default
    def _(self):
        trie = {}
        for filename in self._index:
            components = filename.split(os.sep)
            if len(components) == 1:
                trie.setdefault(components[0], set()).add(None)
            else:
                backwards = reversed(components)
                childAndParent = collections.deque(
                    [next(backwards), next(backwards)], maxlen=2)
                while True:
                    current, ancestor = childAndParent
                    trie.setdefault(current, set()).add(ancestor)
                    try:
                        childAndParent.append(next(backwards))
                    except StopIteration:
                        break
                trie.setdefault(ancestor, set()).add(None)
        return trie

    def _longestSuffixInIndex(self, filename):
        components = filename.split(os.sep)
        if len(components) == 1:
            if None in self._namesTrie.get(components[0], set()):
                return components[0]
            return ''
        backwards = reversed(components)
        suffix = [next(backwards), next(backwards)]
        while True:
            current, ancestor = suffix[-2:]
            if ancestor not in self._namesTrie.get(current, set()):
                break
            try:
                suffix.append(next(backwards))
            except StopIteration:
                break
        if None in self._namesTrie.get(current, set()):
            return os.sep.join(reversed(suffix[:-1]))
        elif None in self._namesTrie.get(ancestor, set()):
            return os.sep.join(reversed(suffix))
        else:
            return ''

    def linesForFilename(self, filename):
        suffix = self._longestSuffixInIndex(filename)
        if suffix:
            return self._index[suffix]
        return []


class DiffCoveragePlugin(coverage.plugin.CoveragePlugin):
    def __init__(self, lineRegistry):
        self._lineRegistry = lineRegistry

    @classmethod
    def frompath(cls, path):
        with open(path) as f:
            return cls(NewLinesInPatchSet(unidiff.PatchSet(f)))

    @classmethod
    def fromStandardIn(cls, stdin):
        return cls(NewLinesInPatchSet(unidiff.PatchSet(stdin)))

    def file_tracer(self, filename):
        if filename.endswith((".py", ".pyc")):
            return Trace(filename)

    def file_reporter(self, filename):
        if filename.endswith((".py", ".pyc")):
            cov = inspect.stack()[1][0].f_locals['self']
            report = ReportDiff(self._lineRegistry, filename, cov)
            return report
