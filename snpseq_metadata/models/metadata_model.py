from typing import Dict, TypeVar, Type, Union, Iterable
import datetime

from snpseq_metadata.exceptions import SomethingNotRecognizedException

M = TypeVar("M", bound="MetadataModel")
T = TypeVar("T")


class MetadataModel:
    def __eq__(self, other: object) -> bool:
        return type(other) is type(self) and all(
            map(
                lambda k: getattr(other, k, None) == getattr(self, k, None),
                filter(
                    lambda k: k not in ["model_object", "exporter"], vars(self).keys()
                ),
            )
        )

    @classmethod
    def from_json(cls: Type[M], json_obj: Dict) -> M:
        raise NotImplementedError

    def to_json(self) -> Dict:
        json_obj = {}
        for name, value in vars(self).items():
            if value is not None:
                json_obj[name] = self._item_to_json(value)
        return json_obj

    @classmethod
    def _item_to_json(cls: Type[M], item: T) -> Union[T, Dict, Iterable]:
        if isinstance(item, MetadataModel):
            return item.to_json()
        if isinstance(item, dict):
            return {k: cls._item_to_json(v) for k, v in item.items()}
        if isinstance(item, str):
            return item
        if isinstance(item, Iterable):
            return [cls._item_to_json(i) for i in item]
        if isinstance(item, datetime.datetime):
            return item.isoformat()
        return item

    @staticmethod
    def _object_from_something(
        needle: str,
        haystack: Dict[str, T],
        on_error: Type[SomethingNotRecognizedException],
    ) -> T:
        try:
            return haystack[needle.lower()]
        except KeyError:
            raise on_error(needle, list(haystack.keys()))
