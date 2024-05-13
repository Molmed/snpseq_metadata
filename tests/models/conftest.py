import datetime
import os
import pytest
import re

from snpseq_metadata.models.lims_models import *
from snpseq_metadata.models.ngi_models import *
from snpseq_metadata.models.sra_models import *
from tests.resources.create_test_data import \
    SnpseqDataExperimentSetObj, \
    SRAExperimentSetObj, \
    SRARunSetObj


def ignore_xml_namespace_attributes(xml_str):
    pattern = r' (xmlns|xsi)\:(xsi|type)=[^\s\>]+'
    return re.sub(pattern, "", xml_str)


@pytest.fixture
def snpseqdata_experiment_set(run_data_csv):
    return SnpseqDataExperimentSetObj.create_from_csv(
        run_data_csv
    )


@pytest.fixture
def sra_experiment_set(run_data_csv):
    return SRAExperimentSetObj.create_from_csv(
        run_data_csv
    )


@pytest.fixture
def sra_run_set(run_data_csv):
    return SRARunSetObj.create_from_csv(
        run_data_csv
    )


@pytest.fixture
def flowcell_id(snpseqdata_experiment_set):
    return snpseqdata_experiment_set.fields["flowcell_id"]


@pytest.fixture
def test_values(snpseqdata_experiment_set, sra_experiment_set, sra_run_set):
    test_values = {}
    test_values.update(snpseqdata_experiment_set.fields)
    test_values.update(sra_experiment_set.fields)
    test_values.update(sra_run_set.fields)
    for sample in \
            snpseqdata_experiment_set.fields["sample_objects"] + \
            sra_experiment_set.fields["sample_objects"] + \
            sra_run_set.fields["sample_objects"]:
        for fqfile in sample.fields.get(
                "sequencing_run_fastq_files", []):
            test_values.update(fqfile.fields)
        test_values.update(sample.fields)

    del test_values["sample_objects"]
    del test_values["sequencing_run_fastq_files"]

    return test_values

#        "study_refname": "this-is-a-project-id",
#        "sample_refname": "this-is-a-sample-id",
#        "experiment_refname": "this-is-a-experiment-alias",
#        "experiment_title": "this-is-an-experiment-title",
#        "sequencing_run_title": "this-is-a-sequencing-run-title",
#        "sequencing_run_alias": "this-is-a-sequencing-run-alias",
#        "run_center": NGIRun.run_center,
#        "center_name": NGIRun.run_center,
#        "filepath": os.path.join("/this", "is", "a", "file.path"),
#        "filetype": "fastq",
#        "checksum_method": "MD5",
#        "checksum": "this-is-a-checksum",
#        "library_description": "this-is-a-library-description",
#        "library_sample_type": "this-is-a-sample-type",
#        "library_application": "this-is-a-library-application",
#        "library_kit": "this-is-a-library-kit",
#        "library_is_paired": True,
#        "library_read_length": "150x2",
#        "library_strategy": "OTHER",
#        "library_source": "OTHER",
#        "library_selection": "other",
#        "platform_model_name": "this-is-a-platform-model-name",
#        "samplesheet": "this-is-the-samplesheet-file",
#        "run_parameters": "this-is-the-run-parameters-file",
#        "flowcell_id": flowcell_id,
#        "runfolder_path": os.path.join("/this", "is", "a", "runfolder", "path"),
#        "runfolder_name": f"{run_date.strftime('%y%m%d')}_A00123_0001_A{flowcell_id}",
#        "run_date": run_date.isoformat(),
#        "container_name": "this-is-a-sequencing-container-name",
#        "attribute_tag": "this-is-an-attribute-tag",
#        "attribute_value": "this-is-an-attribute-value",
#        "attribute_units": "this-is-an-attribute-unit"
#    }


@pytest.fixture
def run_date():
    return datetime.datetime(year=2021, month=8, day=9)


@pytest.fixture
def illumina_model_names():
    return {
        "HiSeq2500 High Output": "HiSeq2500",
        "HiSeq2500 Rapid": "HiSeq2500",
        "HiSeqX": "HiSeqX",
        "MiSeq": "MiSeq",
        "MiSeq Nano": "MiSeq",
        "More than one type of sequencing instrument(FoU only)": None,
        "NovaSeq S1": "NovaSeq",
        "NovaSeq S2": "NovaSeq",
        "NovaSeq S4": "NovaSeq",
        "NovaSeq SP": "NovaSeq",
        "NovaSeq X 10B": "NovaSeqX",
        "NovaSeq X 25B": "NovaSeqX",
        "iSeq": "iSeq",
        "": None,
        None: None,
    }


