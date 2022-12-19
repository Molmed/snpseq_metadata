
from typing import Any, Dict, Iterable, Type

from xsdata.formats.bindings import T
from xsdata.formats.dataclass.parsers import JsonParser
from xsdata.exceptions import ParserError


class CustomJsonParser(JsonParser):
    """
    This extends the default JsonParser in order to override the scoring method used for finding
    the best model dataclass to bind a data dict to. The issue with the original method is that
    it scored an empty list instantiated by default from a missing attribute very high which led to
    e.g. RefObjectType data being bound to the wrong dataclass.

    This version does not score empty lists and includes the proportion of assigned attributes for
    a dataclass in the scoring.
    """
    @staticmethod
    def score_object(obj: Any) -> float:
        """
        Score a binding model instance by its field values types.

        Weights:
            1. None: 0
            2. str: 1
            3. *: 1.5
        """

        if not obj:
            return -1.0

        def score(value: Any) -> float:
            if isinstance(value, str):
                return 1.0

            if value:
                return 1.5

            return 0.0

        return sum(score(getattr(obj, var)) for var in obj.__dict__.keys())

    def bind_best_dataclass(self, data: Dict, classes: Iterable[Type[T]]) -> T:
        """Attempt to bind the given data to one possible models, if more than
        one is successful return the object with the highest score."""
        obj = None
        keys = set(data.keys())
        max_score = -1.0
        for clazz in sorted(classes, key=lambda x: x.__name__):

            if not self.context.class_type.is_model(clazz):
                continue

            if self.context.local_names_match(keys, clazz):
                candidate = self.bind_optional_dataclass(data, clazz)
                score = self.score_object(candidate)
                params = set(clazz().__dict__.keys())

                score += len(keys.intersection(params)) / len(params)
                score -= len(keys.difference(params))
                if score > max_score:
                    max_score = score
                    obj = candidate

        print(f"\n{data}\n\t{obj}\n\t{classes}\n")
        if obj:
            return obj

        raise ParserError(
            f"Failed to bind object with properties({list(data.keys())}) "
            f"to any of the {[cls.__qualname__ for cls in classes]}"
        )
