import os
import pytest

from snpseq_metadata.models.sra_models import *


@pytest.fixture
def result_file_json():
    return {
        "filename": os.path.join("/this", "is", "a", "file.path"),
        "filetype": "fastq",
        "checksum_method": "MD5",
        "checksum": "this-is-a-checksum",
    }


@pytest.fixture
def result_file_obj(result_file_json):
    return SRAResultFile.create_object(
        filepath=result_file_json["filename"],
        filetype=result_file_json["filetype"],
        checksum_method=result_file_json["checksum_method"],
        checksum=result_file_json["checksum"],
    )


@pytest.fixture
def result_file_xml(result_file_json):
    return f'<FILE filename="{result_file_json["filename"]}" filetype="{result_file_json["filetype"]}" checksum_method="{result_file_json["checksum_method"]}" checksum="{result_file_json["checksum"]}"/>'


@pytest.fixture
def result_file_manifest(result_file_json):
    return [(result_file_json["filetype"].upper(), result_file_json["filename"])]


@pytest.fixture
def study_json():
    return {"refname": "this-is-a-project-id"}


@pytest.fixture
def study_manifest(study_json):
    return [("STUDY", study_json["refname"])]


@pytest.fixture
def study_obj(study_json):
    return SRAStudyRef.create_object(refname=study_json["refname"])


@pytest.fixture
def study_xml(study_json):
    # in the experiment context, the tag name will be STUDY_REF but when exported as a stand-alone
    # object, it will use the name of the python class, i.e. STUDYREF
    return f'<STUDYREF refname="{study_json["refname"]}"/>'


@pytest.fixture
def sample_json():
    return {"refname": "this-is-a-sample-id"}


@pytest.fixture
def sample_manifest(sample_json):
    return [("SAMPLE", sample_json["refname"])]


@pytest.fixture
def sample_obj(sample_json):
    return SRASampleDescriptor.create_object(refname=sample_json["refname"])


@pytest.fixture
def sample_xml(sample_json):
    # in the experiment context, the tag name will be SAMPLE_DESCRIPTOR but when exported as a
    # stand-alone object, it will use the name of the python class, i.e. SAMPLEDESCRIPTORTYPE
    return f'<SAMPLEDESCRIPTORTYPE refname="{sample_json["refname"]}"/>'


@pytest.fixture
def library_json(sample_json):
    return {
        "DESIGN_DESCRIPTION": f'{sample_json["refname"]} - Application - Source - Kit',
        "SAMPLE_DESCRIPTOR": {"refname": sample_json["refname"]},
        "LIBRARY_DESCRIPTOR": {
            "LIBRARY_STRATEGY": "OTHER",
            "LIBRARY_SOURCE": "OTHER",
            "LIBRARY_SELECTION": "other",
            "LIBRARY_LAYOUT": {"PAIRED": {}},
        },
    }