@pytest.fixture
def illumina_model_prefixes():
    return {
        "Lh": "NovaSeqX",
        "A12": "NovaSeq",
        "m0___": "MiSeq",
        "Fs98756 ": "iSeq",
        "ST-e1%": "HiSeqX",
        "d": "HiSeq2500",
        "sN": "HiSeq",
    }


@pytest.fixture
def illumina_sequencing_platforms(illumina_model_prefixes):
    return list(map(str.lower, illumina_model_prefixes.values()))


# LIMS models


@pytest.fixture
def lims_sample_json(test_values):
    json_obj = {
        "name": test_values["sample_name"],
        "project": test_values["project_id"],
        "sample_id": test_values["sample_id"]
    }
    for attr in filter(
            lambda k: k.startswith("udf_"),
            test_values.keys()
    ):
        json_obj[attr] = test_values[attr]
    return json_obj


@pytest.fixture
def lims_sample_obj(lims_sample_json):
    return LIMSSample(
        sample_name=lims_sample_json["name"],
        sample_id=lims_sample_json["sample_id"],
        project_id=lims_sample_json["project"],
        **{
            k: v
            for k, v in lims_sample_json.items()
            if k not in LIMSSample.non_udf_fields.values()
        },
    )


@pytest.fixture
def lims_sequencing_container_json(test_values, lims_sample_json):
    return {
        "result": {
            "name": test_values["flowcell_id"],
            "samples": [lims_sample_json]
        }
    }


@pytest.fixture
def lims_sequencing_container_obj(lims_sequencing_container_json, lims_sample_obj):
    return LIMSSequencingContainer(
        name=lims_sequencing_container_json["result"]["name"], samples=[lims_sample_obj]
    )


# NGI models


@pytest.fixture
def ngi_experiment_ref_json(test_values, ngi_study_json, ngi_sample_json):
    return {
        "alias": test_values["experiment_alias"],
        "project": ngi_study_json,
        "sample": ngi_sample_json,
    }


@pytest.fixture
def ngi_experiment_ref_obj(test_values, ngi_study_obj, ngi_sample_obj):
    return NGIExperimentRef(
        alias=test_values["experiment_alias"],
        project=ngi_study_obj,
        sample=ngi_sample_obj,
    )


@pytest.fixture
def ngi_experiment_json(
    test_values, ngi_study_json, ngi_illumina_platform_json, ngi_library_json
):
    return {
        "alias": test_values["experiment_alias"],
        "title": test_values["experiment_title"],
        "project": ngi_study_json,
        "platform": ngi_illumina_platform_json,
        "library": ngi_library_json,
    }


@pytest.fixture
def ngi_experiment_obj(
    ngi_experiment_json, ngi_study_obj, ngi_illumina_platform_obj, ngi_library_obj
):
    return NGIExperiment(
        alias=ngi_experiment_json["alias"],
        title=ngi_experiment_json["title"],
        project=ngi_study_obj,
        platform=ngi_illumina_platform_obj,
        library=ngi_library_obj,
    )


@pytest.fixture
def ngi_experiment_set_json(ngi_experiment_json):
    return {"experiments": [ngi_experiment_json]}


@pytest.fixture
def ngi_experiment_set_obj(ngi_experiment_obj):
    return NGIExperimentSet(experiments=[ngi_experiment_obj])


@pytest.fixture
def ngi_fastq_file_json(ngi_result_file_json):
    return ngi_result_file_json


@pytest.fixture
def ngi_fastq_file_obj(ngi_fastq_file_json):
    return NGIFastqFile(
        filepath=ngi_fastq_file_json["filepath"],
        checksum=ngi_fastq_file_json["checksum"],
        checksum_method=ngi_fastq_file_json["checksum_method"],
    )


