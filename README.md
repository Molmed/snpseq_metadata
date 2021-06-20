# snpseq_metadata

This is a Python project that allows parsing of metadata associated with sequencing projects and export to various formats.

## Prerequisites

- Python 3.7 or greater
- [xsdata](https://xsdata.readthedocs.io/en/latest/)

## Installation

Clone the repo to your local machine and run

```pip install -r requirements.txt -e .```

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
The `extract` subcommand is used to parse a runfolder and extract the metadata:
```
$ snpseq_metadata extract --help
Usage: snpseq_metadata extract [OPTIONS] RUNFOLDER COMMAND1 [ARGS]...
                               [COMMAND2 [ARGS]...]...

Options:
  -o, --outdir PATH  [default: current working directory]
  --help             Show this message and exit.

Commands:
  json
```
Here, `RUNFOLDER` is the path to the sequencing runfolder for which metadata should be exported.
Some test data are available under `tests/resources` and extracting metadata to json can be accomplished by:
```
$ snpseq_metadata export \
  -o /tmp/ \
  tests/resources/210415_A00001_0123_BXYZ321XY
  json
```
This will parse the runfolder into the python NGI models and serialize the models to json, saved under the specified 
output directory:
```
/tmp
└── 210415_A00001_0123_BXYZ321XY.json
``` 

### export

The `export` subcommand is used to parse metadata into python SRA models and serialize the models into the desired 
formats:
```
$ snpseq_metadata export
Usage: snpseq_metadata export [OPTIONS] RUNFOLDER DATA COMMAND1 [ARGS]...
                              [COMMAND2 [ARGS]...]...

Options:
  -o, --outdir PATH  [default: current working directory]
  --help             Show this message and exit.

Commands:
  json
  manifest
  xml
``` 

Here, `RUNFOLDER` is the path to a json file with serialized NGI runfolder metadata (created with the `extract` 
subcommand above), for which metadata should be exported and `DATA` is the path to a json-file with project metadata, 
exported by the [snpseq_data](https://gitlab.snpseq.medsci.uu.se/shared/snpseq-data) service.

Some test data are available under `tests/resources` and exporting metadata compatible with the SRA XML submission 
format and also to a human-friendly manifest (compatible with SRA submissions) can be accomplished by:

```
$ snpseq_metadata export \
  -o /tmp/ \
  tests/resources/210415_A00001_0123_BXYZ321XY.ngi.json \
  tests/resources/snpseq_data_XYZ321XY.json \
  xml manifest
```
For each unique project, this will export a pair of XML-files representing metadata for the RUN and EXPERIMENT objects 
and one manifest file for each sample. For the test data set, the command above will create:
```
/tmp/
├── AB-1234-experiment.xml
├── AB-1234-run.xml
├── CD-5678-experiment.xml
├── CD-5678-run.xml
├── EF-9012-experiment.xml
├── EF-9012-run.xml
├── AB-1234-Sample_AB-1234-SampleA-1.manifest
├── AB-1234-Sample_AB-1234-SampleA-2.manifest
├── AB-1234-Sample_AB-1234-SampleB.manifest
├── CD-5678-CD-5678-SampleA-1.manifest
├── CD-5678-CD-5678-SampleA-2.manifest
└── CD-5678-CD-5678-SampleB.manifest
```
## Package structure
The code is built around the concept of having a set of classes represent metadata and provide internal logic, 
functionality for serializing and de-serializing etc. Such a set of classes can then represent metadata from a specific 
source (e.g. LIMS, SRA) and are collected as a separate module under `snpseq_metadata/models/[source]_models`. 

A conversion layer that provide functionality to convert between metadata models is provided in 
`snpseq_metadata/models/converter.py`, with the help of library mappings from NGI to SRA terminologies in 
`snpseq_metadata/models/ngi_to_sra_library_mapping.py`.


### xsdata
The [xsdata](https://xsdata.readthedocs.io/en/latest/) library was used to create python dataclasses from the XML 
schemas provided by SRA. The `snpseq_metadata` package contains wrappers around these dataclasses and functionality for
converting between different data models.

This is the typical command for creating the python dataclasses for the XML schema files located in `resources/schema` 
using xsdata:
```
$ cd snpseq_metadata/models && \
  xsdata generate \
    -p xsdata ../../resources/schema
```

### NGI to SRA library mapping
The SRA model have a terminology for 
[Library selection](https://ena-docs.readthedocs.io/en/latest/submit/reads/webin-cli.html#permitted-values-for-library-selection), 
[Library source](https://ena-docs.readthedocs.io/en/latest/submit/reads/webin-cli.html#permitted-values-for-library-source) and 
[Library strategy](https://ena-docs.readthedocs.io/en/latest/submit/reads/webin-cli.html#permitted-values-for-library-strategy) that 
is not directly translatable from the fields stored in e.g. Clarity LIMS. Therefore, the file 
`snpseq_metadata/models/ngi_to_sra_library_mapping.py` contains functionality for mapping the NGI terminology to the SRA
terminology.

To add a new mapping for a application, sample type and sample prep kit, create a class that is a subclass of 
`ApplicationSampleTypeMapping` and has class variables 
```
ngi_application
ngi_sample_type
ngi_sample_prep_kit
``` 
containing the possible values (in lower case) stored in Clarity LIMS. Use the class variables 
```
sra_library_strategy 
sra_library_source
sra_library_source
```
to specify the corresponding SRA values. 
Here is an example for bisulfite sequencing libraries:
```
class Bisulphite(ApplicationSampleTypeMapping):
    """
    Bisulphite sequencing
    """

    ngi_application = "epigenetics"
    ngi_sample_type = "gdna"
    ngi_sample_prep_kit = ["splat", "nebnext enzymatic methyl-seq kit"]

    sra_library_strategy = TypeLibraryStrategy.BISULFITE_SEQ
    sra_library_source = TypeLibrarySource.GENOMIC
    sra_library_selection = TypeLibrarySelection.RANDOM

```
The `ApplicationSampleTypeMapping` class contains logic for finding the 
correct mapping from a NGI model. If needed, this logic can be overridden in the subclass.