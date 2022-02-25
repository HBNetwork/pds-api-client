class Forecast(float):
    def __new__(cls, value=0):
        if isinstance(value, str):
            value = cls.parse(value)

        return super().__new__(cls, value)

    @staticmethod
    def parse(value):
        if not value:
            return 0

        if "/" not in value:
            return value

        num, den = value.split('/')
        return float(num) / float(den)

    def __repr__(self):
        type_ = self.__class__.__name__
        number = super().__repr__()
        return f"{type_}({number!r})"


if __name__ == '__main__':
    assert Forecast() == 0.0
    assert Forecast(2.5) == 2.5
    assert Forecast("5/2") == 2.5
    assert Forecast("2.5") == 2.5
    assert Forecast("") == 0

    assert repr(Forecast("2.5")) == "Forecast('2.5')"
    assert repr(Forecast("5/2")) == "Forecast('2.5')"
    assert repr(Forecast("")) == "Forecast('0.0')"