@pytest.fixture
def ngi_flowcell_json(run_date, ngi_sequencing_run_json, test_values):
    return {
        "sequencing_runs": [ngi_sequencing_run_json],
        "runfolder_path": os.path.join(
            test_values["runfolder_path"], test_values["runfolder_name"]
        ),
        "samplesheet": test_values["samplesheet"],
        "run_parameters": test_values["run_parameters"],
    }


@pytest.fixture
def ngi_flowcell_obj(ngi_flowcell_json, ngi_sequencing_run_obj):
    return NGIFlowcell(
        runfolder_path=ngi_flowcell_json["runfolder_path"],
        samplesheet=os.path.join(
            ngi_flowcell_json["runfolder_path"], ngi_flowcell_json["samplesheet"]
        ),
        run_parameters=os.path.join(
            ngi_flowcell_json["runfolder_path"], ngi_flowcell_json["run_parameters"]
        ),
        sequencing_runs=[ngi_sequencing_run_obj],
    )


@pytest.fixture
def ngi_illumina_platform_json(test_values):
    return {"model_name": test_values["illumina_model_value"]}


@pytest.fixture
def ngi_illumina_platform_obj(ngi_illumina_platform_json):
    return NGIIlluminaSequencingPlatform(
        model_name=ngi_illumina_platform_json["model_name"]
    )


@pytest.fixture
def ngi_library_layout_json(test_values):
    return {
        "is_paired": test_values["read_configuration_paired"],
        "fragment_size": test_values.get("udf_fragment_size"),
        "fragment_upper": test_values.get("udf_fragment_upper"),
        "fragment_lower": test_values.get("udf_fragment_lower"),
        "target_insert_size": test_values.get("udf_insert_size_bp")
    }


@pytest.fixture
def ngi_library_layout_obj(ngi_library_layout_json):
    return NGILibraryLayout(
        **ngi_library_layout_json
    )


@pytest.fixture
def ngi_library_json(test_values, ngi_library_layout_json, ngi_sample_json):
    return {
        "description": test_values["library_description"],
        "sample_type": {
            "description": test_values["experiment_sample_type"],
        },
        "application": {
            "description": test_values["experiment_application"],
        },
        "library_kit": {
            "description": test_values["experiment_library_kit"],
        },
        "layout": ngi_library_layout_json,
        "sample": ngi_sample_json,
        "library_protocol": test_values["experiment_library_kit"]
    }


@pytest.fixture
def ngi_library_obj(ngi_sample_obj, ngi_library_layout_obj, ngi_library_json):
    return NGILibrary(
        sample=ngi_sample_obj,
        description=ngi_library_json["description"],
        sample_type=NGISource.match(ngi_library_json["sample_type"]["description"]),
        application=NGIApplication.match(ngi_library_json["application"]["description"]),
        library_kit=NGILibraryKit.match(ngi_library_json["library_kit"]["description"]),
        layout=ngi_library_layout_obj,
        library_protocol=ngi_library_json["library_protocol"],
    )


@pytest.fixture
def ngi_platform_json(test_values):
    return {"model_name": test_values["experiment_instrument_model_name"]}


@pytest.fixture
def ngi_platform_obj(ngi_platform_json):
    return NGISequencingPlatform(model_name=ngi_platform_json["model_name"])


@pytest.fixture
def ngi_result_file_json(test_values):
    return {
        "filepath": test_values["filepath"],
        "filetype": test_values["filetype"],
        "checksum": test_values["checksum"],
        "checksum_method": test_values["checksum_method"],
    }


@pytest.fixture
def ngi_result_file_obj(ngi_result_file_json):
    return NGIResultFile(
        filepath=ngi_result_file_json["filepath"],
        filetype=ngi_result_file_json["filetype"],
        checksum=ngi_result_file_json["checksum"],
        checksum_method=ngi_result_file_json["checksum_method"],
    )


@pytest.fixture
def ngi_sequencing_run_json(
    test_values,
    ngi_experiment_ref_json,
    ngi_illumina_platform_json,
    ngi_result_file_json,
    ngi_attribute_json
):
    return {
        "run_alias": test_values["sequencing_run_alias"],
        "run_date": test_values["sequencing_run_date"],
        "run_center": test_values["sequencing_run_center"],
        "experiment": ngi_experiment_ref_json,
        "platform": ngi_illumina_platform_json,
        "fastqfiles": [ngi_result_file_json],
        "run_attributes": [ngi_attribute_json]
    }


