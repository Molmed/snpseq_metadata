from typing import List, Type, TypeVar, Union, Optional

from snpseq_metadata.models.xsdata import (
    TypeLibrarySelection,
    TypeLibrarySource,
    TypeLibraryStrategy,
)

T = TypeVar("T", bound="ApplicationSampleTypeMapping")


class ApplicationSampleTypeMapping:
    """
    The ApplicationSampleTypeMapping is a base class that provides functionality for picking the
    combination of SRA library selection, source and strategy corresponding to a combination of
    NGI application, sample type and library prep. Only the create_object method on this base class
    needs to be called. The base class will query its subclasses for a suitable match.
    """

    ngi_application: Union[List[str], str]
    ngi_sample_type: Union[List[str], str]
    ngi_sample_prep_kit: Union[List[str], str]

    sra_library_strategy: TypeLibraryStrategy
    sra_library_source: TypeLibrarySource
    sra_library_selection: TypeLibrarySelection

    @classmethod
    def create_object(
        cls: Type[T], application: str, sample_type: str, sample_prep_kit: str
    ) -> Type[T]:
        """
        Class method that given a combination of application, sample type and sample prep kit
        returns a corresponding ApplicationSampleTypeMapping class which contains the appropriate
        NGI-to-SRA mapping for library source, library strategy and library selection.

        :param application: the sample application
        :param sample_type: the sample type
        :param sample_prep_kit: the prep kit used to construct the library
        :return: a ApplicationSampleTypeMapping class corresponding to the supplied combination of
        parameters or the UnspecifiedLibrary class if nothing could be matched
        """
        return (
            cls.match_info_to_class(
                application=application,
                sample_type=sample_type,
                sample_prep_kit=sample_prep_kit,
            )
            or UnspecifiedLibrary
        )

    @classmethod
    def match_info_to_class(
        cls: Type[T], application: str, sample_type: str, sample_prep_kit: str
    ) -> Type[T]:
        """
        Class method that given a combination of application, sample type and sample prep kit
        returns a corresponding ApplicationSampleTypeMapping class which contains the appropriate
        NGI-to-SRA mapping for library source, library strategy and library selection.

        :param application: the sample application
        :param sample_type: the sample type
        :param sample_prep_kit: the prep kit used to construct the library
        :return: a ApplicationSampleTypeMapping class corresponding to the supplied combination of
        parameters or None if nothing could be matched
        """
        # we will only compare the actual values if this class does not have any subclasses
        if not cls.__subclasses__():
            return (
                cls
                if all(
                    [
                        cls._is_match(cls_value, other_value)
                        for cls_value, other_value in [
                            (cls.ngi_application, application),
                            (cls.ngi_sample_type, sample_type),
                            (cls.ngi_sample_prep_kit, sample_prep_kit),
                        ]
                    ]
                )
                else None
            )
        # else, the subclasses will be checked and if a match is found, that subclass will be
        # returned
        cls_matches = list(
            filter(
                lambda c: c is not None,
                [
                    subclass.match_info_to_class(
                        application=application,
                        sample_type=sample_type,
                        sample_prep_kit=sample_prep_kit,
                    )
                    for subclass in cls.__subclasses__()
                ],
            )
        )
        return cls_matches[0] if cls_matches else None

    @staticmethod
    def _is_match(cls_value: Union[str, List[str]], other_value: Optional[str]) -> bool:
        return other_value is not None and (
            other_value.lower() in cls_value
            if type(cls_value) == list
            else other_value.lower() == cls_value
        )


class UnspecifiedLibrary(ApplicationSampleTypeMapping):

    ngi_application = None
    ngi_sample_type = None
    ngi_sample_prep_kit = None

    sra_library_strategy = TypeLibraryStrategy.OTHER
    sra_library_source = TypeLibrarySource.OTHER
    sra_library_selection = TypeLibrarySelection.OTHER


class RNASeqApplication(ApplicationSampleTypeMapping):
    """
    RNA-seq
    """

    ngi_application = "rna-seq"
    ngi_sample_type = "total rna"

    sra_library_strategy = TypeLibraryStrategy.SS_RNA_SEQ
    sra_library_source = TypeLibrarySource.TRANSCRIPTOMIC


class RNASeqKitMRNA(RNASeqApplication):
    """
    mRNA-seq
    """

    ngi_sample_prep_kit = [
        "truseq stranded mrna sample preparation kit",
        "truseq stranded mrna sample preparation kit ht",
    ]

    sra_library_selection = TypeLibrarySelection.POLY_A


class RNASeqKitTotalRNA(RNASeqApplication):
    """
    totalRNA-seq
    """

    ngi_sample_prep_kit = [
        "truseq stranded total rna (ribo-zero tm gold)",
        "truseq stranded total rna (ribo-zero tm gold) ht",
        "truseq stranded with ribo-zero other",
        "illumina stranded total rna ligation (with ribo-zero plus)",
    ]

    sra_library_selection = TypeLibrarySelection.INVERSE_R_RNA


