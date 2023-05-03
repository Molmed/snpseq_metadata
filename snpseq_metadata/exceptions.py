import os
from typing import ClassVar, List, Optional, Type


class MetadataException(Exception):
    def __init__(self, msg: str):
        self.message = msg
        super().__init__(self.message)

    def __str__(self):
        return self.message


class FastqFileLocationNotFoundException(MetadataException):
    def __init__(self, sample_project: str, sample_id: str, search_path: str) -> None:
        self.message = f"No FASTQ file location found in {search_path} for " \
                       f"{sample_project} and {sample_id}"


class RunParametersNotFoundException(MetadataException):
    def __init__(self, runfolder: str) -> None:
        self.message = f"No RunParameters found in {os.path.basename(runfolder)}"


class SampleSheetNotFoundException(MetadataException):
    def __init__(self, runfolder: str) -> None:
        self.message = f"No samplesheet found in {os.path.basename(runfolder)}"


class NoSampleSheetDataFoundException(MetadataException):
    def __init__(self, samplesheet: str) -> None:
        samplesheet_path = os.path.join(
            os.path.basename(os.path.dirname(samplesheet)),
            os.path.basename(samplesheet))
        self.message = f"No data could be parsed from {samplesheet_path}"


class SomethingNotRecognizedException(MetadataException):
    thing: ClassVar[str] = "Needle"
    things: ClassVar[str] = "needles"

    def __init__(self, needle: str, haystack: Optional[List[str]] = None) -> None:
        haystack_str = f" ({', '.join(haystack)})" if haystack else ""
        self.message = f"{self.thing} '{needle}' was not in the list of recognized " \
                       f"{self.things}{haystack_str}"


class InstrumentModelNotRecognizedException(SomethingNotRecognizedException):
    thing: ClassVar[str] = "Instrument model"
    things: ClassVar[str] = "models"


class LibraryStrategyNotRecognizedException(SomethingNotRecognizedException):
    thing: ClassVar[str] = "Library strategy"
    things: ClassVar[str] = "strategies"


class LibrarySourceNotRecognizedException(SomethingNotRecognizedException):
    thing: ClassVar[str] = "Library source"
    things: ClassVar[str] = "sources"


class LibrarySelectionNotRecognizedException(SomethingNotRecognizedException):
    thing: ClassVar[str] = "Library selection"
    things: ClassVar[str] = "selections"


class ChecksumMethodNotRecognizedException(SomethingNotRecognizedException):
    thing: ClassVar[str] = "Checksum method"
    things: ClassVar[str] = "methods"


class FiletypeNotRecognizedException(SomethingNotRecognizedException):
    thing: ClassVar[str] = "File type"
    things: ClassVar[str] = "file types"


class ModelConversionException(MetadataException):
    def __init__(
        self,
        source: Type,
        target: Type,
        reason: Optional[Exception] = None
    ) -> None:
        reason = f", reason: {str(reason)}" if reason is not None else ""
        self.message = f"{source.__name__} could not be converted to a suitable " \
                       f"{target.__name__} object{reason}"