@pytest.fixture
def ngi_sequencing_run_obj(
    ngi_sequencing_run_json,
    ngi_experiment_ref_obj,
    ngi_illumina_platform_obj,
    ngi_result_file_obj,
    ngi_attribute_obj,
    run_date,
):
    return NGIRun(
        run_alias=ngi_sequencing_run_json["run_alias"],
        experiment=ngi_experiment_ref_obj,
        platform=ngi_illumina_platform_obj,
        run_date=run_date,
        fastqfiles=[ngi_result_file_obj],
        run_attributes=[ngi_attribute_obj]
    )


@pytest.fixture
def ngi_sample_json(test_values):
    return {
        "sample_name": test_values["sample_name"],
        "sample_id": test_values["sample_id"],
        "sample_library_id": test_values["sample_library_id"],
        "sample_library_tag": test_values["sample_library_tag"]
    }


@pytest.fixture
def ngi_sample_obj(ngi_sample_json):
    return NGISampleDescriptor(
        sample_id=ngi_sample_json["sample_id"],
        sample_name=ngi_sample_json["sample_name"],
        sample_library_id=ngi_sample_json["sample_library_id"],
        sample_library_tag=ngi_sample_json["sample_library_tag"]
    )


@pytest.fixture
def ngi_study_json(test_values):
    return {
        "project_id": test_values["project_id"]
    }


@pytest.fixture
def ngi_study_obj(ngi_study_json):
    return NGIStudyRef(project_id=ngi_study_json["project_id"])


@pytest.fixture
def ngi_attribute_json(test_values):
    return {
        "tag": test_values["attribute_tag"],
        "value": test_values["attribute_value"],
        "units": test_values["attribute_units"]}


@pytest.fixture
def ngi_attribute_obj(ngi_attribute_json):
    return NGIAttribute(
        tag=ngi_attribute_json["tag"],
        value=ngi_attribute_json["value"],
        units=ngi_attribute_json["units"])


@pytest.fixture
def ngi_read_label_json(test_values):
    return {
        "label": test_values["index_i7"],
        "read_group_tag": test_values["sample_library_id"]
    }


@pytest.fixture
def ngi_read_label_obj(ngi_read_label_json):
    return NGIReadLabel(
        label=ngi_read_label_json["label"],
        read_group_tag=ngi_read_label_json["read_group_tag"]
    )


@pytest.fixture
def ngi_pool_member_json(ngi_sample_json):
    return ngi_sample_json


@pytest.fixture
def ngi_pool_member_obj(ngi_sample_obj):
    return NGIPoolMember(
        **vars(ngi_sample_obj)
    )


@pytest.fixture
def ngi_pool_json(ngi_sample_json):
    return {
        "samples": [
            ngi_sample_json
            ]
    }


@pytest.fixture
def ngi_pool_obj(ngi_pool_json):
    return NGIPool.from_json(
        json_obj=ngi_pool_json
    )


# SRA models


@pytest.fixture
def sra_experiment_json(
    test_values, sra_study_json, sra_library_json, sra_sequencing_platform_json
):
    return {
        "alias": test_values["experiment_alias"],
        "TITLE": test_values["experiment_title"],
        "STUDY_REF": sra_study_json,
        "DESIGN": sra_library_json,
        "PLATFORM": sra_sequencing_platform_json,
    }


@pytest.fixture
def sra_experiment_obj(
    sra_experiment_json, sra_study_obj, sra_sequencing_platform_obj, sra_library_obj
):
    return SRAExperiment.create_object(
        alias=sra_experiment_json["alias"],
        title=sra_experiment_json["TITLE"],
        study_ref=sra_study_obj,
        platform=sra_sequencing_platform_obj,
        library=sra_library_obj,
    )


@pytest.fixture
def sra_experiment_manifest(
    sra_experiment_json,
    sra_study_manifest,
    sra_sequencing_platform_manifest,
    sra_library_manifest,
):
    return (
        [("NAME", sra_experiment_json["alias"])]
        + sra_study_manifest
        + sra_sequencing_platform_manifest
        + sra_library_manifest
    )


