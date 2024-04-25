class CustomLineCache:
    _cache = {}

    @classmethod
    def getline(cls, filename, lineno, module_globals=None):
        lines = cls._cache.get(filename, "").splitlines()
        if 1 <= lineno <= len(lines):
            return lines[lineno - 1]
        return ""

    @classmethod
    def cache(cls, filename, contents):
        cls._cache[filename] = contents
