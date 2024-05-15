
[![Run unit tests](../../actions/workflows/run-unit-tests.yml/badge.svg?event=push)](../../actions/workflows/run-unit-tests.yml)

# snpseq_metadata

This is a Python project that allows parsing of metadata associated with sequencing projects and export to various formats.

## Prerequisites

- Python >= 3.8

## Installation
Clone the repo to your local machine and deploy the code
```
git clone https://github.com/Molmed/snpseq_metadata && cd snpseq_metadata
python3 -m venv --upgrade-deps .venv
source .venv/bin/activate
pip install .
```
Download the [ENA/SRA XML schema](#enasra-xml-schema) and generate python models (can be skipped if these are already available)
``` 
generate_python_models.sh xsdata
```

## Docker

You can also build a docker image using the supplied Dockerfile:

```
docker build -t snpseq_metadata .
docker run -v /path/to/host/folder:/mnt/metadata snpseq_metadata snpseq_metadata --help
```

## Usage

The main command is `snpseq_metadata` and it offers a number of subcommands. Running without arguments will display the usage help:
```
$ snpseq_metadata
Usage: snpseq_metadata [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  export
  extract
```

### extract
The `extract` subcommand is used to parse a runfolder from disk and extract the metadata, or parse data from
 the [snpseq_data](https://gitlab.snpseq.medsci.uu.se/shared/snpseq-data) service and export to the specified format:
```
$ snpseq_metadata extract --help
Usage: snpseq_metadata extract [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  runfolder
  snpseq-data
```
#### runfolder
The `runfolder` subcommand is used to parse a runfolder from disk, extract the necessary metadata and export to the
specified format.
```
$ snpseq_metadata extract runfolder --help
Usage: snpseq_metadata extract runfolder [OPTIONS] RUNFOLDER_PATH COMMAND1
                                         [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  -o, --outdir PATH  [default: current working directory]
  --help             Show this message and exit.

Commands:
  json
```
Here, `RUNFOLDER_PATH` is the path to the sequencing runfolder for which metadata should be exported.
Some test data are available under `tests/resources/export` and extracting metadata to json can be accomplished by:
```
$ snpseq_metadata extract runfolder \
  -o /tmp/ \
  tests/resources/export/210415_A00001_0123_BXYZ321XY
  json
```
This will parse the runfolder into the python NGI models and serialize the models to json, saved under the specified
output directory:
```
/tmp
└── 210415_A00001_0123_BXYZ321XY.ngi.json
```

#### snpseq-data
The `snpseq-data` subcommand is used to parse data exported from the
[snpseq_data](https://gitlab.snpseq.medsci.uu.se/shared/snpseq-data) service and export to the specified format.
```
$ snpseq_metadata extract snpseq-data --help
Usage: snpseq_metadata extract snpseq-data [OPTIONS] SNPSEQ_DATA_FILE COMMAND1
                                           [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  -o, --outdir PATH  [default: current working directory]
  --help             Show this message and exit.

Commands:
  json
```
Here, `SNPSEQ_DATA_FILE` is the path to a json-file containing metadata for a flowcell obtained from the
[snpseq_data](https://gitlab.snpseq.medsci.uu.se/shared/snpseq-data) service. Some test data are available under
`tests/resources/export` and extracting metadata to json can be accomplished by:
```
$ snpseq_metadata extract snpseq-data \
  -o /tmp/ \
  tests/resources/export/snpseq_data_XYZ321XY.json
  json
```
This will parse the metadata into the python NGI models and serialize the models to json, saved under the specified
output directory:
```
/tmp
└── /snpseq_data_XYZ321XY.ngi.json
```

### export

The `export` subcommand is used to parse the extracted NGI model metadata from json into python SRA models and
serialize the models into the specified formats:
```
$ snpseq_metadata export
Usage: snpseq_metadata export [OPTIONS] RUNFOLDER_DATA SNPSEQ_DATA COMMAND1
                              [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  -o, --outdir PATH  [default: current working directory]
  --help             Show this message and exit.

Commands:
  json
  manifest
  xml
```

Here, `RUNFOLDER_DATA` is the path to a json file with serialized NGI runfolder metadata (created with the
`extract runfolder` subcommand above), for which metadata should be exported and `SNPSEQ_DATA` is the path to a
json-file with serialized NGI experiment metadata (created with the `extract snpseq-data` subcommand above).

Some test data are available under `tests/resources/export` and exporting metadata compatible with the SRA XML submission
format and also to a human-friendly manifest or tsv format can be accomplished by:

```
$ snpseq_metadata export \
  -o /tmp/ \
  tests/resources/export/210415_A00001_0123_BXYZ321XY.ngi.json \
  tests/resources/export/snpseq_data_XYZ321XY.ngi.json \
  xml manifest tsv
```
For each unique project, this will export one TSV file, a pair of XML-files representing metadata for the RUN and 
EXPERIMENT objects and one manifest file for each unique experiment. For the test data set, the command above will create:
```
/tmp/
├── AB-1234-experiment.xml
├── AB-1234-run.xml
├── AB-1234.metadata.ena.tsv
├── CD-5678-experiment.xml
├── CD-5678-run.xml
├── Project_CD-5678.metadata.ena.tsv
├── EF-9012-experiment.xml
├── EF-9012-run.xml
├── EF-9012.metadata.ena.tsv
├── AB-1234-Sample_AB-1234-SampleA-1-NovaSeq.manifest
├── AB-1234-Sample_AB-1234-SampleA-2-NovaSeq.manifest
├── AB-1234-Sample_AB-1234-SampleB-NovaSeq.manifest
├── CD-5678-CD-5678-SampleA-1-NovaSeq.manifest
├── CD-5678-CD-5678-SampleA-2-NovaSeq.manifest
└── CD-5678-CD-5678-SampleB-NovaSeq.manifest
```
## Test data
As mentioned above, test data is available under `tests/resources/export` and the package include a pytest suite.
If not already installed, first install the test dependencies:
```
source .venv/bin/activate
pip install .[test]
```
Then the test suite can be run with 
```
pytest tests/
``` 
In addition, a python script for validating a XML file against an XSD schema is provided:
```
$ python tests/validate_xml_file.py --help
Usage: validate_xml_file.py [OPTIONS] XML_FILE XSD_FILE

Options:
  --help  Show this message and exit.
```
For integration tests, a bash script is provided which runs through the test data and validates the generated XML files
against the corresponding schema:
```
bash tests/validate_test_data.sh $(pwd) /tmp/test_output
```
## Package structure
The code is built around the concept of having a set of models that represent metadata and provide internal logic,
functionality for serializing and de-serializing etc. Such a model can then represent metadata from a specific
source (e.g. LIMS, NGI, SRA) and the class files are collected as a separate module under 
`snpseq_metadata/models/[source]_models`.

A conversion layer that provide functionality to convert between metadata models is provided in
`snpseq_metadata/models/converter.py`, with the help of mapping utilities for translating e.g. NGI to SRA library 
terminologies in `snpseq_metadata/models/ngi_to_sra_library_mapping.py`.

### ENA/SRA XML schema
[ENA/SRA](https://www.ebi.ac.uk/ena/browser/home) provide 
[XML schema](ftp://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5/) (in XSD format), specifying the format for the 
metadata XML files used for 
[programmatic submission](https://ena-docs.readthedocs.io/en/latest/submit/general-guide/programmatic.html) of raw 
sequences to the repository.
 
### xsdata
The [xsdata](https://xsdata.readthedocs.io/en/latest/) library was used to create python dataclasses from the XML
schemas provided by SRA. These dataclasses are used to export the modeled metadata into XML format, corresponding to
the SRA schemas. The `snpseq_metadata` package contains wrappers around the dataclasses and functionality for
converting between different data models.

This is the typical command for creating the python dataclasses for the XML schema files located in `resources/schema`
using xsdata:
```
$ cd snpseq_metadata/models && \
  xsdata generate \
    -p xsdata ../../resources/schema
```

### NGI to SRA library mapping
The SRA model has a terminology for
[Library selection](https://ena-docs.readthedocs.io/en/latest/submit/reads/webin-cli.html#permitted-values-for-library-selection),
[Library source](https://ena-docs.readthedocs.io/en/latest/submit/reads/webin-cli.html#permitted-values-for-library-source) and
[Library strategy](https://ena-docs.readthedocs.io/en/latest/submit/reads/webin-cli.html#permitted-values-for-library-strategy) that
is not directly translatable from the fields stored in e.g. Clarity LIMS. 

Therefore, the information stored in Clarity LIMS have to be mapped to the corresponding SRA/ENA terms. This is done by
representing the information by the different models and following defined logic to convert from one model to the next
according to:
```
Clarity LIMS extract -> lims_models -> ngi_models -> sra_models -> export SRA/ENA terms
```

Each model represents the library construction information in e.g. 
`snpseq_metadata/models/[source]_models/library_design.py` and contains logic to create corresponding class instances.
The file `snpseq_metadata/models/ngi_to_sra_mapping.py` contains the logic for mapping the NGI library model to the 
SRA model representation.

As an example, consider the representations for mRNA sequencing libraries. The SRA model represents this library type 
with the class `RNASeq.MRNA`. This class defines the corresponding SRA/ENA terminology that should be used for 
submissions. In this case:
- library_source: `TRANSCRIPTOMIC`
- library_strategy: `RNA-Seq`
- library_selection: `POLY_A` 

In `snpseq_metadata/models/ngi_to_sra_mapping.py`, it is specified that the NGI model 
representation that maps to this class is the combination of:
- `NGISourceClasses.RNA.TOTAL` or `NGISourceClasses.RNA.DEPLETED` or `NGISource`
- `NGIApplicationClasses.RNASEQ`
- `NGILibraryKitClasses.TRANSCRIPTOMIC.MRNA` 

In the declaration of each of these classes, it is defined what Clarity terms they correspond to. 
For example:
- `NGISourceClasses.RNA.TOTAL`: `total RNA`
- `NGIApplicationClasses.RNASEQ`: `rna-seq`
- `NGILibraryKitClasses.TRANSCRIPTOMIC.MRNA`: `truseq stranded mrna sample preparation kit` or 
`truseq stranded mrna sample preparation kit ht`

Finally, in `lims_models/library_design.py`, it's declared what Clarity LIMS UDFs and values are mapped to which 
`lims_models` classes:
- `LIMSApplicationClasses.RNASEQ`: `udf_application`
  - `rna-seq`
- `LIMSSampleType.RNA.TOTAL`: `udf_sample_type`
  - `total RNA`
- `LIMSLibraryKit.TRANSCRIPTOMIC.MRNA`: `udf_library_preparation_kit`
  - `truseq stranded mrna sample preparation kit`
  - `truseq stranded mrna sample preparation kit ht`
