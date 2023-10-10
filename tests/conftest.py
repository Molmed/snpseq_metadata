import gzip
import json
import datetime
import os
import pytest
import shutil
import subprocess


def pytest_sessionstart(session):
    create_test_data_script = os.path.join(
        "create_test_data.py"
    )
    run_data_spec = os.path.join(
        "sample_data",
        "run_data_XYZ321XY.csv"
    )
    export_dir = os.path.join(
        "tests",
        "resources",
        "export"
    )
    try:
        shutil.rmtree(export_dir)
    except FileNotFoundError:
        pass
    subprocess.check_call(
        [
            "python",
            create_test_data_script,
            run_data_spec
        ],
        cwd=os.path.join(
            "tests",
            "resources")
    )


def parse_json(json_file):
    with open(json_file, "r") as fh:
        return json.load(fh)


def parse_xml(xml_file):
    with open(xml_file, "r") as fh:
        return "".join([line for line in fh])


@pytest.fixture
def test_resources_path():
    return os.path.join("tests", "resources", "export")


@pytest.fixture
def sample_data_path(test_resources_path):
    return os.path.join(
        os.path.dirname(test_resources_path),
        "sample_data"
    )


@pytest.fixture
def sample_data_csv(sample_data_path):
    return os.path.join(
        sample_data_path,
        "sample_data_test_values.csv"
    )


@pytest.fixture
def run_data_csv(sample_data_path):
    return os.path.join(
        sample_data_path,
        "run_data_test_values.csv"
    )


@pytest.fixture
def experiment_set_lims_json_file(test_resources_path):
    return os.path.join(test_resources_path, "snpseq_data_XYZ321XY.snpseq.json")


@pytest.fixture
def runfolder_path(test_resources_path):
    return os.path.join(test_resources_path, "210415_A00001_0123_BXYZ321XY")


@pytest.fixture
def runfolder_run_date(runfolder_path):
    date_str = os.path.basename(runfolder_path).split("_")[0]
    if len(date_str) == 6:
        return datetime.datetime.strptime(date_str, "%y%m%d")
    else:
        return datetime.datetime.strptime(date_str, "%Y%m%d")


@pytest.fixture
def runfolder_flowcell_id(runfolder_path):
    return runfolder_path.split("_")[-1][1:]


@pytest.fixture
def runfolder_samplesheet():
    return "fc_SampleSheet.csv"


@pytest.fixture
def runfolder_run_parameters():
    return "RunParameters.xml"


@pytest.fixture
def runfolder_ngi_json_file(runfolder_path):
    return f"{runfolder_path}.ngi.json"


@pytest.fixture
def runfolder_ngi_json(runfolder_ngi_json_file):
    return parse_json(runfolder_ngi_json_file)


@pytest.fixture
def runfolder_sra_json_file(runfolder_path):
    return f"{runfolder_path}.sra.json"


@pytest.fixture
def runfolder_sra_json(runfolder_sra_json_file):
    return parse_json(runfolder_sra_json_file)


@pytest.fixture
def runfolder_sra_xml_file(runfolder_path):
    return f"{runfolder_path}.sra.xml"


@pytest.fixture
def runfolder_sra_xml(runfolder_sra_xml_file):
    return parse_xml(runfolder_sra_xml_file)


@pytest.fixture
def runfolder_sra_manifest_file(runfolder_path):
    return f"{runfolder_path}.sra.manifest"


@pytest.fixture
def runfolder_sra_manifest(runfolder_sra_manifest_file):
    with open(runfolder_sra_manifest_file, "r") as fh:
        return [tuple(line.strip().split("\t")) for line in fh]


@pytest.fixture
def experiment_set_name(experiment_set_lims_json):
    return experiment_set_lims_json["result"]["name"]


@pytest.fixture
def experiment_set_samples(experiment_set_lims_json):
    return experiment_set_lims_json["result"]["samples"]


@pytest.fixture
def experiment_set_lims_json(experiment_set_lims_json_file):
    return parse_json(experiment_set_lims_json_file)


@pytest.fixture
def experiment_set_ngi_json_file(experiment_set_lims_json_file):
    return os.path.join(
        os.path.dirname(experiment_set_lims_json_file),
        os.path.basename(experiment_set_lims_json_file).replace(
            ".snpseq.",
            ".ngi."
        )
    )


@pytest.fixture
def experiment_set_ngi_json(experiment_set_ngi_json_file):
    return parse_json(experiment_set_ngi_json_file)


