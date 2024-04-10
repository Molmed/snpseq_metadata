
from snpseq_metadata.models.ngi_models.library_design import (
    NGIApplication,
    NGIApplicationClasses,
    NGISource,
    NGISourceClasses,
    NGILibraryKit,
    NGILibraryKitClasses,
)


class TestNGILibraryKit:

    mappings = {
        "Chromium single cell 3’ Library prep": NGILibraryKitClasses.TRANSCRIPTOMIC.CHROMIUM,
        "Chromium single cell 3\u00b4Library prep": NGILibraryKitClasses.TRANSCRIPTOMIC.CHROMIUM,
        "custom": NGILibraryKit,
        "Explore HT": NGILibraryKitClasses.PROTEOMIC.OLINKEXPLORE,
        "Illumina Stranded Total RNA Ligation(with Ribo-Zero Plus)":
            NGILibraryKitClasses.TRANSCRIPTOMIC.TOTAL,
        "NEBNext Enzymatic Methyl-seq kit": NGILibraryKitClasses.METHYLATION.BISULFITE,
        "Olink Explore 1536": NGILibraryKitClasses.PROTEOMIC.OLINKEXPLORE,
        "Olink Explore 3072": NGILibraryKitClasses.PROTEOMIC.OLINKEXPLORE,
        "Olink Explore 384": NGILibraryKitClasses.PROTEOMIC.OLINKEXPLORE,
        "RML": NGILibraryKit,
        "SPLAT": NGILibraryKitClasses.METHYLATION.BISULFITE,
        "ThruPLEX DNA - Seq Kit": NGILibraryKit,
        "ThruPLEX SMARTer DNA - seq": NGILibraryKitClasses.GENOMIC.WHOLEGENOME,
        "TruSeq DNA Nano Sample Preparation kit HT": NGILibraryKitClasses.GENOMIC.WHOLEGENOME,
        "TruSeq DNA PCR - free": NGILibraryKitClasses.GENOMIC.WHOLEGENOME,
        "TruSeq DNA PCR - Free Sample Preparation kit HT": NGILibraryKitClasses.GENOMIC.WHOLEGENOME,
        "TruSeq stranded mRNA Sample Preparation kit": NGILibraryKitClasses.TRANSCRIPTOMIC.MRNA,
        "TruSeq stranded mRNA Sample Preparation kit HT": NGILibraryKitClasses.TRANSCRIPTOMIC.MRNA,
        "TruSeq stranded Total RNA(Ribo - zero TM Gold)": NGILibraryKitClasses.TRANSCRIPTOMIC.TOTAL,
        "Twist Human Comprehensive Exome EF lib kit": NGILibraryKitClasses.GENOMIC.TARGET,
        "Twist Human Core Exome": NGILibraryKitClasses.GENOMIC.TARGET,
        "Zymo - Seq RRBS Library Kit": NGILibraryKit,
    }

    def test_create_library_kit_object(self):
        for inp, exp in self.mappings.items():
            assert isinstance(
                NGILibraryKit.match(
                    inp
                ),
                exp
            ), f"Library kit '{inp}' did not get mapped to type {exp}"


class TestNGISource:

    mappings = {
        "gDNA": NGISourceClasses.DNA.GENOMIC,
        "ChIP": NGISourceClasses.IMMUNOPRECIPITATED,
        "Ready-made library": NGISource,
        "Serum": NGISourceClasses.WHOLEINPUT.SERUM,
        "Amplicon": NGISourceClasses.DNA.AMPLICON,
        "total RNA": NGISourceClasses.RNA.TOTAL,
        "rRNA depleted RNA": NGISourceClasses.RNA.DEPLETED,
        "cells / nuclei": NGISourceClasses.WHOLEINPUT.CELLS,
        "HMW DNA": NGISourceClasses.DNA.HMW,
    }

    def test_create_source_object(self):
        for inp, exp in self.mappings.items():
            assert isinstance(
                NGISource.match(
                    inp
                ),
                exp
            ), f"Source '{inp}' did not get mapped to type {exp}"


class TestNGIApplication:

    mappings = {
        "Epigenetics": NGIApplicationClasses.EPIGENETICS,
        "Metagenomics": NGIApplicationClasses.METAGENOMICS,
        "Olink Explore": NGIApplicationClasses.OLINK,
        "Other": NGIApplication,
        "Ready-made library": NGIApplication,
        "RML- Epigenetics": NGIApplicationClasses.EPIGENETICS,
        "RML- Metagenomics": NGIApplicationClasses.METAGENOMICS,
        "RML- Other": NGIApplication,
        "RML- RNA-seq": NGIApplicationClasses.RNASEQ,
        "RML- Single cell": NGIApplicationClasses.SINGLECELL,
        "RML- Target re-seq": NGIApplicationClasses.TARGETSEQ,
        "RML- WG re-seq": NGIApplicationClasses.RESEQ,
        "RML- WG re-seq Human": NGIApplicationClasses.RESEQ,
        "RNA-seq": NGIApplicationClasses.RNASEQ,
        "Single cell": NGIApplicationClasses.SINGLECELL,
        "SPLAT": NGIApplicationClasses.EPIGENETICS,
        "Target re-seq": NGIApplicationClasses.TARGETSEQ,
        "WG re-seq": NGIApplicationClasses.RESEQ,
        "WG re-seq Human": NGIApplicationClasses.RESEQ,
    }

    def test_create_application_object(self):
        for inp, exp in self.mappings.items():
            assert isinstance(
                NGIApplication.match(
                    inp
                ),
                exp
            ), f"Application '{inp}' did not get mapped to type {exp}"
