import os

from typing import Dict, TypeVar, Type

from snpseq_metadata.models.ngi_models.metadata_model import NGIMetadataModel

T = TypeVar("T", bound="NGIResultFile")


class NGIResultFile(NGIMetadataModel):
    def __init__(
        self, filepath: str, filetype: str, checksum: str, checksum_method: str = "MD5"
    ) -> None:
        self.filepath = filepath
        self.filetype = filetype
        self.checksum = checksum
        self.checksum_method = checksum_method

    def __eq__(self, other: T) -> bool:
        return (
            os.path.normpath(self.filepath) == os.path.normpath(other.filepath)
            and self.filetype == other.filetype
            and self.checksum == other.checksum
            and self.checksum_method == other.checksum_method
        )

    @classmethod
    def from_json(cls: Type[T], json_obj: Dict[str, str]) -> T:
        return cls(
            filepath=json_obj.get("filepath"),
            filetype=json_obj.get("filetype"),
            checksum=json_obj.get("checksum"),
            checksum_method=json_obj.get("checksum_method"),
        )


class NGIFastqFile(NGIResultFile):
    def __init__(
        self,
        filepath: str,
        filetype: str = "fastq",
        checksum: str = None,
        checksum_method: str = None,
    ) -> None:
        super().__init__(
            filepath=filepath,
            filetype=filetype,
            checksum=checksum,
            checksum_method=checksum_method,
        )
