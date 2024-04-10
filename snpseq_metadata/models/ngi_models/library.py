from typing import Dict, Optional, Type, TypeVar

from snpseq_metadata.models.ngi_models.metadata_model import NGIMetadataModel
from snpseq_metadata.models.ngi_models.sample import NGISampleDescriptor
from snpseq_metadata.models.ngi_models.pool import NGIPool
from snpseq_metadata.models.ngi_models.library_design import \
    NGISource, NGIApplication, NGILibraryKit


T = TypeVar("T", bound="NGILibrary")


class NGILibraryLayout(NGIMetadataModel):

    def __init__(
            self,
            is_paired: bool,
            fragment_size: Optional[int] = None,
            fragment_upper: Optional[int] = None,
            fragment_lower: Optional[int] = None,
            target_insert_size: Optional[int] = None
    ) -> None:
        self.is_paired = is_paired
        self.fragment_size = fragment_size
        self.fragment_upper = fragment_upper
        self.fragment_lower = fragment_lower
        self.target_insert_size = target_insert_size

    @classmethod
    def from_json(cls: Type[T], json_obj: Dict) -> T:
        is_paired = json_obj.get("is_paired")
        fragment_size = json_obj.get("fragment_size")
        fragment_upper = json_obj.get("fragment_upper")
        fragment_lower = json_obj.get("fragment_lower")
        target_insert_size = json_obj.get("target_insert_size")
        return cls(
            is_paired=is_paired,
            fragment_size=fragment_size,
            fragment_upper=fragment_upper,
            fragment_lower=fragment_lower,
            target_insert_size=target_insert_size
        )


class NGILibrary(NGIMetadataModel):
    def __init__(
        self,
        description: str,
        application: NGIApplication,
        sample_type: NGISource,
        library_kit: NGILibraryKit,
        layout: NGILibraryLayout,
        sample: Optional[NGISampleDescriptor] = None,
        pool: Optional[NGIPool] = None
    ) -> None:
        self.sample = sample
        self.pool = pool
        self.description = description
        self.application = application
        self.sample_type = sample_type
        self.library_kit = library_kit
        self.layout = layout

    @classmethod
    def from_json(cls: Type[T], json_obj: Dict) -> T:
        sample = NGISampleDescriptor.from_json(
            json_obj=json_obj.get("sample", {})
        )
        pool = NGIPool.from_json(
            json_obj=json_obj.get("pool")
        )
        description = json_obj.get("description")
        sample_type = NGISource.from_json(json_obj.get("sample_type"))
        application = NGIApplication.from_json(json_obj.get("application"))
        library_kit = NGILibraryKit.from_json(json_obj.get("library_kit"))
        layout = NGILibraryLayout.from_json(json_obj=json_obj.get("layout"))
        return cls(
            description=description,
            sample_type=sample_type,
            application=application,
            library_kit=library_kit,
            layout=layout,
            sample=sample,
            pool=pool
        )
