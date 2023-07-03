import os

from typing import ClassVar, Optional, TypeVar, Type, List, Tuple

from snpseq_metadata.models.sra_models.metadata_model import SRAMetadataModel
from snpseq_metadata.models.xsdata import Run, FileFiletype, FileChecksumMethod
from snpseq_metadata.exceptions import (
    ChecksumMethodNotRecognizedException,
    FiletypeNotRecognizedException,
)

T = TypeVar("T", bound="SRAResultFile")


class SRAResultFile(SRAMetadataModel):
    model_object_class: ClassVar[Type] = Run.DataBlock.Files.File

    def __eq__(self, other: T) -> bool:
        return (
            os.path.normpath(self.filename)
            == os.path.normpath(other.filename)
            and self.filetype == other.filetype
            and self.checksum == other.checksum
            and self.checksum_method == other.checksum_method
        )

    def __getattr__(self, item: str) -> Optional[str]:
        attr = super().__getattr__(item)
        if attr:
            return attr
        attr = getattr(self.model_object, item)
        if type(attr) in (FileChecksumMethod, FileFiletype):
            return attr.value

    @classmethod
    def object_from_method(cls: Type[T], checksum_method: str) -> FileChecksumMethod:
        method_dict = {method.value.lower(): method for method in FileChecksumMethod}
        return cls._object_from_something(
            checksum_method, method_dict, ChecksumMethodNotRecognizedException
        )

    @classmethod
    def object_from_filetype(cls: Type[T], filetype: str) -> FileFiletype:
        filetype_dict = {filetype.value.lower(): filetype for filetype in FileFiletype}
        return cls._object_from_something(
            filetype, filetype_dict, FiletypeNotRecognizedException
        )

    @classmethod
    def create_object(
        cls: Type[T],
        filepath: str,
        filetype: str,
        checksum: str,
        checksum_method: str = "MD5",
    ) -> T:
        xsd_checksum_method = cls.object_from_method(checksum_method)
        xsd_filetype = cls.object_from_filetype(filetype)
        model_object = Run.DataBlock.Files.File(
            filename=filepath,
            filetype=xsd_filetype,
            checksum=checksum,
            checksum_method=xsd_checksum_method,
        )
        return cls(model_object=model_object)

    def to_manifest(self) -> List[Tuple[str, str]]:
        return [(self.model_object.filetype.name, self.filename)]


class SRAFastqFile(SRAResultFile):
    pass
