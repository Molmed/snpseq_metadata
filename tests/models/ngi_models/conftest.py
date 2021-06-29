import datetime
import os
import pytest

from snpseq_metadata.models.ngi_models import *


@pytest.fixture
def experiment_ref_json(study_json, sample_json):
    return {
        "alias": "this-is-a-experiment-alias",
        "project": study_json,
        "sample": sample_json,
    }


@pytest.fixture
def experiment_ref_obj(experiment_ref_json, study_obj, sample_obj):
    return NGIExperimentRef(
        alias=experiment_ref_json["alias"], project=study_obj, sample=sample_obj
    )


@pytest.fixture
def samplesheet_row(study_json, sample_json):
    return {
        "sample_project": study_json["project_id"],
        "sample_id": sample_json["sample_id"],
    }


@pytest.fixture
def samplesheet_rows():
    rows = []
    for project_id, sample_ids in [
        (
            "AB-1234",
            [
                "Sample_AB-1234-SampleA-1",
                "Sample_AB-1234-SampleA-2",
                "Sample_AB-1234-SampleB",
            ],
        ),
        ("CD-5678", ["CD-5678-SampleA-1", "CD-5678-SampleA-2", "CD-5678-SampleB"]),
        ("EF-9012", ["EF-9012-608"]),
    ]:
        rows.extend(
            [
                {"sample_project": project_id, "sample_id": sample_id}
                for sample_id in sample_ids
            ]
        )
    return rows


@pytest.fixture
def samplesheet_experiment_refs(flowcell_obj, samplesheet_rows):
    return [
        NGIExperimentRef(
            alias=f"{row['sample_project']}-{row['sample_id']}-{flowcell_obj.platform.model_name}",
            project=NGIStudyRef(project_id=row["sample_project"]),
            sample=NGISampleDescriptor(sample_id=row["sample_id"]),
        )
        for row in samplesheet_rows
    ]


@pytest.fixture
def experiment_json(experiment_ref_json, illumina_platform_json, library_json):
    return {
        "alias": experiment_ref_json["alias"],
        "title": "this-is-a-experiment-title",
        "project": experiment_ref_json["project"],
        "platform": illumina_platform_json,
        "library": library_json,
    }


@pytest.fixture
def experiment_obj(experiment_json, study_obj, illumina_platform_obj, library_obj):
    return NGIExperiment(
        alias=experiment_json["alias"],
        title=experiment_json["title"],
        project=study_obj,
        platform=illumina_platform_obj,
        library=library_obj,
    )


@pytest.fixture
def experiment_set_json(experiment_json):
    experiments = [experiment_json.copy(), experiment_json.copy()]
    experiments[0]["alias"] = "this-is-another-experiment-title"
    return {"experiments": experiments}


@pytest.fixture
def experiment_set_obj(experiment_obj):
    experiments = [
        NGIExperiment(
            alias="this-is-another-experiment-title",
            title=experiment_obj.title,
            project=experiment_obj.project,
            platform=experiment_obj.platform,
            library=experiment_obj.library,
        ),
        experiment_obj,
    ]
    return NGIExperimentSet(experiments=experiments)


@pytest.fixture
def result_file_json():
    return {
        "filepath": os.path.join("/this", "is", "a", "file.path"),
        "filetype": "this-is-a-file-type",
        "checksum": "this-is-a-checksum",
        "checksum_method": "this-is-a-checksum-method",
    }


@pytest.fixture
def result_file_obj(result_file_json):
    return NGIResultFile(
        filepath=result_file_json["filepath"],
        filetype=result_file_json["filetype"],
        checksum=result_file_json["checksum"],
        checksum_method=result_file_json["checksum_method"],
    )


@pytest.fixture
def fastq_file_json():
    return {
        "filepath": os.path.join("/this", "is", "a", "file.fastq.gz"),
        "filetype": "fastq",
        "checksum": "this-is-a-checksum",
        "checksum_method": "this-is-a-checksum-method",
    }


