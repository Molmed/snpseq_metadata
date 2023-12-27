import pytest

from snpseq_metadata.models.ngi_models import *


@pytest.fixture
def samplesheet_row(ngi_study_json, ngi_sample_json, test_values):
    return {
        "sample_project": ngi_study_json["project_id"],
        "sample_id": ngi_sample_json["sample_id"],
        "sample_name": ngi_sample_json["sample_name"],
        "index": ngi_sample_json["sample_library_tag"],
        "description": f"LIBRARY_NAME:"
                       f"{test_values['sample_library_name']}"
    }


@pytest.fixture
def samplesheet_rows():
    rows = []
    projects = [
        "AB-1234",
        "CD-5678",
        "EF-9012",
        "GH-2341"
    ]
    project_sample_ids = [
        [
            "Sample_AB-1234-SampleA-1",
            "Sample_AB-1234-SampleA-2",
            "Sample_AB-1234-SampleB",
        ],
        [
            "CD-5678-SampleA-1",
            "CD-5678-SampleA-2",
            "CD-5678-SampleB"
        ],
        [
            "EF-9012-608"
        ],
        [
            "Sample_GH-2341-A",
            "GH-2341-A-1",
            "GH-2341-A-2"
        ]
    ]
    project_sample_names = [
        [],
        [],
        [],
        [
            "GH-2341-A",
            "GH-2341-A",
            "GH-2341-A"
        ]
    ]
    project_sample_library_names = [
        [
            "AB-1234-LibraryA-1",
            "AB-1234-LibraryA-2",
            "AB-1234-LibraryB",
        ],
        [
            "CD-5678-LibraryA-1",
            "CD-5678-LibraryA-2",
            "CD-5678-LibraryB"
        ],
        [
            "EF-9012-Library608"
        ],
        [
            "GH-2341-LibraryA",
            "GH-2341-LibraryA-1",
            "GH-2341-LibraryA-2"
        ]
    ]
    for project, sample_ids, sample_names, sample_library_names in zip(
            projects,
            project_sample_ids,
            project_sample_names,
            project_sample_library_names
    ):
        rows.extend(
            [
                {
                    "sample_project": project,
                    "sample_id": sample_id,
                    "sample_name": sample_name.replace("Sample_", ""),
                    "description": f"LIBRARY_NAME:{sample_library_name}"
                }
                for sample_id, sample_name, sample_library_name in
                zip(
                    sample_ids,
                    sample_names
                    if sample_names
                    else [s.replace("Sample_", "") for s in sample_ids],
                    sample_library_names
                )
            ]
        )
    return rows


@pytest.fixture
def samplesheet_experiment_refs(samplesheet_rows):
    experiment_refs = []
    for row in samplesheet_rows:
        project = NGIStudyRef(
            project_id=row["sample_project"]
        )
        sample_library_name = row.get(
            "description", ":"
        ).split(":")[1]
        sample = NGISampleDescriptor(
            sample_id=row["sample_id"],
            sample_name=row["sample_name"],
            sample_library_id=f'{row["sample_id"]}_{sample_library_name}',
            sample_library_tag=row.get("sample_library_tag", "")
        )
        alias = sample.sample_alias()
        experiment_refs.append(NGIExperimentRef(alias=alias, project=project, sample=sample))
    return experiment_refs
