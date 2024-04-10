
from typing import TypeVar, ClassVar, List, Type, Optional, Dict

from snpseq_metadata.models.lims_models.metadata_model import LIMSMetadataModel

A = TypeVar("A", bound="LIMSLibraryObject")


class LIMSLibraryObject(LIMSMetadataModel):
    
    udf_terms: ClassVar[List[str]]
    library_object_type: ClassVar[str]

    def __init__(self: A, udf: str):
        self.udf = udf

    def __str__(self: A) -> str:
        return self.udf

    def to_json(self: A) -> Dict[str, str]:
        return {
            self.library_object_type: str(self)
        }

    @classmethod
    def from_json(cls: Type[A], json_obj: Dict[str, str]) -> A:
        return cls.match(
            json_obj.get(
                cls.library_object_type
            )
        )

    @classmethod
    def match(
            cls: Type[A],
            udf: Optional[str],
    ) -> Optional[A]:

        matches = list(
            filter(
                lambda m: m is not None,
                map(
                    lambda c: c.match(udf),
                    cls.__subclasses__()
                )
            )
        )

        # if the udf string is empty, don't match anything
        if not udf:
            return None

        # return the first match
        if matches:
            return matches[0]

        # if no subclass matched, check this class for matches. if "udf_terms" is empty, it is the
        # "top" class and nothing has matched so return the class representing e.g. "other"
        if cls.match_terms(udf) or not cls.udf_terms:
            return cls(udf)

        return None

    @classmethod
    def match_terms(
            cls: Type[A],
            udf: Optional[str],
    ) -> bool:
        return udf and (
                udf.lower().replace("rml-", "").replace("-", " ").replace(" ", "") in
                [
                    na.lower().replace("-", " ").replace(" ", "")
                    for na in cls.udf_terms
                ]
        )


class LIMSApplication(LIMSLibraryObject):
    udf_terms = []
    library_object_type = "udf_application"


class LIMSSampleType(LIMSLibraryObject):
    udf_terms = []
    library_object_type = "udf_sample_type"


class LIMSLibraryKit(LIMSLibraryObject):
    udf_terms = []
    library_object_type = "udf_library_preparation_kit"


class LIMSLibraryKitRML(LIMSLibraryObject):
    udf_terms = []
    library_object_type = "udf_rml_kitprotocol"

    @classmethod
    def match(
            cls: Type[A],
            udf: Optional[str],
    ) -> Optional[A]:
        return LIMSLibraryKit.match(udf)


# use an outer class, mainly for overview
class LIMSApplicationClasses:

    class RNASEQ(LIMSApplication):
        udf_terms = [
            "rna-seq",
        ]

    class SINGLECELL(LIMSApplication):
        udf_terms = [
            "single-cell",
        ]

    class EPIGENETICS(LIMSApplication):
        udf_terms = [
            "epigenetics",
            "splat",
        ]

    class TARGETSEQ(LIMSApplication):
        udf_terms = [
            "target re-seq",
        ]

    class DENOVO(LIMSApplication):
        udf_terms = [
            "de novo",
        ]

    class RESEQ(LIMSApplication):
        udf_terms = [
            "wg re-seq",
            "wg re-seq human",
        ]

    class METAGENOMICS(LIMSApplication):
        udf_terms = [
            "metagenomics",
        ]

    class OLINK(LIMSApplication):
        udf_terms = [
            "olink explore",
        ]


# use an outer class, mainly for overview
class LIMSSampleTypeClasses:

    class RNA(LIMSSampleType):
        udf_terms = [""]

        class TOTAL(LIMSSampleType):
            udf_terms = [
                "total RNA"
            ]

        class DEPLETED(LIMSSampleType):
            udf_terms = [
                "rRNA depleted RNA"
            ]

    class DNA(LIMSSampleType):
        udf_terms = [""]

        class GENOMIC(LIMSSampleType):
            udf_terms = [
                "gdna"
            ]

        class HMW(LIMSSampleType):
            udf_terms = [
                "hmw dna"
            ]

        class AMPLICON(LIMSSampleType):
            udf_terms = [
                "amplicon"
            ]

    class IMMUNOPRECIPITATED(LIMSSampleType):
        udf_terms = [
            "chip"
        ]

    class WHOLEINPUT(LIMSSampleType):
        udf_terms = [""]

        class SERUM(LIMSSampleType):
            udf_terms = [
                "serum"
            ]

        class CELLS(LIMSSampleType):
            udf_terms = [
                "cells/nuclei"
            ]


class LIMSLibraryKitClasses:

    class TRANSCRIPTOMIC(LIMSLibraryKit):
        udf_terms = [""]

        class MRNA(LIMSLibraryKit):
            udf_terms = [
                "truseq stranded mrna sample preparation kit",
                "truseq stranded mrna sample preparation kit ht",

            ]

        class TOTAL(LIMSLibraryKit):
            udf_terms = [
                "truseq stranded total rna (ribo-zero tm gold)",
                "truseq stranded total rna (ribo-zero tm gold) ht",
                "truseq stranded with ribo-zero other",
                "illumina stranded total rna ligation (with ribo-zero plus)",
            ]

        class CHROMIUM(LIMSLibraryKit):
            udf_terms = [
                "Chromium single cell 3’ Library prep",
                "Chromium single cell 3\u00b4Library prep",
            ]

    class METHYLATION(LIMSLibraryKit):
        udf_terms = [""]

        class BISULFITE(LIMSLibraryKit):
            udf_terms = [
                "splat",
                "nebnext enzymatic methyl-seq kit",
            ]

    class GENOMIC(LIMSLibraryKit):
        udf_terms = [""]

        class WHOLEGENOME(LIMSLibraryKit):
            udf_terms = [
                "thruplex smarter dna-seq",
                "thruplex smarter dna-seq kit",
                "truseq dna nano sample preparation kit ht",
                "truseq dna nano sample preparation kit lt",
                "truseq dna pcr-free sample preparation kit ht",
                "truseq dna pcr-free sample preparation kit lt",
                "truseq dna pcr-free"
            ]

        class TARGET(LIMSLibraryKit):
            udf_terms = [
                "twist human core exome",
                "twist human comprehensive exome ef lib kit"
            ]

    class PROTEOMIC(LIMSLibraryKit):
        udf_terms = [""]

        class OLINKEXPLORE(LIMSLibraryKit):
            udf_terms = [
                "olink explore 1536",
                "olink explore 3072",
                "olink explore 384",
                "olink explore ht",
                "explore ht",
            ]