@pytest.fixture
def experiment_set_sra_json_file(experiment_set_lims_json_file):
    return os.path.join(
        os.path.dirname(experiment_set_lims_json_file),
        os.path.basename(experiment_set_lims_json_file).replace(
            ".snpseq.",
            ".sra."
        )
    )


@pytest.fixture
def experiment_set_sra_json(experiment_set_sra_json_file):
    return parse_json(experiment_set_sra_json_file)


@pytest.fixture
def experiment_set_sra_xml_file(experiment_set_sra_json_file):
    return os.path.join(
        os.path.dirname(experiment_set_sra_json_file),
        os.path.basename(experiment_set_sra_json_file).replace(
            ".json",
            ".xml"
        )
    )


@pytest.fixture
def experiment_set_sra_xml(experiment_set_sra_xml_file):
    return parse_xml(experiment_set_sra_xml_file)


@pytest.fixture
def file_checksums(test_resources_path):
    method = "MD5"
    file_checksums = {}

    file_contents = [
        "this is some text that will generate a checksum",
        "this is some other text that will generate another checksum"
    ]

    checksums = [
        "3bcd3f921bab077437a4d5289fbee4c9",
        "ba55c62dc4e8420b71c8b13763e54f7c"
    ]

    for contents, checksum in zip(file_contents, checksums):

        testfile = os.path.join(
            test_resources_path,
            f"{checksum}.{method.lower()}"
        )
        with open(testfile, "w") as fh:
            fh.write(contents)
            fh.write("\n")

        file_checksums[testfile] = checksum

    return file_checksums


@pytest.fixture
def checksum_file(test_resources_path, file_checksums):
    checksum_file = os.path.join(
        test_resources_path,
        "MD5",
        "checksums.md5"
    )
    if not os.path.exists(checksum_file):
        os.makedirs(
            os.path.dirname(
                checksum_file
            ),
            exist_ok=True
        )
        with open(checksum_file, "w") as fh:
            for pth, md5 in file_checksums.items():
                fh.write(f"{md5}  {pth}\n")

    return checksum_file


@pytest.fixture
def samplesheet_file(
        test_resources_path,
        samplesheet_header,
        samplesheet_data):
    samplesheet_file = os.path.join(
        test_resources_path,
        "test_samplesheet.csv"
    )
    if not os.path.exists(samplesheet_file):
        with open(samplesheet_file, "w") as fh:
            fh.write(samplesheet_header)
            cols = ",".join(samplesheet_data[0].keys())
            fh.write(
                "\n".join(
                    [cols] + [
                        ",".join(row.values())
                        for row in samplesheet_data
                    ]
                )
            )
    return samplesheet_file


@pytest.fixture
def samplesheet_header():
    header = """[Header],,,,,,,,
IEMFileVersion,4,,,,,,,
Investigator Name,SNPSEQ,,,,,,,
Experiment,NovaSeq-dual-index,,,,,,,
Date,2021-03-09,,,,,,,
Workflow,GenerateFASTQ,,,,,,,
Application,NovaSeq FASTQ Only,,,,,,,
Assay,TruSeq HT,,,,,,,
Description,,,,,,,,
Chemistry,Amplicon,,,,,,,
,,,,,,,,
[Reads],,,,,,,,
151,,,,,,,,
151,,,,,,,,
,,,,,,,,
[Settings],,,,,,,,
Adapter,,,,,,,,
AdapterRead2,,,,,,,,
,,,,,,,,
[Data],,,,,,,,
"""
    return header


