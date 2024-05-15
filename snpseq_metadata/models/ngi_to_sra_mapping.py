
from typing import List, Type, TypeVar, Tuple, ClassVar


from snpseq_metadata.models.ngi_models.library_design import (
    NGISource,
    NGISourceClasses,
    NGIApplication,
    NGIApplicationClasses,
    NGILibraryKit,
    NGILibraryKitClasses,
)

from snpseq_metadata.models.sra_models.library_design import (
    UnspecifiedLibrary,
    RNASeq,
    SingleCell,
    Epigenetics,
    TargetCaptureExome,
    WGS,
    Metagenomics,
    OLinkExplore,
    SRAObject,
)

A = TypeVar("A", bound="ModelMapper")


class ModelMapper:

    library_mapping: ClassVar[
        List[
            Tuple[
                Tuple[
                    List[Type[NGISource]],
                    List[Type[NGIApplication]],
                    List[Type[NGILibraryKit]]
                ],
                Type[SRAObject]
            ]
        ]
    ] = [
        (
            # other
            (
                [NGISource],
                [NGIApplication],
                [NGILibraryKit],
            ),
            UnspecifiedLibrary.Unspecified,
        ),
        (
            # RNA-seq
            (
                [NGISourceClasses.RNA.TOTAL, NGISourceClasses.RNA.DEPLETED, NGISource],
                [NGIApplicationClasses.RNASEQ],
                [NGILibraryKit],
            ),
            RNASeq.Unspecified,
        ),
        (
            # mRNA-seq
            (
                [NGISourceClasses.RNA.TOTAL, NGISourceClasses.RNA.DEPLETED, NGISource],
                [NGIApplicationClasses.RNASEQ],
                [NGILibraryKitClasses.TRANSCRIPTOMIC.MRNA],
            ),
            RNASeq.MRNA,
        ),
        (
            # totalRNA-seq
            (
                [NGISourceClasses.RNA.TOTAL, NGISourceClasses.RNA.DEPLETED, NGISource],
                [NGIApplicationClasses.RNASEQ],
                [NGILibraryKitClasses.TRANSCRIPTOMIC.TOTAL],
            ),
            RNASeq.Total,
        ),
        (
            # Single-cell
            (
                [NGISourceClasses.WHOLEINPUT.CELLS, NGISource],
                [NGIApplicationClasses.SINGLECELL],
                [NGILibraryKit],
            ),
            SingleCell.Unspecified,
        ),
        (
            # Single-cell
            (
                [NGISourceClasses.WHOLEINPUT.CELLS, NGISource],
                [NGIApplicationClasses.SINGLECELL],
                [NGILibraryKitClasses.TRANSCRIPTOMIC.CHROMIUM],
            ),
            SingleCell.Transcriptomic,
        ),
        (
            # Epigenetics
            (
                [NGISourceClasses.DNA.GENOMIC, NGISourceClasses.IMMUNOPRECIPITATED, NGISource],
                [NGIApplicationClasses.EPIGENETICS],
                [NGILibraryKit],
            ),
            Epigenetics.Unspecified,
        ),
        (
            # ChIP-seq
            (
                [NGISourceClasses.IMMUNOPRECIPITATED, NGISource],
                [NGIApplicationClasses.EPIGENETICS],
                [NGILibraryKitClasses.GENOMIC.WHOLEGENOME],
            ),
            Epigenetics.ChIPSeq,
        ),
        (
            # Bisulfite sequencing
            (
                [NGISourceClasses.DNA.GENOMIC, NGISource],
                [NGIApplicationClasses.EPIGENETICS],
                [NGILibraryKitClasses.METHYLATION.BISULFITE],
            ),
            Epigenetics.Bisulfite,
        ),
        (
            # Target capture
            (
                [NGISourceClasses.DNA.GENOMIC, NGISourceClasses.DNA.HMW, NGISource],
                [NGIApplicationClasses.TARGETSEQ],
                [NGILibraryKit],
            ),
            TargetCaptureExome.Unspecified,
        ),
        (
            # Target capture with Twist exome kits
            (
                [NGISourceClasses.DNA.GENOMIC, NGISourceClasses.DNA.HMW, NGISource],
                [NGIApplicationClasses.TARGETSEQ],
                [NGILibraryKitClasses.GENOMIC.TARGET],
            ),
            TargetCaptureExome.Twist,
        ),
        (
            # WGS sequencing
            (
                [NGISourceClasses.DNA.GENOMIC, NGISource],
                [NGIApplicationClasses.RESEQ, NGIApplicationClasses.DENOVO],
                [NGILibraryKitClasses.GENOMIC.WHOLEGENOME, NGILibraryKit],
            ),
            WGS.Unspecified,
        ),
        (
            # Metagenomics
            (
                [NGISourceClasses.DNA.GENOMIC, NGISource],
                [NGIApplicationClasses.METAGENOMICS],
                [NGILibraryKit],
            ),
            Metagenomics.Unspecified,
        ),
        (
            # Metagenomics
            (
                [NGISourceClasses.DNA.GENOMIC, NGISource],
                [NGIApplicationClasses.METAGENOMICS],
                [NGILibraryKitClasses.GENOMIC.WHOLEGENOME],
            ),
            Metagenomics.Genomic,
        ),
        (
            # Olink Explore
            (
                [NGISourceClasses.WHOLEINPUT.SERUM, NGISource],
                [NGIApplicationClasses.OLINK],
                [NGILibraryKitClasses.PROTEOMIC.OLINKEXPLORE],
            ),
            OLinkExplore.Unspecified,
        )
    ]

    @classmethod
    def map_library(
            cls: Type[A],
            source: NGISource,
            application: NGIApplication,
            library_kit: NGILibraryKit,
    ) -> SRAObject:
        """
        Map a combination of NGISource, NGIApplication and NGILibraryKit objects to the
        corresponding SRAObject as specified in the ModelMapper.library_mapping list

        Args:
            source: a NGISource object
            application: a NGIApplication object
            library_kit: a NGILibraryKit object

        Returns:
            a SRAObject corresponding to the combination of input objects or None if no match was
            found

        """
        for mapping in cls.library_mapping:
            if cls.is_match((
                    source,
                    application,
                    library_kit),
                    mapping[0]
            ):
                return mapping[1]()

    @classmethod
    def is_match(
        cls: Type[A],
        query: Tuple[
            NGISource,
            NGIApplication,
            NGILibraryKit
        ],
        mapping: Tuple[
            List[Type[NGISource]],
            List[Type[NGIApplication]],
            List[Type[NGILibraryKit]]
        ],
    ) -> bool:
        """
        compares a 3-element tuple of objects to a 3-element tuple of lists of object types

        Args:
            query: a tuple of (NGISource, NGIApplication, NGILibraryKit) objects
            mapping: a tuple of ([Type[NGISource]], [Type[NGIApplication]], [Type[NGILibraryKit]])

        Returns:
           True if each of the query objects' type is in the corresponding list of object types
           False otherwise

        """
        return all(
            [
                any(
                    map(
                        lambda x: type(q) is x,
                        m
                    )
                )
                for q, m in zip(query, mapping)
            ]
        )