@pytest.fixture
def sra_experiment_tsv(
    sra_experiment_json,
    sra_study_tsv,
    sra_sequencing_platform_tsv,
    sra_library_tsv,
):
    tsv_dict = {
        "library_name": sra_experiment_json["alias"],
    }
    tsv_dict.update(sra_study_tsv[0])
    tsv_dict.update(sra_sequencing_platform_tsv[0])
    tsv_dict.update(sra_library_tsv[0])
    return [tsv_dict]


@pytest.fixture
def sra_experiment_xml(
    sra_experiment_json, sra_study_xml, sra_sequencing_platform_xml, sra_library_xml
):
    return f"""<EXPERIMENT alias="{sra_experiment_json["alias"]}">
      <TITLE>{sra_experiment_json["TITLE"]}</TITLE>
      {sra_study_xml.replace('STUDYREF', 'STUDY_REF')}
      {sra_library_xml.replace("LIBRARYTYPE", "DESIGN")}
      {sra_sequencing_platform_xml.replace("PLATFORMTYPE", "PLATFORM")}
    </EXPERIMENT>"""


@pytest.fixture
def sra_experiment_ref_json(test_values):
    return {"refname": test_values["experiment_alias"]}


@pytest.fixture
def sra_experiment_ref_obj(sra_experiment_ref_json):
    return SRAExperimentRef.create_object(
        experiment_name=sra_experiment_ref_json["refname"]
    )


@pytest.fixture
def sra_experiment_ref_manifest(sra_experiment_ref_json):
    return [("NAME", sra_experiment_ref_json["refname"])]


@pytest.fixture
def sra_experiment_ref_xml(sra_experiment_ref_json):
    # in the run context, the tag name will be EXPERIMENT_REF but when exported as a stand-alone
    # object, it will use the name of the python class, i.e. EXPERIMENTREF
    return f'<EXPERIMENT_REF refname="{sra_experiment_ref_json["refname"]}"/>'


@pytest.fixture
def sra_experiment_set_json(sra_experiment_json):
    return {"EXPERIMENT": [sra_experiment_json]}


@pytest.fixture
def sra_experiment_set_tsv(sra_experiment_tsv):
    return sra_experiment_tsv


@pytest.fixture
def sra_experiment_set_manifest(sra_experiment_manifest):
    return sra_experiment_manifest


@pytest.fixture
def sra_experiment_set_obj(sra_experiment_obj):
    return SRAExperimentSet.create_object(experiments=[sra_experiment_obj])


@pytest.fixture
def sra_experiment_set_xml(sra_experiment_xml):
    return f"""<EXPERIMENT_SET>
  {sra_experiment_xml}
  </EXPERIMENT_SET>"""


@pytest.fixture
def sra_library_layout_json(test_values):
    return {
        "PAIRED": {
            "NOMINAL_LENGTH": test_values.get("udf_insert_size_bp")
        }
    }


@pytest.fixture
def sra_library_layout_tsv(test_values):
    return [{
        "insert_size": test_values.get("udf_insert_size_bp")
        }]


@pytest.fixture
def sra_library_layout_obj(test_values, sra_library_layout_json):
    is_paired = "PAIRED" in sra_library_layout_json
    target_insert_size = sra_library_layout_json.get(
        "PAIRED", {}).get(
        "NOMINAL_LENGTH"
    )

    fragment_size = test_values.get("udf_fragment_size")
    fragment_lower = test_values.get("udf_fragment_lower")
    fragment_upper = test_values.get("udf_fragment_upper")
    return SRALibraryLayout.create_object(
        is_paired=is_paired,
        fragment_size=fragment_size,
        fragment_lower=fragment_lower,
        fragment_upper=fragment_upper,
        target_insert_size=target_insert_size
    )


@pytest.fixture
def sra_library_layout_xml(sra_library_layout_json):
    # in the experiment context, the tag name will be SAMPLE_DESCRIPTOR but when exported as a
    # stand-alone object, it will use the name of the python class, i.e. SAMPLEDESCRIPTORTYPE
    mode = "PAIRED" if "PAIRED" in sra_library_layout_json else "SINGLE"
    len = f" NOMINAL_LENGTH=\"{sra_library_layout_json['PAIRED']['NOMINAL_LENGTH']}\"" \
        if mode == "PAIRED" and "NOMINAL_LENGTH" in sra_library_layout_json["PAIRED"] \
        else ""
    return f"""<LIBRARY_LAYOUT>
            <{mode}{len}/>
        </LIBRARY_LAYOUT>"""