@pytest.fixture
def samplesheet_data():
    data = [
        [
            "Lane",
            "Sample_ID",
            "Sample_Name",
            "Sample_Plate",
            "Sample_Well",
            "I7_Index_ID",
            "index",
            "I5_Index_ID",
            "index2",
            "Sample_Project",
            "Description",
        ],
        [
            "1",
            "Sample_AB-2755-1290",
            "AB-2755-1290",
            "",
            "",
            "",
            "CCGCGGTT",
            "",
            "CTAGCGCT",
            "AB-2755",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2755-1290_2-2271",
        ],
        [
            "1",
            "Sample_AB-2755-1277",
            "AB-2755-1277",
            "",
            "",
            "",
            "TTATAACC",
            "",
            "TCGATATC",
            "AB-2755",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2755-1277_2-2272",
        ],
        [
            "1",
            "Sample_AB-2755-1341",
            "AB-2755-1341",
            "",
            "",
            "",
            "GGACTTGG",
            "",
            "CGTCTGCG",
            "AB-2755",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2755-1341_2-2273",
        ],
        [
            "1",
            "Sample_AB-2755-1332",
            "AB-2755-1332",
            "",
            "",
            "",
            "AAGTCCAA",
            "",
            "TACTCATA",
            "AB-2755",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2755-1332_2-2274",
        ],
        [
            "1",
            "Sample_AB-2755-1307",
            "AB-2755-1307",
            "",
            "",
            "",
            "ATCCACTG",
            "",
            "ACGCACCT",
            "AB-2755",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2755-1307_2-2275",
        ],
        [
            "1",
            "Sample_AB-2755-1282",
            "AB-2755-1282",
            "",
            "",
            "",
            "GCTTGTCA",
            "",
            "GTATGTTC",
            "AB-2755",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2755-1282_2-2276",
        ],
        [
            "2",
            "Sample_AB-2755-1314",
            "AB-2755-1314",
            "",
            "",
            "",
            "CAAGCTAG",
            "",
            "CGCTATGT",
            "AB-2755",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2755-1314_2-2277",
        ],
        [
            "2",
            "Sample_AB-2755-1317",
            "AB-2755-1317",
            "",
            "",
            "",
            "TGGATCGA",
            "",
            "TATCGCAC",
            "AB-2755",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2755-1317_2-2278",
        ],
        [
            "2",
            "Sample_AB-2755-1295",
            "AB-2755-1295",
            "",
            "",
            "",
            "AGTTCAGG",
            "",
            "TCTGTTGG",
            "AB-2755",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2755-1295_2-2279",
        ],
        [
            "2",
            "Sample_AB-2755-1286",
            "AB-2755-1286",
            "",
            "",
            "",
            "GACCTGAA",
            "",
            "CTCACCAA",
            "AB-2755",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2755-1286_2-2280",
        ],
        [
            "2",
            "Sample_AB-2755-1234",
            "AB-2755-1234",
            "",
            "",
            "",
            "TCTCTACT",
            "",
            "GAACCGCG",
            "AB-2755",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2755-1234_2-2281",
        ],
        [
            "2",
            "Sample_AB-2755-1090",
            "AB-2755-1090",
            "",
            "",
            "",
            "CTCTCGTC",
            "",
            "AGGTTATA",
            "AB-2755",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2755-1090_2-2282",
        ],
        [
            "3",
            "Sample_AB-2769-653",
            "AB-2769-653",
            "",
            "",
            "",
            "CTACGACA",
            "",
            "TTGGACTC",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-653_2-5886",
        ],
        [
            "3",
            "Sample_AB-2769-659",
            "AB-2769-659",
            "",
            "",
            "",
            "TAAGTGGT",
            "",
            "GGCTTAAG",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-659_2-5887",
        ],
        [
            "3",
            "Sample_AB-2769-620",
            "AB-2769-620",
            "",
            "",
            "",
            "CGGACAAC",
            "",
            "AATCCGGA",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-620_2-5888",
        ],
        [
            "3",
            "Sample_AB-2769-726",
            "AB-2769-726",
            "",
            "",
            "",
            "ATATGGAT",
            "",
            "TAATACAG",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-726_2-5889",
        ],
        [
            "3",
            "Sample_AB-2769-622",
            "AB-2769-622",
            "",
            "",
            "",
            "GCGCAAGC",
            "",
            "CGGCGTGA",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-622_2-5890",
        ],
        [
            "3",
            "Sample_AB-2769-827",
            "AB-2769-827",
            "",
            "",
            "",
            "AAGATACT",
            "",
            "ATGTAAGT",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-827_2-5891",
        ],
        [
            "3",
            "Sample_AB-2769-623",
            "AB-2769-623",
            "",
            "",
            "",
            "CGTCTGCG",
            "",
            "ATTGTGAA",
            "AB-2769",
            "FRAGMENT_SIZE:285;FRAGMENT_LOWER:95;FRAGMENT_UPPER:671;LIBRARY_NAME:AB-2769-623_2-5898",
        ],
        [
            "3",
            "Sample_AB-2769-673",
            "AB-2769-673",
            "",
            "",
            "",
            "GGAGCGTC",
            "",
            "GCACGGAC",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-673_2-5892",
        ],
        [
            "3",
            "Sample_AB-2769-647",
            "AB-2769-647",
            "",
            "",
            "",
            "ATGGCATG",
            "",
            "GGTACCTT",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-647_2-5893",
        ],
        [
            "3",
            "Sample_AB-2769-648",
            "AB-2769-648",
            "",
            "",
            "",
            "GCAATGCA",
            "",
            "AACGTTCC",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-648_2-5894",
        ],
        [
            "3",
            "Sample_AB-2769-649",
            "AB-2769-649",
            "",
            "",
            "",
            "GTTCCAAT",
            "",
            "GCAGAATT",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-649_2-5895",
        ],
        [
            "3",
            "Sample_AB-2769-727",
            "AB-2769-727",
            "",
            "",
            "",
            "ACCTTGGC",
            "",
            "ATGAGGCC",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-727_2-5896",
        ],
        [
            "3",
            "Sample_AB-2769-728",
            "AB-2769-728",
            "",
            "",
            "",
            "ATATCTCG",
            "",
            "ACTAAGAT",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-728_2-5897",
        ],
        [
            "4",
            "Sample_AB-2769-653",
            "AB-2769-653",
            "",
            "",
            "",
            "CTACGACA",
            "",
            "TTGGACTC",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-653_2-5886",
        ],
        [
            "4",
            "Sample_AB-2769-659",
            "AB-2769-659",
            "",
            "",
            "",
            "TAAGTGGT",
            "",
            "GGCTTAAG",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-659_2-5887",
        ],
        [
            "4",
            "Sample_AB-2769-620",
            "AB-2769-620",
            "",
            "",
            "",
            "CGGACAAC",
            "",
            "AATCCGGA",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-620_2-5888",
        ],
        [
            "4",
            "Sample_AB-2769-726",
            "AB-2769-726",
            "",
            "",
            "",
            "ATATGGAT",
            "",
            "TAATACAG",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-726_2-5889",
        ],
        [
            "4",
            "Sample_AB-2769-622",
            "AB-2769-622",
            "",
            "",
            "",
            "GCGCAAGC",
            "",
            "CGGCGTGA",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-622_2-5890",
        ],
        [
            "4",
            "Sample_AB-2769-827",
            "AB-2769-827",
            "",
            "",
            "",
            "AAGATACT",
            "",
            "ATGTAAGT",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-827_2-5891",
        ],
        [
            "4",
            "Sample_AB-2769-623",
            "AB-2769-623",
            "",
            "",
            "",
            "CGTCTGCG",
            "",
            "ATTGTGAA",
            "AB-2769",
            "FRAGMENT_SIZE:285;FRAGMENT_LOWER:95;FRAGMENT_UPPER:671;LIBRARY_NAME:AB-2769-623_2-5898",
        ],
        [
            "4",
            "Sample_AB-2769-673",
            "AB-2769-673",
            "",
            "",
            "",
            "GGAGCGTC",
            "",
            "GCACGGAC",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-673_2-5892",
        ],
        [
            "4",
            "Sample_AB-2769-647",
            "AB-2769-647",
            "",
            "",
            "",
            "ATGGCATG",
            "",
            "GGTACCTT",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-647_2-5893",
        ],
        [
            "4",
            "Sample_AB-2769-648",
            "AB-2769-648",
            "",
            "",
            "",
            "GCAATGCA",
            "",
            "AACGTTCC",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-648_2-5894",
        ],
        [
            "4",
            "Sample_AB-2769-649",
            "AB-2769-649",
            "",
            "",
            "",
            "GTTCCAAT",
            "",
            "GCAGAATT",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-649_2-5895",
        ],
        [
            "4",
            "Sample_AB-2769-727",
            "AB-2769-727",
            "",
            "",
            "",
            "ACCTTGGC",
            "",
            "ATGAGGCC",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-727_2-5896",
        ],
        [
            "4",
            "Sample_AB-2769-728",
            "AB-2769-728",
            "",
            "",
            "",
            "ATATCTCG",
            "",
            "ACTAAGAT",
            "AB-2769",
            "FRAGMENT_SIZE:430;FRAGMENT_LOWER:230;FRAGMENT_UPPER:630;LIBRARY_NAME:AB-2769-728_2-5897",
        ],
    ]
    return [
        dict(
            zip(
                map(
                    str.lower,
                    data[0]
                ),
                row
            )
        )
        for row in data[1:]
    ]
