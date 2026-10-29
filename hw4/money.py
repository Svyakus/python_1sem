class Money:
    __slots__ = ('amount', 'currency')       # других атрибутов не будет

    def __init__(self, amount, currency):
        # self.amount = ... нельзя: наш __setattr__ запрещает запись
        object.__setattr__(self, 'amount', amount)
        object.__setattr__(self, 'currency', currency)

    def __setattr__(self, name, value):
        raise AttributeError('Money нельзя менять')

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self):
        return hash((self.amount, self.currency))   # те же поля, что и в __eq__

    def __add__(self, other):
        if self.currency != other.currency:
            raise ValueError('Разные валюты')
        return Money(self.amount + other.amount, self.currency)   # новый объект

    def __repr__(self):
        return f"Money({self.amount}, {self.currency!r})"


def total_by_currency(payments):
    totals = {}
    for payment in payments:
        if payment.currency in totals:
            totals[payment.currency] = totals[payment.currency] + payment
        else:
            totals[payment.currency] = payment
    return totals


if __name__ == '__main__':
    assert len({Money(100, 'RUB'), Money(100, 'RUB'), Money(100, 'USD')}) == 2
    prices = {Money(100, 'RUB'): 'сто рублей'}
    assert prices[Money(100, 'RUB')] == 'сто рублей'
    assert Money(100, 'RUB') + Money(50, 'RUB') == Money(150, 'RUB')
    for action in (lambda m: setattr(m, 'amount', 5), lambda m: setattr(m, 'extra', 1)):
        try:
            action(Money(1, 'RUB'))
            assert False, 'ожидали AttributeError'
        except AttributeError:
            pass
    try:
        Money(1, 'RUB') + Money(1, 'USD')
        assert False, 'ожидали ValueError'
    except ValueError:
        pass
    pays = [Money(100, 'RUB'), Money(5, 'USD'), Money(250, 'RUB')]
    assert total_by_currency(pays) == {'RUB': Money(350, 'RUB'), 'USD': Money(5, 'USD')}

    # свои проверки
    assert repr(Money(1500, 'RUB')) == "Money(1500, 'RUB')"
    assert Money(1, 'RUB') != 1                  # другой тип: просто не равны
    assert total_by_currency([]) == {}
    print('Все проверки прошли')


# Если бы поля можно было менять, хеш объекта менялся бы, а сам объект оставался бы
# в старой корзине множества или словаря. Как в лекции с Point: p = Point(1, 2),
# visited = {p}, потом p.x = 100. После этого `p in visited` даёт False (ищем по
# новому хешу), а `p in list(visited)` даёт True (объект на месте, но найти его
# нельзя). Поэтому Money неизменяем.