@pytest.fixture
def sra_library_json(test_values, sra_library_layout_json, sra_sample_json):
    return {
        "DESIGN_DESCRIPTION": test_values["library_description"],
        "SAMPLE_DESCRIPTOR": sra_sample_json,
        "LIBRARY_DESCRIPTOR": {
            "LIBRARY_STRATEGY": test_values["experiment_sra_library_strategy"],
            "LIBRARY_SOURCE": test_values["experiment_sra_library_source"],
            "LIBRARY_SELECTION": test_values["experiment_sra_library_selection"],
            "LIBRARY_LAYOUT": sra_library_layout_json,
            "LIBRARY_CONSTRUCTION_PROTOCOL": test_values["experiment_library_kit"]
        },
    }


@pytest.fixture
def sra_library_obj(sra_library_json, sra_library_layout_obj, sra_sample_obj):
    return SRALibrary.create_object(
        sample=sra_sample_obj,
        description=sra_library_json["DESIGN_DESCRIPTION"],
        strategy=sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_STRATEGY"],
        source=sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SOURCE"],
        selection=sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SELECTION"],
        layout=sra_library_layout_obj,
        library_protocol=sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_CONSTRUCTION_PROTOCOL"]
    )


@pytest.fixture
def sra_library_tsv(test_values, sra_library_layout_tsv, sra_sample_tsv):
    tsv = {
        "design_description": test_values["library_description"],
        "library_source": test_values["experiment_sra_library_source"],
        "library_selection": test_values["experiment_sra_library_selection"].upper(),
        "library_strategy": test_values["experiment_sra_library_strategy"],
        "library_layout": "PAIRED",
        "library_construction_protocol": test_values["experiment_library_kit"],
    }
    tsv.update(sra_library_layout_tsv[0])
    tsv.update(sra_sample_tsv[0])
    return [tsv]


@pytest.fixture
def sra_library_manifest(sra_library_json, sra_sample_manifest):
    return (
        [
            ("DESCRIPTION", sra_library_json["DESIGN_DESCRIPTION"]),
        ]
        + [
            (k, v.upper())
            for k, v in sra_library_json["LIBRARY_DESCRIPTOR"].items()
            if k in ["LIBRARY_STRATEGY", "LIBRARY_SOURCE", "LIBRARY_SELECTION"]
        ]
        + sra_sample_manifest
    )


@pytest.fixture
def sra_library_xml(sra_library_json, sra_library_layout_xml, sra_sample_xml):
    return f"""<LIBRARYTYPE>
      <DESIGN_DESCRIPTION>{sra_library_json["DESIGN_DESCRIPTION"]}</DESIGN_DESCRIPTION>
      {sra_sample_xml.replace("SAMPLEDESCRIPTORTYPE", "SAMPLE_DESCRIPTOR")}
      <LIBRARY_DESCRIPTOR>
        <LIBRARY_STRATEGY>{sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_STRATEGY"]}</LIBRARY_STRATEGY>
        <LIBRARY_SOURCE>{sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SOURCE"]}</LIBRARY_SOURCE>
        <LIBRARY_SELECTION>{sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_SELECTION"]}</LIBRARY_SELECTION>
        {sra_library_layout_xml}
        <LIBRARY_CONSTRUCTION_PROTOCOL>{sra_library_json["LIBRARY_DESCRIPTOR"]["LIBRARY_CONSTRUCTION_PROTOCOL"]}</LIBRARY_CONSTRUCTION_PROTOCOL>
      </LIBRARY_DESCRIPTOR>
    </LIBRARYTYPE>"""


@pytest.fixture
def sra_result_file_json(test_values):
    return {
        "filename": test_values["filepath"],
        "filetype": test_values["filetype"],
        "checksum_method": test_values["checksum_method"],
        "checksum": test_values["checksum"],
    }


@pytest.fixture
def sra_result_file_obj(sra_result_file_json):
    return SRAResultFile.create_object(
        filepath=sra_result_file_json["filename"],
        filetype=sra_result_file_json["filetype"],
        checksum_method=sra_result_file_json["checksum_method"],
        checksum=sra_result_file_json["checksum"],
    )