@pytest.fixture
def fastq_file_obj(fastq_file_json):
    return NGIFastqFile(
        filepath=fastq_file_json["filepath"],
        checksum=fastq_file_json["checksum"],
        checksum_method=fastq_file_json["checksum_method"],
    )


@pytest.fixture
def flowcell_json(run_date, run_json):
    return {
        "sequencing_runs": [run_json, run_json],
        "runfolder_path": os.path.join(
            "/this",
            "is",
            "a",
            "runfolder",
            "path",
            f"{run_date.strftime('%y%m%d')}_A00123_0001_AABC123XYZ",
        ),
        "samplesheet": "this-is-the-samplesheet-file",
        "run_parameters": "this-is-the-run-parameters-file",
    }


@pytest.fixture
def flowcell_obj(flowcell_json, run_obj):
    return NGIFlowcell(
        runfolder_path=flowcell_json["runfolder_path"],
        samplesheet=os.path.join(
            flowcell_json["runfolder_path"], flowcell_json["samplesheet"]
        ),
        run_parameters=os.path.join(
            flowcell_json["runfolder_path"], flowcell_json["run_parameters"]
        ),
        sequencing_runs=[run_obj, run_obj],
    )


@pytest.fixture
def library_json(sample_json):
    return {
        "description": "this-is-a-library-description",
        "sample_type": "this-is-a-sample-type",
        "application": "this-is-a-library-application",
        "library_kit": "this-is-a-library-kit",
        "is_paired": True,
        "sample": sample_json,
    }


@pytest.fixture
def library_obj(sample_obj, library_json):
    return NGILibrary(
        sample=sample_obj,
        description=library_json["description"],
        sample_type=library_json["sample_type"],
        application=library_json["application"],
        library_kit=library_json["library_kit"],
        is_paired=library_json["is_paired"],
    )


@pytest.fixture
def sample_json():
    return {"sample_id": "this-is-a-sample-id"}


@pytest.fixture
def sample_obj(sample_json):
    return NGISampleDescriptor(sample_id=sample_json["sample_id"])


@pytest.fixture
def platform_json():
    return {"model_name": "this-is-a-model-name"}


@pytest.fixture
def platform_obj(platform_json):
    return NGISequencingPlatform(model_name=platform_json["model_name"])


@pytest.fixture
def illumina_platform_json():
    return {"model_name": "this-is-a-illumina-model-name"}


@pytest.fixture
def illumina_platform_obj(illumina_platform_json):
    return NGIIlluminaSequencingPlatform(
        model_name=illumina_platform_json["model_name"]
    )


@pytest.fixture
def model_prefixes():
    return {
        "A12": "NovaSeq",
        "m0___": "MiSeq",
        "Fs98756 ": "iSeq",
        "ST-e1%": "HiSeqX",
        "d": "HiSeq2500",
        "sN": "HiSeq",
    }


@pytest.fixture
def run_json(run_date, experiment_ref_json, illumina_platform_json, fastq_file_json):
    return {
        "run_alias": "this-is-a-run-alias",
        "run_date": run_date.isoformat(" "),
        "run_center": NGIRun.run_center,
        "experiment": experiment_ref_json,
        "platform": illumina_platform_json,
        "fastqfiles": [fastq_file_json, fastq_file_json],
    }


@pytest.fixture
def run_obj(run_json, experiment_ref_obj, illumina_platform_obj, fastq_file_obj):
    return NGIRun(
        run_alias=run_json["run_alias"],
        experiment=experiment_ref_obj,
        platform=illumina_platform_obj,
        run_date=datetime.datetime.fromisoformat(run_json["run_date"]),
        fastqfiles=[fastq_file_obj, fastq_file_obj],
    )


@pytest.fixture
def run_date():
    return datetime.datetime(year=2021, month=6, day=28)


@pytest.fixture
def study_json():
    return {"project_id": "this-is-a-project-id"}


@pytest.fixture
def study_obj(study_json):
    return NGIStudyRef(project_id=study_json["project_id"])
