class StatsStore:
    _instance = None
    _stats = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StatsStore, cls).__new__(cls)
        return cls._instance

    def set(self, key, value):
        self._stats[key] = value

    def get(self, key, default=None):
        return self._stats.get(key, default)

    def all(self):
        return self._stats

    def clear(self):
        self._stats.clear()

    def increment(self, key):
        current = self._stats.get(key)
        count = 0
        if current is not None:
            count = current

        count += 1
        self._stats[key] = count
