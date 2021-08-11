import dataclasses
from typing import ClassVar, Dict, Type, TypeVar, Optional, List, Tuple

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
    LibraryType,
)
from snpseq_metadata.models.sra_models.sample import SRASampleDescriptor

T = TypeVar("T", bound="SRALibrary")
TLS = TypeVar("TLS", TypeLibraryStrategy, TypeLibrarySelection, TypeLibrarySource)


class SRALibrary(SRAMetadataModel):
    model_object_class: ClassVar[Type] = LibraryType

    def __init__(
        self,
        model_object: model_object_class,
        sample: Optional[SRASampleDescriptor] = None,
    ):
        super().__init__(model_object)
        self.sample = sample

    @classmethod
    def object_from_paired(
        cls: Type[T], is_paired: bool
    ) -> LibraryDescriptorType.LibraryLayout:
        if is_paired:
            layout = LibraryDescriptorType.LibraryLayout(
                paired=LibraryDescriptorType.LibraryLayout.Paired()
            )
        else:
            layout = LibraryDescriptorType.LibraryLayout(
                single=LibraryDescriptorType.LibraryLayout.Single()
            )
        return layout

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
        is_paired: bool = True,
    ) -> T:
        xsdlibrary = LibraryDescriptorType(
            library_layout=cls.object_from_paired(is_paired=is_paired),
            library_source=cls.object_from_source(source=source),
            library_selection=cls.object_from_selection(selection=selection),
            library_strategy=cls.object_from_strategy(strategy=strategy),
        )
        model_object = LibraryType(
            design_description=description,
            sample_descriptor=sample.model_object,
            library_descriptor=xsdlibrary,
        )
        return cls(model_object=model_object, sample=sample)

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
                    getattr(self.model_object.library_descriptor, field.name).name,
                )
            )
        manifest.extend(self.sample.to_manifest())
        return manifest