class SingleCellApplication(ApplicationSampleTypeMapping):
    """
    Single-cell
    """

    ngi_application = "single-cell"
    ngi_sample_type = "cells/nuclei"
    ngi_sample_prep_kit = "Chromium single cell 3’ Library prep"

    sra_library_strategy = TypeLibraryStrategy.SS_RNA_SEQ
    sra_library_source = TypeLibrarySource.TRANSCRIPTOMIC_SINGLE_CELL
    sra_library_selection = TypeLibrarySelection.POLY_A


class Bisulphite(ApplicationSampleTypeMapping):
    """
    Bisulphite sequencing
    """

    ngi_application = "epigenetics"
    ngi_sample_type = "gdna"
    ngi_sample_prep_kit = ["splat", "nebnext enzymatic methyl-seq kit"]

    sra_library_strategy = TypeLibraryStrategy.BISULFITE_SEQ
    sra_library_source = TypeLibrarySource.GENOMIC
    sra_library_selection = TypeLibrarySelection.RANDOM


class ChIPSeq(ApplicationSampleTypeMapping):
    """
    ChIP-seq
    """

    ngi_application = "epigenetics"
    ngi_sample_type = "chip"
    ngi_sample_prep_kit = ["thruplex smarter dna-seq"]

    sra_library_strategy = TypeLibraryStrategy.CH_IP_SEQ
    sra_library_source = TypeLibrarySource.GENOMIC
    sra_library_selection = TypeLibrarySelection.CH_IP


class TargetCaptureExome(ApplicationSampleTypeMapping):
    """
    Target capture
    """

    ngi_application = "target re-seq"
    ngi_sample_type = "gdna"
    ngi_sample_prep_kit = ["twist human core exome"]

    sra_library_strategy = TypeLibraryStrategy.TARGETED_CAPTURE
    sra_library_source = TypeLibrarySource.GENOMIC
    sra_library_selection = TypeLibrarySelection.OTHER


class WGSDeNovo(ApplicationSampleTypeMapping):
    """
    De novo sequencing
    """

    ngi_application = "de novo"
    ngi_sample_type = "gdna"
    ngi_sample_prep_kit = ["truseq dna nano sample preparation kit lt"]

    sra_library_strategy = TypeLibraryStrategy.WGS
    sra_library_source = TypeLibrarySource.GENOMIC
    sra_library_selection = TypeLibrarySelection.RANDOM


class WGSReSeq(ApplicationSampleTypeMapping):
    """
    WGS re-seq
    """

    ngi_application = ["wg re-seq", "wg re-seq human"]
    ngi_sample_type = "gdna"
    ngi_sample_prep_kit = [
        "thruplex smarter dna-seq",
        "thruplex smarter dna-seq kit",
        "truseq dna nano sample preparation kit ht",
        "truseq dna nano sample preparation kit lt",
        "truseq dna pcr-free sample preparation kit ht",
        "truseq dna pcr-free sample preparation kit lt",
    ]

    sra_library_strategy = TypeLibraryStrategy.WGS
    sra_library_source = TypeLibrarySource.GENOMIC
    sra_library_selection = TypeLibrarySelection.RANDOM


class OLinkExplore(ApplicationSampleTypeMapping):
    """
    Olink Explore
    """

    ngi_application = ["olink explore", "olink explore 1536"]
    ngi_sample_type = ["plasma", "serum", "ready-made library"]
    ngi_sample_prep_kit = ["olink explore 1536", "explore 1536"]

    sra_library_strategy = TypeLibraryStrategy.OTHER
    sra_library_source = TypeLibrarySource.OTHER
    sra_library_selection = TypeLibrarySelection.UNSPECIFIED


class ReadyMadeLibrary(ApplicationSampleTypeMapping):
    """
    Ready-made library
    """

    ngi_sample_type = "ready-made library"
    ngi_application = ["ready-made library", "rml-"]

    sra_library_strategy = TypeLibraryStrategy.OTHER
    sra_library_source = TypeLibrarySource.OTHER
    sra_library_selection = TypeLibrarySelection.UNSPECIFIED

    @classmethod
    def match_info_to_class(
        cls: Type[T], application: str, sample_type: str, sample_prep_kit: str
    ) -> Type[T]:
        """
        Method overriding the parent's class method in order to allow more fuzzy matching against
        RML applications
        """
        cls_application = (
            cls.ngi_application
            if type(cls.ngi_application) == list
            else [cls.ngi_application]
        )
        if cls._is_match(cls.ngi_sample_type, sample_type) and any(
            map(application.lower().startswith, cls_application)
        ):
            return cls