@pytest.fixture
def sra_result_file_xml(sra_result_file_json):
    return f'<FILE filename="{sra_result_file_json["filename"]}" filetype="{sra_result_file_json["filetype"]}" checksum_method="{sra_result_file_json["checksum_method"]}" checksum="{sra_result_file_json["checksum"]}"/>'


@pytest.fixture
def sra_result_file_manifest(sra_result_file_json):
    return [
        (sra_result_file_json["filetype"].upper(), sra_result_file_json["filename"])
    ]


@pytest.fixture
def sra_result_file_tsv(sra_result_file_json):
    return [
        {
            "FileType": sra_result_file_json["filetype"],
            "_file_name": sra_result_file_json["filename"],
            "_file_md5": sra_result_file_json["checksum"],
        }
    ]


@pytest.fixture
def sra_sample_json(test_values):
    return {"refname": test_values["sample_name"]}


@pytest.fixture
def sra_sample_tsv(sra_sample_json):
    return [{"sample": sra_sample_json["refname"]}]


@pytest.fixture
def sra_sample_manifest(sra_sample_json):
    return [("SAMPLE", sra_sample_json["refname"])]


@pytest.fixture
def sra_sample_obj(sra_sample_json):
    return SRASampleDescriptor.create_object(refname=sra_sample_json["refname"])


@pytest.fixture
def sra_sample_xml(sra_sample_json):
    # in the experiment context, the tag name will be SAMPLE_DESCRIPTOR but when exported as a
    # stand-alone object, it will use the name of the python class, i.e. SAMPLEDESCRIPTORTYPE
    return f'<SAMPLEDESCRIPTORTYPE refname="{sra_sample_json["refname"]}"/>'


@pytest.fixture
def sra_sequencing_platform_json(illumina_sequencing_platforms):
    model = SRAIlluminaSequencingPlatform.object_from_name(
        model_name=illumina_sequencing_platforms[0]
    )
    return {"ILLUMINA": {"INSTRUMENT_MODEL": model.value}}


@pytest.fixture
def sra_sequencing_platform_manifest(sra_sequencing_platform_json):
    platform = list(sra_sequencing_platform_json.keys())[0]
    return [
        ("PLATFORM", platform),
        (
            "INSTRUMENT",
            sra_sequencing_platform_json[platform]["INSTRUMENT_MODEL"],
        ),
    ]


@pytest.fixture
def sra_sequencing_platform_obj(illumina_sequencing_platforms):
    return SRAIlluminaSequencingPlatform.create_object(
        model_name=illumina_sequencing_platforms[0]
    )


@pytest.fixture
def sra_sequencing_platform_xml(sra_sequencing_platform_json):
    platform = list(sra_sequencing_platform_json.keys())[0]
    return f"""<PLATFORMTYPE>
      <{platform}>
        <INSTRUMENT_MODEL>{sra_sequencing_platform_json[platform]["INSTRUMENT_MODEL"]}</INSTRUMENT_MODEL>
      </{platform}>
    </PLATFORMTYPE>"""


@pytest.fixture
def sra_sequencing_platform_tsv(sra_sequencing_platform_json):
    platform = list(sra_sequencing_platform_json.keys())[0]
    return [{
        "instrument_model": sra_sequencing_platform_json[platform]["INSTRUMENT_MODEL"]
    }]


@pytest.fixture
def sra_sequencing_run_json(
        test_values, sra_experiment_ref_json, sra_result_file_json, sra_attribute_json):
    return {
        "TITLE": test_values["sequencing_run_alias"],
        "EXPERIMENT_REF": sra_experiment_ref_json,
        "RUN_ATTRIBUTES": {"RUN_ATTRIBUTE": [sra_attribute_json]},
        "DATA_BLOCK": {"FILES": {"FILE": [sra_result_file_json]}},
        "run_date": test_values["sequencing_run_date"],
        "run_center": test_values["sequencing_run_center"],
        "center_name": test_values["sequencing_run_center"],
    }


@pytest.fixture
def sra_sequencing_run_tsv(sra_result_file_tsv):
    return sra_result_file_tsv


@pytest.fixture
def sra_sequencing_run_manifest(sra_result_file_manifest):
    return sra_result_file_manifest