@pytest.fixture
def library_obj(library_json, sample_obj):
    return SRALibrary.create_object(
        sample=sample_obj,
        description=library_json["DESIGN_DESCRIPTION"],
        strategy=library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_STRATEGY"],
        source=library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SOURCE"],
        selection=library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SELECTION"],
        is_paired=list(library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_LAYOUT"].keys())[0]
        == "PAIRED",
    )


@pytest.fixture
def library_manifest(library_json, sample_manifest):
    return (
        [
            ("DESCRIPTION", library_json["DESIGN_DESCRIPTION"]),
        ]
        + [
            (k, v)
            for k, v in library_json["LIBRARY_DESCRIPTOR"].items()
            if k in ["LIBRARY_STRATEGY", "LIBRARY_SOURCE", "LIBRARY_SELECTION"]
        ]
        + sample_manifest
    )


@pytest.fixture
def library_xml(library_json, sample_xml):
    return f"""<LIBRARYTYPE>
      <DESIGN_DESCRIPTION>{library_json["DESIGN_DESCRIPTION"]}</DESIGN_DESCRIPTION>
      {sample_xml.replace("SAMPLEDESCRIPTORTYPE", "SAMPLE_DESCRIPTOR")}
      <LIBRARY_DESCRIPTOR>
        <LIBRARY_STRATEGY>{library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_STRATEGY"]}</LIBRARY_STRATEGY>
        <LIBRARY_SOURCE>{library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SOURCE"]}</LIBRARY_SOURCE>
        <LIBRARY_SELECTION>{library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SELECTION"]}</LIBRARY_SELECTION>
        <LIBRARY_LAYOUT>
          <{list(library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_LAYOUT"].keys())[0]}/>
        </LIBRARY_LAYOUT>
      </LIBRARY_DESCRIPTOR>
    </LIBRARYTYPE>"""


@pytest.fixture
def sequencing_platform_json(illumina_sequencing_platforms):
    model = SRAIlluminaSequencingPlatform.object_from_name(
        model_name=illumina_sequencing_platforms[0]
    )
    return {"ILLUMINA": {"INSTRUMENT_MODEL": model.value}}


@pytest.fixture
def sequencing_platform_manifest(sequencing_platform_json):
    platform = list(sequencing_platform_json.keys())[0]
    return [
        ("PLATFORM", platform),
        (
            "INSTRUMENT",
            sequencing_platform_json[platform]["INSTRUMENT_MODEL"],
        ),
    ]


@pytest.fixture
def sequencing_platform_obj(illumina_sequencing_platforms):
    return SRAIlluminaSequencingPlatform.create_object(
        model_name=illumina_sequencing_platforms[0]
    )


@pytest.fixture
def sequencing_platform_xml(sequencing_platform_json):
    platform = list(sequencing_platform_json.keys())[0]
    return f"""<PLATFORMTYPE>
      <{platform}>
        <INSTRUMENT_MODEL>{sequencing_platform_json[platform]["INSTRUMENT_MODEL"]}</INSTRUMENT_MODEL>
      </{platform}>
    </PLATFORMTYPE>"""


@pytest.fixture
def illumina_sequencing_platforms():
    return ["novaseq", "miseq", "iseq", "hiseqx", "hiseq2500", "hiseq", "nextseq"]


@pytest.fixture
def experiment_ref_json():
    return {"refname": "this-is-an-experiment-alias"}


@pytest.fixture
def experiment_ref_obj(experiment_ref_json):
    return SRAExperimentRef.create_object(
        experiment_name=experiment_ref_json["refname"]
    )


@pytest.fixture
def experiment_ref_manifest(experiment_ref_json):
    return [("NAME", experiment_ref_json["refname"])]


@pytest.fixture
def experiment_ref_xml(experiment_ref_json):
    # in the run context, the tag name will be EXPERIMENT_REF but when exported as a stand-alone
    # object, it will use the name of the python class, i.e. EXPERIMENTREF
    return f'<EXPERIMENTREF refname="{experiment_ref_json["refname"]}"/>'


@pytest.fixture
def experiment_json(
    experiment_ref_json, study_json, library_json, sequencing_platform_json
):
    return {
        "alias": experiment_ref_json["refname"],
        "TITLE": "this-is-an-experiment-title",
        "STUDY_REF": study_json,
        "DESIGN": library_json,
        "PLATFORM": sequencing_platform_json,
    }


@pytest.fixture
def experiment_obj(experiment_json, study_obj, sequencing_platform_obj, library_obj):
    return SRAExperiment.create_object(
        alias=experiment_json["alias"],
        title=experiment_json["TITLE"],
        study_ref=study_obj,
        platform=sequencing_platform_obj,
        library=library_obj,
    )


@pytest.fixture
def experiment_manifest(
    experiment_json, study_manifest, sequencing_platform_manifest, library_manifest
):
    return (
        [("NAME", experiment_json["alias"])]
        + study_manifest
        + sequencing_platform_manifest
        + library_manifest
    )


@pytest.fixture
def experiment_xml(experiment_json, study_xml, sequencing_platform_xml, library_xml):
    return f"""<EXPERIMENT alias="{experiment_json["alias"]}">
      <TITLE>{experiment_json["TITLE"]}</TITLE>
      {study_xml.replace('STUDYREF', 'STUDY_REF')}
      {library_xml.replace("LIBRARYTYPE", "DESIGN")}
      {sequencing_platform_xml.replace("PLATFORMTYPE", "PLATFORM")}
    </EXPERIMENT>"""
