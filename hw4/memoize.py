import time


def memoize(func):
    cache = {}                                   # кэш живёт внутри memoize

    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        try:
            hash(key)
        except TypeError:                        # есть нехешируемый аргумент (например, список)
            return func(*args, **kwargs)

        if key in cache:
            wrapper.hits += 1
            return cache[key]

        wrapper.misses += 1
        cache[key] = func(*args, **kwargs)
        return cache[key]

    def cache_clear():
        cache.clear()
        wrapper.hits = 0
        wrapper.misses = 0

    wrapper.hits = 0                             # у функции тоже есть __dict__
    wrapper.misses = 0
    wrapper.cache_clear = cache_clear
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


if __name__ == '__main__':
    calls = []

    def slow_square(x, power=2):
        '''Возводит в степень.'''
        calls.append(x)
        return x ** power

    sq = memoize(slow_square)
    assert sq(3) == 9 and sq(3) == 9 and sq(3, power=3) == 27
    assert calls == [3, 3]
    assert (sq.hits, sq.misses) == (1, 2)
    assert sq.__name__ == 'slow_square' and sq.__doc__ == 'Возводит в степень.'
    total = memoize(sum)
    assert total([1, 2, 3]) == 6 and total([1, 2, 3]) == 6
    assert (total.hits, total.misses) == (0, 0)
    sq.cache_clear()
    assert (sq.hits, sq.misses) == (0, 0)
    sq(3)
    assert calls[-1] == 3

    # свои проверки
    def add(a=0, b=0):
        return a + b

    madd = memoize(add)
    assert madd(a=1, b=2) == 3 and madd(b=2, a=1) == 3   # порядок имён не важен
    assert (madd.hits, madd.misses) == (1, 1)

    # эксперимент с fib(30)
    fast_fib = memoize(fib)                      # вариант A
    start = time.perf_counter()
    fast_fib(30)
    print(f'A: misses = {fast_fib.misses}, {time.perf_counter() - start:.4f} сек')

    fib = memoize(fib)                           # вариант B
    start = time.perf_counter()
    fib(30)
    print(f'B: misses = {fib.misses}, {time.perf_counter() - start:.6f} сек')
    print('Все проверки прошли')


# В варианте A рекурсивный вызов fib(n - 1) ищет имя fib по LEGB: в локальной и
# объемлющей области его нет, в глобальной оно указывает на ОБЫЧНУЮ fib без кэша.
# Кэш сработал только на самом первом вызове (misses = 1), дальше обычная медленная
# рекурсия, у меня около 0.1 сек. В варианте B имя fib переприсвоено на функцию с
# кэшем. Рекурсивный вызов ищет имя в момент выполнения и находит уже её, поэтому
# каждое значение считается один раз (misses = 31) и всё занимает около 0.0001 сек.
