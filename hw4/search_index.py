import re
from collections import Counter


class SearchIndex:
    """Инвертированный индекс.

    _index: dict {слово: set id документов}. Нужен для быстрого поиска слова:
            не надо перебирать документы, а set удобен для пересечения и объединения.
    _docs:  dict {id документа: список его слов}. Нужен, чтобы remove и повторный add
            знали, какие слова были в документе, и не перебирали весь индекс.
    """

    def __init__(self):
        self._index = {}
        self._docs = {}

    def add(self, doc_id, text):
        if doc_id in self._docs:             # такой документ уже был: удаляем старый
            self.remove(doc_id)
        words = re.findall(r'\w+', text.lower())
        self._docs[doc_id] = words
        for word in words:
            self._index.setdefault(word, set()).add(doc_id)

    def remove(self, doc_id):
        words = self._docs.pop(doc_id, [])
        for word in set(words):
            self._index[word].discard(doc_id)
            if not self._index[word]:        # слово больше нигде не встречается
                del self._index[word]

    def search_all(self, *words):
        result = None
        for word in words:
            ids = self._index.get(word.lower(), set())
            if result is None:
                result = set(ids)            # копия, чтобы не испортить индекс
            else:
                result &= ids
        return result or set()

    def search_any(self, *words):
        result = set()
        for word in words:
            result |= self._index.get(word.lower(), set())
        return result

    def top_words(self, n):
        counter = Counter()
        for words in self._docs.values():
            counter.update(words)
        pairs = sorted(counter.items(), key=lambda p: (-p[1], p[0]))
        return pairs[:n]


if __name__ == '__main__':
    idx = SearchIndex()
    idx.add(1, 'Python is a programming language.')
    idx.add(2, 'A dict is a hash table; a set is a hash table too!')
    idx.add(3, 'Python dict and set are fast.')
    assert idx.search_all('python') == {1, 3}
    assert idx.search_all('dict', 'set') == {2, 3}
    assert idx.search_all('python', 'hash') == set()
    assert idx.search_any('language', 'fast') == {1, 3}
    assert idx.search_all('PYTHON') == {1, 3}
    assert idx.search_all('nothing') == set()
    assert idx.top_words(2) == [('a', 5), ('is', 3)]
    idx.remove(1)
    assert idx.search_all('python') == {3}
    assert idx.search_any('language', 'programming') == set()
    idx.add(3, 'Totally new text')
    assert idx.search_all('python') == set()
    assert idx.search_all('new') == {3}

    # свои проверки
    assert 'language' not in idx._index          # слово исчезло из индекса полностью
    found = idx.search_all('new')
    found.add(100)                               # меняем результат
    assert idx.search_all('new') == {3}          # индекс не пострадал
    idx.remove(999)                              # удаление несуществующего: без ошибки
    assert idx.search_all() == set()
    print('Все проверки прошли')
