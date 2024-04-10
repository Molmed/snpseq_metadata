
from snpseq_metadata.models.lims_models.library_design import (
    LIMSApplication,
    LIMSApplicationClasses,
    LIMSSampleType,
    LIMSSampleTypeClasses,
    LIMSLibraryKit,
    LIMSLibraryKitClasses,
)


class TestLIMSLibraryKit:

    mappings = {
        "Chromium single cell 3’ Library prep": LIMSLibraryKitClasses.TRANSCRIPTOMIC.CHROMIUM,
        "Chromium single cell 3\u00b4Library prep": LIMSLibraryKitClasses.TRANSCRIPTOMIC.CHROMIUM,
        "custom": LIMSLibraryKit,
        "Explore HT": LIMSLibraryKitClasses.PROTEOMIC.OLINKEXPLORE,
        "Illumina Stranded Total RNA Ligation(with Ribo-Zero Plus)":
            LIMSLibraryKitClasses.TRANSCRIPTOMIC.TOTAL,
        "NEBNext Enzymatic Methyl-seq kit": LIMSLibraryKitClasses.METHYLATION.BISULFITE,
        "Olink Explore 1536": LIMSLibraryKitClasses.PROTEOMIC.OLINKEXPLORE,
        "Olink Explore 3072": LIMSLibraryKitClasses.PROTEOMIC.OLINKEXPLORE,
        "Olink Explore 384": LIMSLibraryKitClasses.PROTEOMIC.OLINKEXPLORE,
        "RML": LIMSLibraryKit,
        "SPLAT": LIMSLibraryKitClasses.METHYLATION.BISULFITE,
        "ThruPLEX DNA - Seq Kit": LIMSLibraryKit,
        "ThruPLEX SMARTer DNA - seq": LIMSLibraryKitClasses.GENOMIC.WHOLEGENOME,
        "TruSeq DNA Nano Sample Preparation kit HT": LIMSLibraryKitClasses.GENOMIC.WHOLEGENOME,
        "TruSeq DNA PCR - free": LIMSLibraryKitClasses.GENOMIC.WHOLEGENOME,
        "TruSeq DNA PCR - Free Sample Preparation kit HT": LIMSLibraryKitClasses.GENOMIC.WHOLEGENOME,
        "TruSeq stranded mRNA Sample Preparation kit": LIMSLibraryKitClasses.TRANSCRIPTOMIC.MRNA,
        "TruSeq stranded mRNA Sample Preparation kit HT": LIMSLibraryKitClasses.TRANSCRIPTOMIC.MRNA,
        "TruSeq stranded Total RNA(Ribo - zero TM Gold)": LIMSLibraryKitClasses.TRANSCRIPTOMIC.TOTAL,
        "Twist Human Comprehensive Exome EF lib kit": LIMSLibraryKitClasses.GENOMIC.TARGET,
        "Twist Human Core Exome": LIMSLibraryKitClasses.GENOMIC.TARGET,
        "Zymo - Seq RRBS Library Kit": LIMSLibraryKit,
    }

    def test_create_library_kit_object(self):
        for inp, exp in self.mappings.items():
            assert isinstance(
                LIMSLibraryKit.match(
                    inp
                ),
                exp
            ), f"Library kit '{inp}' did not get mapped to type {exp}"


class TestLIMSSampleType:

    mappings = {
        "gDNA": LIMSSampleTypeClasses.DNA.GENOMIC,
        "ChIP": LIMSSampleTypeClasses.IMMUNOPRECIPITATED,
        "Ready-made library": LIMSSampleType,
        "Serum": LIMSSampleTypeClasses.WHOLEINPUT.SERUM,
        "Amplicon": LIMSSampleTypeClasses.DNA.AMPLICON,
        "total RNA": LIMSSampleTypeClasses.RNA.TOTAL,
        "rRNA depleted RNA": LIMSSampleTypeClasses.RNA.DEPLETED,
        "cells / nuclei": LIMSSampleTypeClasses.WHOLEINPUT.CELLS,
        "HMW DNA": LIMSSampleTypeClasses.DNA.HMW,
    }

    def test_create_source_object(self):
        for inp, exp in self.mappings.items():
            assert isinstance(
                LIMSSampleType.match(
                    inp
                ),
                exp
            ), f"Source '{inp}' did not get mapped to type {exp}"


class TestLIMSApplication:

    mappings = {
        "Epigenetics": LIMSApplicationClasses.EPIGENETICS,
        "Metagenomics": LIMSApplicationClasses.METAGENOMICS,
        "Olink Explore": LIMSApplicationClasses.OLINK,
        "Other": LIMSApplication,
        "Ready-made library": LIMSApplication,
        "RML- Epigenetics": LIMSApplicationClasses.EPIGENETICS,
        "RML- Metagenomics": LIMSApplicationClasses.METAGENOMICS,
        "RML- Other": LIMSApplication,
        "RML- RNA-seq": LIMSApplicationClasses.RNASEQ,
        "RML- Single cell": LIMSApplicationClasses.SINGLECELL,
        "RML- Target re-seq": LIMSApplicationClasses.TARGETSEQ,
        "RML- WG re-seq": LIMSApplicationClasses.RESEQ,
        "RML- WG re-seq Human": LIMSApplicationClasses.RESEQ,
        "RNA-seq": LIMSApplicationClasses.RNASEQ,
        "Single cell": LIMSApplicationClasses.SINGLECELL,
        "SPLAT": LIMSApplicationClasses.EPIGENETICS,
        "Target re-seq": LIMSApplicationClasses.TARGETSEQ,
        "WG re-seq": LIMSApplicationClasses.RESEQ,
        "WG re-seq Human": LIMSApplicationClasses.RESEQ,
    }

    def test_create_application_object(self):
        for inp, exp in self.mappings.items():
            assert isinstance(
                LIMSApplication.match(
                    inp
                ),
                exp
            ), f"Application '{inp}' did not get mapped to type {exp}"
