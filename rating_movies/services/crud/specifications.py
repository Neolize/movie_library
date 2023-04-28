from typing import Union

from rating_movies.exceptions import AbsentParameterError, UnavailableParameterError


class Specification:
    __slots__ = ("params", )

    def __init__(self, *args, **kwargs):
        self.params = args if args else kwargs

    def is_satisfied(self, available_params) -> Union[tuple, dict]:
        """Метод проверяет переданные позиционные или ключевые аргументы
        и возвращает их в виде кортежа или словаря"""
        if not self.params:
            raise AbsentParameterError()

        if not self.are_available_params(available_params=available_params):
            raise UnavailableParameterError(self.params)

        return self.params

    def are_available_params(self, available_params) -> bool:
        available_params = available_params + tuple(f"-{param}" for param in available_params)
        if len(list(filter(lambda parameter: parameter in available_params, self.params))) == len(self.params):
            # если длина списка отфильтрованных параметров равна длине списка переданных аргументов,
            # значит все переданные значения являются допустимыми
            return True
        return False


class SameObjectSpecification(Specification):
    __slots__ = ("__available_params", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__available_params = ("name", "url", "title", "year")

    def is_satisfied(self, available_params=()):
        return super().is_satisfied(available_params=self.__available_params)


class ObjectByParameterSpecification(Specification):
    __slots__ = ("__available_params", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__available_params = ("pk", "id", "url", "title", "world_premiere", "movie")

    def is_satisfied(self, available_params=()):
        return super().is_satisfied(available_params=self.__available_params)


class ObjectsOrderBySpecification(Specification):
    __slots__ = ("__available_params", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__available_params = ("id", "name", "world_premiere", "title")

    def is_satisfied(self, available_params=()):
        return super().is_satisfied(available_params=self.__available_params)


class UniqueValuesSpecification(Specification):
    __slots__ = ("__available_params", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__available_params = ("pk", "country", "year")

    def is_satisfied(self, available_params=()):
        return super().is_satisfied(available_params=self.__available_params)
