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
                {
                    "sample_project": project_id,
                    "sample_id": sample_id,
                    "sample_name": sample_id.replace("Sample_", ""),
                }
                for sample_id in sample_ids
            ]
        )
    return rows


@pytest.fixture
def samplesheet_experiment_refs(ngi_flowcell_obj, samplesheet_rows):
    return [
        NGIExperimentRef(
            alias=f"{row['sample_project']}-{row['sample_name']}-{ngi_flowcell_obj.platform.model_name}",
            project=NGIStudyRef(project_id=row["sample_project"]),
            sample=NGISampleDescriptor(sample_id=row["sample_name"]),
        )
        for row in samplesheet_rows
    ]
