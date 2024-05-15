from typing import Dict, TypeVar, Type, Union, Iterable, List
import datetime

from snpseq_metadata.exceptions import SomethingNotRecognizedException

M = TypeVar("M", bound="MetadataModel")
T = TypeVar("T")


class MetadataModel:
    def __eq__(self, other: object) -> bool:
        """
        compare to objects for equality

        This will explicitly omit comparing member attributes "model_object" and "exporter"

        Args:
            other: the object to compare the calling object to

        Returns:
            True if both object are of the same type and all attributes are identical
            False otherwise
        """
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
        """
        instantiate the model object from a json representation

        Should be defined in subclasses

        Args:
            json_obj: a json representation of a MetadataModel subclass instance

        Returns:
            an instance of the MetadataModel subclass represented by the supplied json
        """
        raise NotImplementedError

    def to_json(self) -> Dict:
        """
        represent the object as json

        Returns:
            a json representation of the calling object

        """
        json_obj = {}
        for name, value in vars(self).items():
            if value is not None:
                json_obj[name] = self._item_to_json(value)
        return json_obj

    @classmethod
    def _item_to_json(cls: Type[M], item: T) -> Union[T, Dict, Iterable]:
        """
        return the json representation for a class instance member (recursively)

        Args:
            item: the item to represent as json

        Returns:
            a json representation of the supplied item

        """
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
        """
        return the dict value for a supplied key or raise an exception of the supplied type if
        the key was not in the dict

        Args:
            needle: the dict key
            haystack: the dict
            on_error: the type of a SomethingNotRecognizedException to raise if the key is not
            found in the dict

        Returns:
            the dict value for the supplied key

        """
        try:
            return haystack[needle.lower()]
        except KeyError:
            raise on_error(needle, list(haystack.keys()))
