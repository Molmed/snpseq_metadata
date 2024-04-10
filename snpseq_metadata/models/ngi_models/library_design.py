
from typing import List, Type, TypeVar, Optional, ClassVar, Dict

from snpseq_metadata.models.ngi_models.metadata_model import NGIMetadataModel

A = TypeVar("A", bound="NGIObject")


class NGIObject(NGIMetadataModel):

    descriptions: ClassVar[List[str]]
    key: ClassVar[str]

    def __init__(self: A, description: str):
        self.description = description

    def __str__(self: A) -> str:
        return self.description

    @classmethod
    def from_json(cls: Type[A], json_obj: Dict[str, str]) -> A:
        return cls.match(
            json_obj.get("description")
        )

    @classmethod
    def match(
            cls: Type[A],
            description: Optional[str],
    ) -> Optional[A]:

        matches = list(
            filter(
                lambda m: m is not None,
                map(
                    lambda c: c.match(description),
                    cls.__subclasses__()
                )
            )
        )

        # return the first match
        if matches:
            return matches[0]

        # if no subclass matched, check this class for matches. if "descriptions" is empty, it is the
        # "top" class and nothing has matched so return the class representing e.g. "other"
        if cls.match_terms(description) or not cls.descriptions:
            return cls(description)

        return None

    @classmethod
    def match_terms(
            cls: Type[A],
            description: Optional[str],
    ) -> bool:
        return description and (
                description.lower().replace("rml-", "").replace("-", " ").replace(" ", "") in
                [
                    na.lower().replace("-", " ").replace(" ", "")
                    for na in cls.descriptions
                ]
        )


class NGIApplication(NGIObject):

    key = "application"
    descriptions = []


class NGISource(NGIObject):

    key = "sample_type"
    descriptions = []


class NGILibraryKit(NGIObject):

    key = "library_kit"
    descriptions = []


class NGIApplicationClasses:

    class RNASEQ(NGIApplication):
        descriptions = [
            "rna-seq",
        ]

    class SINGLECELL(NGIApplication):
        descriptions = [
            "single-cell",
        ]

    class EPIGENETICS(NGIApplication):
        descriptions = [
            "epigenetics",
            "splat",
        ]

    class TARGETSEQ(NGIApplication):
        descriptions = [
            "target re-seq",
        ]

    class DENOVO(NGIApplication):
        descriptions = [
            "de novo",
        ]

    class RESEQ(NGIApplication):
        descriptions = [
            "wg re-seq",
            "wg re-seq human",
        ]

    class METAGENOMICS(NGIApplication):
        descriptions = [
            "metagenomics",
        ]

    class OLINK(NGIApplication):
        descriptions = [
            "olink explore",
        ]


class NGISourceClasses:

    class RNA(NGISource):
        descriptions = [""]

        class TOTAL(NGISource):
            descriptions = [
                "total RNA"
            ]

        class DEPLETED(NGISource):
            descriptions = [
                "rRNA depleted RNA"
            ]

    class DNA(NGISource):
        descriptions = [""]

        class GENOMIC(NGISource):
            descriptions = [
                "gdna"
            ]

        class HMW(NGISource):
            descriptions = [
                "hmw dna"
            ]

        class AMPLICON(NGISource):
            descriptions = [
                "amplicon"
            ]

    class IMMUNOPRECIPITATED(NGISource):
        descriptions = [
            "chip"
        ]

    class WHOLEINPUT(NGISource):
        descriptions = [""]

        class SERUM(NGISource):
            descriptions = [
                "serum"
            ]

        class CELLS(NGISource):
            descriptions = [
                "cells/nuclei"
            ]


class NGILibraryKitClasses:

    class TRANSCRIPTOMIC(NGILibraryKit):
        descriptions = [""]

        class MRNA(NGILibraryKit):
            descriptions = [
                "truseq stranded mrna sample preparation kit",
                "truseq stranded mrna sample preparation kit ht",

            ]

        class TOTAL(NGILibraryKit):
            descriptions = [
                "truseq stranded total rna (ribo-zero tm gold)",
                "truseq stranded total rna (ribo-zero tm gold) ht",
                "truseq stranded with ribo-zero other",
                "illumina stranded total rna ligation (with ribo-zero plus)",
            ]

        class CHROMIUM(NGILibraryKit):
            descriptions = [
                "Chromium single cell 3’ Library prep",
                "Chromium single cell 3\u00b4Library prep",
            ]

    class METHYLATION(NGILibraryKit):
        descriptions = [""]

        class BISULFITE(NGILibraryKit):
            descriptions = [
                "splat",
                "nebnext enzymatic methyl-seq kit",
            ]

    class GENOMIC(NGILibraryKit):
        descriptions = [""]

        class WHOLEGENOME(NGILibraryKit):
            descriptions = [
                "thruplex smarter dna-seq",
                "thruplex smarter dna-seq kit",
                "truseq dna nano sample preparation kit ht",
                "truseq dna nano sample preparation kit lt",
                "truseq dna pcr-free sample preparation kit ht",
                "truseq dna pcr-free sample preparation kit lt",
                "truseq dna pcr-free"
            ]

        class TARGET(NGILibraryKit):
            descriptions = [
                "twist human core exome",
                "twist human comprehensive exome ef lib kit"
            ]

    class PROTEOMIC(NGILibraryKit):
        descriptions = [""]

        class OLINKEXPLORE(NGILibraryKit):
            descriptions = [
                "olink explore 1536",
                "olink explore 3072",
                "olink explore 384",
                "olink explore ht",
                "explore ht",
            ]