@pytest.fixture
def sra_sequencing_run_obj(
    sra_sequencing_run_json, sra_experiment_obj, sra_result_file_obj, sra_attribute_obj, run_date
):
    return SRARun.create_object(
        run_alias=sra_sequencing_run_json["TITLE"],
        run_center=sra_sequencing_run_json["run_center"],
        run_date=run_date,
        experiment=sra_experiment_obj,
        fastqfiles=[sra_result_file_obj],
        run_attributes=[sra_attribute_obj]
    )


@pytest.fixture
def sra_sequencing_run_xml(
    sra_sequencing_run_json, sra_experiment_ref_xml, sra_result_file_xml, sra_attribute_xml
):
    return f"""<RUN center_name="{sra_sequencing_run_json["center_name"]}" run_date="{sra_sequencing_run_json["run_date"]}" run_center="{sra_sequencing_run_json["run_center"]}">
    <TITLE>{sra_sequencing_run_json["TITLE"]}</TITLE>
    {sra_experiment_ref_xml.replace("EXPERIMENTREF", "EXPERIMENT_REF")}
    <DATA_BLOCK>
      <FILES>
        {sra_result_file_xml}
      </FILES>
    </DATA_BLOCK>
    <RUN_ATTRIBUTES>
    {sra_attribute_xml.replace("ATTRIBUTETYPE", "RUN_ATTRIBUTE")}
    </RUN_ATTRIBUTES>
  </RUN>"""


@pytest.fixture
def sra_sequencing_run_set_json(sra_sequencing_run_json):
    return {"RUN": [sra_sequencing_run_json]}


@pytest.fixture
def sra_sequencing_run_set_tsv(sra_sequencing_run_tsv):
    return sra_sequencing_run_tsv


@pytest.fixture
def sra_sequencing_run_set_manifest(sra_sequencing_run_manifest):
    return sra_sequencing_run_manifest


@pytest.fixture
def sra_sequencing_run_set_obj(sra_sequencing_run_obj):
    return SRARunSet.create_object(runs=[sra_sequencing_run_obj])


@pytest.fixture
def sra_sequencing_run_set_xml(sra_sequencing_run_xml):
    return f"""<RUN_SET>
    {sra_sequencing_run_xml}</RUN_SET>"""


@pytest.fixture
def sra_study_json(test_values):
    return {"refname": test_values["project_id"]}


@pytest.fixture
def sra_study_manifest(sra_study_json):
    return [("STUDY", sra_study_json["refname"])]


@pytest.fixture
def sra_study_tsv(sra_study_json):
    return [{"study": sra_study_json["refname"]}]


@pytest.fixture
def sra_study_obj(sra_study_json):
    return SRAStudyRef.create_object(refname=sra_study_json["refname"])


@pytest.fixture
def sra_study_xml(sra_study_json):
    # in the experiment context, the tag name will be STUDY_REF but when exported as a stand-alone
    # object, it will use the name of the python class, i.e. STUDYREF
    return f'<STUDY_REF refname="{sra_study_json["refname"]}"/>'


@pytest.fixture
def sra_attribute_json(test_values):
    return {
        "TAG": test_values["attribute_tag"],
        "VALUE": test_values["attribute_value"],
        "UNITS": test_values["attribute_units"]
    }


@pytest.fixture
def sra_attribute_manifest(sra_attribute_json):
    return [(
        sra_attribute_json["TAG"].upper(),
        f'{sra_attribute_json["VALUE"]} {sra_attribute_json["UNITS"]}')]


@pytest.fixture
def sra_attribute_obj(sra_attribute_json):
    return SRAAttribute.create_object(
        tag=sra_attribute_json["TAG"],
        value=sra_attribute_json["VALUE"],
        units=sra_attribute_json["UNITS"]
    )


@pytest.fixture
def sra_attribute_xml(sra_attribute_json):
    # in the experiment context, the tag name will be STUDY_REF but when exported as a stand-alone
    # object, it will use the name of the python class, i.e. STUDYREF
    return f"""
<ATTRIBUTETYPE>
<TAG>{sra_attribute_json['TAG']}</TAG>
<VALUE>{sra_attribute_json['VALUE']}</VALUE>
<UNITS>{sra_attribute_json['UNITS']}</UNITS>
</ATTRIBUTETYPE>
"""
