import dataclasses
from typing import ClassVar, Dict, Type, TypeVar, Optional, List, Tuple, Union

from snpseq_metadata.exceptions import (
    LibraryStrategyNotRecognizedException,
    LibrarySourceNotRecognizedException,
    LibrarySelectionNotRecognizedException,
)
from snpseq_metadata.models.sra_models.metadata_model import SRAMetadataModel
from snpseq_metadata.models.xsdata import (
    TypeLibraryStrategy,
    TypeLibrarySource,
    TypeLibrarySelection,
    LibraryDescriptorType,
    LibraryType
)
from snpseq_metadata.models.sra_models.sample import SRASampleDescriptor

T = TypeVar("T", bound="SRALibrary")
TLS = TypeVar("TLS", TypeLibraryStrategy, TypeLibrarySelection, TypeLibrarySource)


class SRALibraryLayout(SRAMetadataModel):
    model_object_class: ClassVar[Type] = LibraryDescriptorType.LibraryLayout
    model_object_parent_field: ClassVar[Optional[Tuple[Type, str]]] = (
        LibraryDescriptorType,
        "library_layout"
    )

    def __init__(
            self,
            model_object: model_object_class,
            fragment_size: Optional[int] = None,
            fragment_upper: Optional[int] = None,
            fragment_lower: Optional[int] = None
    ) -> None:
        super().__init__(model_object)
        self.fragment_size = fragment_size
        self.fragment_upper = fragment_upper
        self.fragment_lower = fragment_lower

    @classmethod
    def create_object(
        cls: Type[T],
        is_paired: bool,
        fragment_size: Optional[int] = None,
        fragment_upper: Optional[int] = None,
        fragment_lower: Optional[int] = None,
        target_insert_size: Optional[int] = None
    ) -> T:
        if is_paired:
            model_object = LibraryDescriptorType.LibraryLayout(
                paired=LibraryDescriptorType.LibraryLayout.Paired(
                    nominal_length=target_insert_size
                )
            )
        else:
            model_object = LibraryDescriptorType.LibraryLayout(
                single=""
            )
        return cls(
            model_object=model_object,
            fragment_size=fragment_size,
            fragment_lower=fragment_lower,
            fragment_upper=fragment_upper
        )

    def to_manifest(self) -> List[Tuple[str, str]]:
        return []

    def to_tsv(self) -> List[Dict[str, str]]:
        return [
            {
                "insert_size": str(self.fragment_size)
            }
        ]


class SRALibrary(SRAMetadataModel):
    model_object_class: ClassVar[Type] = LibraryType

    def __init__(self, model_object: model_object_class):
        super().__init__(model_object)

    @classmethod
    def object_from_source(cls: Type[T], source: str) -> TypeLibrarySource:
        return cls._object_from_something(
            needle=source,
            haystack=cls._dict_from_enum(TypeLibrarySource),
            on_error=LibrarySourceNotRecognizedException,
        )

    @classmethod
    def object_from_selection(cls: Type[T], selection: str) -> TypeLibrarySelection:
        return cls._object_from_something(
            needle=selection,
            haystack=cls._dict_from_enum(TypeLibrarySelection),
            on_error=LibrarySelectionNotRecognizedException,
        )

    @classmethod
    def object_from_strategy(cls: Type[T], strategy: str) -> TypeLibraryStrategy:
        return cls._object_from_something(
            needle=strategy,
            haystack=cls._dict_from_enum(TypeLibraryStrategy),
            on_error=LibraryStrategyNotRecognizedException,
        )

    @staticmethod
    def _dict_from_enum(enum_cls: TLS) -> Dict[str, TLS]:
        return {e.value.lower(): e for e in list(enum_cls)}

    @classmethod
    def create_object(
        cls: Type[T],
        sample: SRASampleDescriptor,
        description: str,
        strategy: str,
        source: str,
        selection: str,
        layout: SRALibraryLayout,
        library_protocol: Optional[str] = None,
    ) -> T:
        xsdlibrary = LibraryDescriptorType(
            library_layout=layout.model_object,
            library_source=cls.object_from_source(source=source),
            library_selection=cls.object_from_selection(selection=selection),
            library_strategy=cls.object_from_strategy(strategy=strategy),
            library_construction_protocol=library_protocol,
        )
        model_object = LibraryType(
            design_description=description,
            sample_descriptor=sample.model_object,
            library_descriptor=xsdlibrary,
        )
        return cls(model_object=model_object)

    def to_manifest(self) -> List[Tuple[str, str]]:
        manifest = (
            [("DESCRIPTION", self.model_object.design_description)]
            if self.model_object.design_description
            else []
        )
        manifest_fields = ["library_source", "library_selection", "library_strategy"]

        for field in filter(
            lambda f: f.name in manifest_fields,
            dataclasses.fields(self.model_object.library_descriptor),
        ):
            manifest.append(
                (
                    field.metadata["name"],
                    getattr(self, field.name),
                )
            )
        manifest.extend(self.sample.to_manifest())
        return manifest

    def __getattr__(self, item: str) -> Union[None, str, SRASampleDescriptor]:
        attr = super().__getattr__(item)
        if attr:
            return attr
        if item in (
                "library_source",
                "library_selection",
                "library_strategy",
                "library_layout",
                "library_construction_protocol",
                "insert_size",
        ):
            library_descriptor = getattr(self.model_object, "library_descriptor")
            if item == "insert_size":
                attr = getattr(library_descriptor, "library_layout")
                p = getattr(attr, "paired")
                if p:
                    return p.nominal_length
                else:
                    return None

            attr = getattr(library_descriptor, item)
            if item == "library_construction_protocol":
                return attr
            if item == "library_layout":
                field = next(filter(lambda x: getattr(attr, x.name), dataclasses.fields(attr)))
                return field.metadata["name"]
            return attr.name
        if item == "sample":
            attr = getattr(self.model_object, "sample_descriptor")
            return SRASampleDescriptor.from_model_object(attr)

    def to_tsv(self) -> List[Dict[str, str]]:
        tsv_dict = {
            "design_description": self.description or "",
        }
        for attr in "library_source", \
                    "library_selection", \
                    "library_strategy", \
                    "library_layout", \
                    "library_construction_protocol", \
                    "insert_size":
            tsv_dict[attr] = self.__getattr__(attr)
        tsv_dict.update(
            self.sample.to_tsv()[0]
        )
        return [tsv_dict]
