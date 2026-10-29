class MyDict:
    def __init__(self, size=8):
        self._buckets = [[] for _ in range(size)]
        self._len = 0

    def _find(self, key):
        # Находит корзину ключа и место пары в ней (если ключа нет, место будет None).
        bucket = self._buckets[hash(key) % len(self._buckets)]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                return bucket, i
        return bucket, None

    def _resize(self):
        # Делает корзин в 2 раза больше и раскладывает все пары заново.
        old_pairs = []
        for bucket in self._buckets:
            old_pairs.extend(bucket)

        self._buckets = [[] for _ in range(len(self._buckets) * 2)]
        for key, value in old_pairs:
            self._buckets[hash(key) % len(self._buckets)].append((key, value))

    def __setitem__(self, key, value):
        bucket, i = self._find(key)
        if i is not None:                    # ключ уже есть: меняем значение
            bucket[i] = (key, value)
        else:                                # ключа нет: добавляем пару
            bucket.append((key, value))
            self._len += 1
            if self._len > len(self._buckets) * 2 / 3:
                self._resize()

    def __getitem__(self, key):
        bucket, i = self._find(key)
        if i is None:
            raise KeyError(key)
        return bucket[i][1]

    def __delitem__(self, key):
        bucket, i = self._find(key)
        if i is None:
            raise KeyError(key)
        del bucket[i]
        self._len -= 1

    def __contains__(self, key):
        bucket, i = self._find(key)
        return i is not None

    def __len__(self):
        return self._len

    def get(self, key, default=None):
        bucket, i = self._find(key)
        if i is None:
            return default
        return bucket[i][1]

    def stats(self):
        longest = max(len(bucket) for bucket in self._buckets)
        return (len(self._buckets), self._len, longest)

    def __repr__(self):
        parts = []
        for bucket in self._buckets:
            for key, value in bucket:
                parts.append(f"{key!r}: {value!r}")
        return "MyDict({" + ", ".join(parts) + "})"


class BadKey:
    # Ключ, у которого хеш всегда 42 (для эксперимента).

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return 42

    def __eq__(self, other):
        return self.name == other.name


if __name__ == '__main__':
    d = MyDict()
    for i in range(1000):
        d[f'key{i}'] = i
    assert len(d) == 1000
    assert d['key42'] == 42
    assert 'key7' in d and 'nope' not in d
    d['key42'] = -1
    assert d['key42'] == -1 and len(d) == 1000
    del d['key42']
    assert 'key42' not in d and len(d) == 999
    assert d.get('nope') is None and d.get('nope', 0) == 0
    for bad in (lambda: d['nope'], lambda: d.__delitem__('nope')):
        try:
            bad()
            assert False, 'ожидали KeyError'
        except KeyError:
            pass
    buckets, size, longest = d.stats()
    assert size == 999 and size <= buckets * 2 / 3
    print(d.stats())

    # свои проверки
    small = MyDict(size=1)                  # всё попадает в одну корзину (коллизии)
    for ch in 'abc':
        small[ch] = ch.upper()
    del small['b']
    assert small['a'] == 'A' and small['c'] == 'C' and 'b' not in small

    e = MyDict()
    e['a'] = 1
    assert repr(e) == "MyDict({'a': 1})"

    # эксперимент для вопроса 2
    import time
    for name, keys in (('обычные ключи', [f'key{i}' for i in range(1000)]),
                       ('хеш всегда 42', [BadKey(f'key{i}') for i in range(1000)])):
        t = MyDict()
        start = time.perf_counter()
        for i, key in enumerate(keys):
            t[key] = i
        print(name, t.stats(), f'{time.perf_counter() - start:.4f} сек')


# 1. Номер корзины считается как hash(key) % число_корзин. Когда корзин становится
#    в 2 раза больше, у того же ключа получается другой номер. Если просто скопировать
#    пары на те же места, поиск пойдёт в другую корзину и ключ не найдётся.
#
# 2. Для 1000 строк stats() показывает примерно (2048, 1000, 4): самая длинная корзина
#    короткая. Если хеш всегда 42, будет (2048, 1000, 1000): все ключи в одной корзине,
#    и каждый поиск перебирает всю цепочку. У меня вставка обычных ключей заняла
#    около 0.001 сек, а ключей с хешем 42 около 0.05 сек (в десятки раз дольше).
