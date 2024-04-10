
from typing import Type, TypeVar, Optional, ClassVar, Tuple

from snpseq_metadata.models.metadata_model import MetadataModel

from snpseq_metadata.models.xsdata import (
    TypeLibrarySelection,
    TypeLibrarySource,
    TypeLibraryStrategy,
)

A = TypeVar("A", bound="SRAObject")


class SRAObject(MetadataModel):

    sra_objects: ClassVar[Tuple[TypeLibrarySource, TypeLibraryStrategy, TypeLibrarySelection]]

    def __init__(
            self: A,
            source: Optional[TypeLibrarySource] = None,
            strategy: Optional[TypeLibraryStrategy] = None,
            selection: Optional[TypeLibrarySelection] = None,
    ):
        self.source = source or self.sra_objects[0]
        self.strategy = strategy or self.sra_objects[1]
        self.selection = selection or self.sra_objects[2]

    @classmethod
    def match(
            cls: Type[A],
            source: Optional[TypeLibrarySource],
            strategy: Optional[TypeLibraryStrategy],
            selection: Optional[TypeLibrarySelection],
    ) -> Optional[A]:

        matches = list(
            filter(
                lambda m: m is not None,
                map(
                    lambda c: c.match(source, strategy, selection),
                    cls.__subclasses__()
                )
            )
        )

        # return the first match
        if matches:
            return matches[0]

        if cls.match_terms(source, strategy, selection):
            return cls(source, strategy, selection)

        return None

    @classmethod
    def match_terms(
            cls: Type[A],
            source: Optional[TypeLibrarySource],
            strategy: Optional[TypeLibraryStrategy],
            selection: Optional[TypeLibrarySelection],
    ) -> bool:
        return all(
            [
                isinstance(
                    s,
                    cls.sra_objects[i]
                )
                for i, s in enumerate([source, strategy, selection])
            ]
        )


class UnspecifiedLibrary:

    class Unspecified(SRAObject):
        sra_objects = (
            TypeLibrarySource.OTHER,
            TypeLibraryStrategy.OTHER,
            TypeLibrarySelection.OTHER,
        )


class RNASeq:
    """
    RNA-seq
    """

    class Unspecified(SRAObject):
        sra_objects = (
            TypeLibrarySource.TRANSCRIPTOMIC,
            TypeLibraryStrategy.SS_RNA_SEQ,
            TypeLibrarySelection.UNSPECIFIED,
        )

    class MRNA(SRAObject):
        """
        mRNA-seq
        """
        sra_objects = (
            TypeLibrarySource.TRANSCRIPTOMIC,
            TypeLibraryStrategy.SS_RNA_SEQ,
            TypeLibrarySelection.POLY_A,
        )

    class Total(SRAObject):
        """
        totalRNA-seq
        """
        sra_objects = (
            TypeLibrarySource.TRANSCRIPTOMIC,
            TypeLibraryStrategy.SS_RNA_SEQ,
            TypeLibrarySelection.INVERSE_R_RNA,
        )


class SingleCell:
    """
    Single-cell
    """

    class Unspecified(SRAObject):
        sra_objects = (
            TypeLibrarySource.OTHER,
            TypeLibraryStrategy.OTHER,
            TypeLibrarySelection.UNSPECIFIED
        )

    class Transcriptomic(SRAObject):
        sra_objects = (
            TypeLibrarySource.TRANSCRIPTOMIC_SINGLE_CELL,
            TypeLibraryStrategy.SS_RNA_SEQ,
            TypeLibrarySelection.POLY_A
        )


class Epigenetics:
    """
    Epigenetics
    """

    class Unspecified(SRAObject):
        sra_objects = (
            TypeLibrarySource.OTHER,
            TypeLibraryStrategy.OTHER,
            TypeLibrarySelection.UNSPECIFIED,
        )

    class Bisulfite(SRAObject):
        """
        Bisulfite sequencing
        """
        sra_objects = (
            TypeLibrarySource.GENOMIC,
            TypeLibraryStrategy.BISULFITE_SEQ,
            TypeLibrarySelection.RANDOM,
        )

    class ChIPSeq(SRAObject):
        """
        ChIP-seq
        """
        sra_objects = (
            TypeLibrarySource.GENOMIC,
            TypeLibraryStrategy.CH_IP_SEQ,
            TypeLibrarySelection.CH_IP,
        )


class TargetCaptureExome:
    """
    Target capture
    """

    class Unspecified(SRAObject):
        sra_objects = (
            TypeLibrarySource.GENOMIC,
            TypeLibraryStrategy.TARGETED_CAPTURE,
            TypeLibrarySelection.UNSPECIFIED,
        )

    class Twist(SRAObject):
        """
        Target capture with Twist exome kits
        """
        sra_objects = (
            TypeLibrarySource.GENOMIC,
            TypeLibraryStrategy.TARGETED_CAPTURE,
            TypeLibrarySelection.HYBRID_SELECTION,
        )


class WGS:
    """
    WGS sequencing
    """

    class Unspecified(SRAObject):
        sra_objects = (
            TypeLibrarySource.GENOMIC,
            TypeLibraryStrategy.WGS,
            TypeLibrarySelection.RANDOM,
        )


class Metagenomics:
    """
    Metagenomics
    """

    class Unspecified(SRAObject):
        sra_objects = (
            TypeLibrarySource.METAGENOMIC,
            TypeLibraryStrategy.OTHER,
            TypeLibrarySelection.UNSPECIFIED,
        )

    class Genomic(SRAObject):
        sra_objects = (
            TypeLibrarySource.METAGENOMIC,
            TypeLibraryStrategy.WGS,
            TypeLibrarySelection.RANDOM,
        )


class OLinkExplore:
    """
    Olink Explore
    """

    class Unspecified(SRAObject):
        sra_objects = (
            TypeLibrarySource.OTHER,
            TypeLibraryStrategy.OTHER,
            TypeLibrarySelection.PADLOCK_PROBES_CAPTURE_METHOD,
        )
