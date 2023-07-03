import pytest

from snpseq_metadata.models.ngi_models import *


@pytest.fixture
def samplesheet_row(ngi_study_json, ngi_sample_json):
    return {
        "sample_project": ngi_study_json["project_id"],
        "sample_id": f'Sample_{ngi_sample_json["sample_id"]}',
        "sample_name": ngi_sample_json["sample_id"],
    }


@pytest.fixture
def samplesheet_rows():
    rows = []
    for project_id, sample_ids, sample_names in [
        (
            "AB-1234",
            [
                "Sample_AB-1234-SampleA-1",
                "Sample_AB-1234-SampleA-2",
                "Sample_AB-1234-SampleB",
            ],
            []
        ),
        ("CD-5678", ["CD-5678-SampleA-1", "CD-5678-SampleA-2", "CD-5678-SampleB"], []),
        ("EF-9012", ["EF-9012-608"], []),
        (
            "GH-2341",
            [
                "Sample_GH-2341-A",
                "GH-2341-A-1",
                "GH-2341-A-2"
            ],
            [
                "GH-2341-A",
                "GH-2341-A",
                "GH-2341-A"
            ]
        ),
    ]:
        rows.extend(
            [
                {
                    "sample_project": project_id,
                    "sample_id": sample_id,
                    "sample_name": sample_name.replace("Sample_", ""),
                }
                for sample_id, sample_name in
                zip(
                    sample_ids,
                    sample_names
                    if sample_names
                    else [s.replace("Sample_", "") for s in sample_ids]
                )
            ]
        )
    return rows


@pytest.fixture
def samplesheet_experiment_refs(samplesheet_rows):
    experiment_refs = []
    for row in samplesheet_rows:
        project = NGIStudyRef(project_id=row["sample_project"])
        sample = NGISampleDescriptor(
            sample_id=row["sample_name"],
            sample_library_id=row["sample_id"]
        )
        alias = f"{project.project_id}-{sample.sample_alias()}"
        experiment_refs.append(NGIExperimentRef(alias=alias, project=project, sample=sample))
    return experiment_refs
