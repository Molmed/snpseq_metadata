
import csv
import json
import os
import re
import sys

from functools import cmp_to_key


class MetaObj:

    model_source = ""

    JSON_STRUCTURE = ""
    XML_STRUCTURE = ""
    MANIFEST = ""

    MAPPING = {}

    def __init__(self, fields):
        self._fields = fields.copy()
        self.fields = fields.copy()

        for cls_key, meta_key in self.MAPPING.items():
            self.fields[cls_key] = self.fields[meta_key]

    def flowcell_id(self):
        return self.fields.get("flowcell_id", "FCID")

    def structure_to_str(self, structure):
        return structure.format(**self.fields)

    def to_json(self):
        return json.loads(
            self.structure_to_str(
                self.JSON_STRUCTURE
            )
        )

    def to_xml(self):
        return self.structure_to_str(
            self.XML_STRUCTURE
        )

    def to_manifest(self, extra_rows=None):
        extra_rows = extra_rows or []
        rows = [
            "\t".join(
                [
                    manifest[0],
                    self.structure_to_str(
                        manifest[1]
                    )
                ]
            ) for manifest in self.MANIFEST
        ]
        return "\n".join(
            filter(
                lambda r: len(r) > 0,
                rows + extra_rows
            )
        )

    @classmethod
    def create_from_csv(cls, csv_file):
        fields = dict()
        with open(csv_file) as fh:
            reader = csv.reader(fh, dialect=csv.excel)
            for row in filter(lambda r: len(r) >= 2, reader):
                if len(row) > 2:
                    fields[row[0]] = row[1:]
                else:
                    fields[row[0]] = row[1]
        return cls(fields=fields)

    def to_class(self, cls):
        return cls(self._fields)

    def _export_to_file(self, contents, ext, outdir, outname=None):
        outfile = os.path.join(outdir, f"{outname or ''}.{self.model_source}.{ext}")
        os.makedirs(outdir, exist_ok=True)
        with open(outfile, "w") as fh:
            fh.write(contents)
        return outfile

    def export_json(self, outdir, outname=None):
        return self._export_to_file(
            json.dumps(
                self.to_json(),
                indent=2
            ),
            "json",
            outdir,
            outname=outname
        )

    def export_xml(self, outdir, outname=None):
        return self._export_to_file(
            self.to_xml(),
            "xml",
            outdir,
            outname=outname
        )

    def export_manifest(self, outdir, outname=None):
        return self._export_to_file(
            self.to_manifest(),
            "manifest",
            outdir,
            outname=outname
        )

    def create_sample_folder(self, outdir):
        project_dir = os.path.join(outdir, self.fields["project_id"])
        sample_dir = os.path.join(project_dir, self.fields["sample_id"])
        os.makedirs(sample_dir, exist_ok=True)
        for fqfile in self.fields["sequencing_run_fastq_files"]:
            fqfile.create_file(sample_dir)

    def write_checksum(self, checksumfile):
        for fqfile in self.fields["sequencing_run_fastq_files"]:
            fqfile.write_checksum(checksumfile)

    def samplesheet_entries(self):
        entries = []
        for fqfile in self.fields["sequencing_run_fastq_files"]:
            entry = fqfile.samplesheet_entry()
            if not entry:
                continue
            entry["sample_id"] = self.fields["sample_id"]
            entry["sample_name"] = self.fields["sample_name"]
            entry["project_id"] = self.fields["project_id"]
            entry["index"] = self.fields["index_i7"]
            entry["index2"] = self.fields["index_i5"]
            entry["description"] = ";".join([
                f"FRAGMENT_SIZE:{self.fields['fragment_size']}",
                f"FRAGMENT_LOWER:{self.fields['fragment_lower']}",
                f"FRAGMENT_UPPER:{self.fields['fragment_upper']}",
                f"LIBRARY_NAME:{self.fields['sample_name']}_{self.fields['udf_id']}",
            ])
            entries.append(entry)

        return entries


class FastqFile(MetaObj):

    def _filepath(self, outdir):
        return os.path.join(
            outdir,
            os.path.basename(
                self.fields["filepath"]
            )
        )

    def create_file(self, outdir):
        fpath = self._filepath(outdir)
        with open(fpath, "w") as fh:
            fh.write(self.fields["checksum"])

        return fpath

    def write_checksum(self, checksumfile):
        with open(checksumfile, "a") as fh:
            fh.write("  ".join([
                self.fields["checksum"],
                self.fields["filepath"]
            ]))
            fh.write("\n")

    def samplesheet_entry(self):
        pat = r'^.*\/[^\/]+_S(\d+)_L00(\d+)_R1_.*$'
        m = re.match(
            pat,
            self.fields["filepath"]
        )
        if not m:
            return None
        return {
            "lane": m.group(2),
            "entry_pos": m.group(1)
        }


class NGIFastqFile(FastqFile):

    model_source = "ngi"

    JSON_STRUCTURE = """
        {{
            "filepath": "{filepath}",
            "filetype": "{filetype}",
            "checksum": "{checksum}",
            "checksum_method": "{checksum_method}"
        }}
    """


class SRAFastqFile(FastqFile):

    model_source = "sra"

    JSON_STRUCTURE = """
        {{
            "filename": "{filename}",
            "filetype": "{filetype}",
            "checksum": "{checksum}",
            "checksum_method": "{checksum_method}"
        }}
    """

    XML_STRUCTURE = """
                <FILE filename="{filename}" filetype="{filetype}" checksum_method="{checksum_method}" checksum="{checksum}" />"""

    MANIFEST = [
        ["FASTQ", "{filename}"]
    ]

    MAPPING = {
        "filename": "filepath"
    }

    def __init__(self, fields):
        super(SRAFastqFile, self).__init__(fields)


class SnpseqDataSampleObj(MetaObj):

    FIELDNAMES = [
        'name',
        'project',
        'udf_application',
        'udf_conc_fc',
        'udf_current_sample_volume_ul',
        'udf_custom_sequencing_primer',
        'udf_data_analysis',
        'udf_genotyping_idpanel',
        'udf_id',
        'udf_index',
        'udf_index2',
        'udf_insert_size_bp',
        'udf_library_preparation_kit',
        'udf_number_of_lanes',
        'udf_of_libraries_per_sample',
        'udf_phix_',
        'udf_plate_',
        'udf_pooling',
        'udf_progress',
        'udf_read_length',
        'udf_rml_kitprotocol',
        'udf_sample_conc',
        'udf_sample_type',
        'udf_seq_data_coverage_x',
        'udf_sequencing_instrument',
        'udf_special_info_prep',
        'udf_special_info_seq',
        'udf_species',
        'udf_volume_ul'
    ]

    MAPPING = {
        "name": "sample_name",
        "project": "project_id",
        "udf_read_length": "read_configuration",
        "udf_sequencing_instrument": "instrument_model_name",
        "udf_index": "index_i7",
        "udf_index2": "index_i5",
        "udf_insert_size_bp": "insert_size",
        "udf_library_preparation_kit": "experiment_library_kit",
        "udf_sample_type": "experiment_sample_type",
        "udf_application": "experiment_application"
    }

    def to_json(self):
        return {k: self.fields.get(k, "") for k in self.FIELDNAMES}


class ExperimentObj(MetaObj):

    def export_manifest(self, outdir, outname=None):
        return super(ExperimentObj, self).export_manifest(
            outdir,
            outname=f"{outname or ''}.{self.fields['sample_id']}"
        )


class NGIExperimentObj(ExperimentObj):

    model_source = "ngi"

    JSON_STRUCTURE = """
        {{
          "alias": "{experiment_ngi_alias}",
          "project": {{
            "project_id": "{experiment_ngi_project_id}"
          }},
          "title": "{experiment_ngi_title}",
          "platform": {{
            "model_name": "{experiment_ngi_model_name}"
          }},
          "library": {{
            "sample": {{
              "sample_id": "{experiment_ngi_sample_id}"
            }},
            "application": "{experiment_ngi_application}",
            "sample_type": "{experiment_ngi_sample_type}",
            "library_kit": "{experiment_ngi_library_kit}",
            "is_paired": "{experiment_ngi_is_paired}"
          }}
        }}
    """

    MAPPING = {
        "experiment_ngi_alias": "experiment_alias",
        "experiment_ngi_project_id": "project_id",
        "experiment_ngi_title": "experiment_title",
        "experiment_ngi_model_name": "instrument_model_name",
        "experiment_ngi_sample_id": "sample_id",
        "experiment_ngi_application": "experiment_application",
        "experiment_ngi_sample_type": "experiment_sample_type",
        "experiment_ngi_library_kit": "experiment_library_kit",
        "experiment_ngi_is_paired": "read_configuration_paired"
    }


class SRAExperimentObj(ExperimentObj):

    model_source = "sra"

    JSON_STRUCTURE = """
        {{
          "alias": "{experiment_sra_alias}",
          "TITLE": "{experiment_sra_title}",
          "STUDY_REF": {{
            "refname": "{experiment_sra_study_refname}"
          }},
          "DESIGN": {{
            "SAMPLE_DESCRIPTOR": {{
              "refname": "{experiment_sra_sample_refname}"
            }},
            "LIBRARY_DESCRIPTOR": {{
              "LIBRARY_STRATEGY": "{experiment_sra_library_strategy}",
              "LIBRARY_SOURCE": "{experiment_sra_library_source}",
              "LIBRARY_SELECTION": "{experiment_sra_library_selection}",
              "LIBRARY_LAYOUT": {{
                "PAIRED": "{{}}"
              }}
            }}
          }},
          "PLATFORM": {{
            "{experiment_sra_platform}": {{
              "INSTRUMENT_MODEL": "{experiment_sra_instrument_model}"
            }}
          }}
        }}
    """

    XML_STRUCTURE = """
    <EXPERIMENT alias="{experiment_sra_alias}">
    <TITLE>{experiment_sra_title}</TITLE>
    <STUDY_REF refname="{experiment_sra_study_refname}"/>
    <DESIGN>
        <SAMPLE_DESCRIPTOR refname="{experiment_sra_sample_refname}"/>
        <LIBRARY_DESCRIPTOR>
            <LIBRARY_STRATEGY>{experiment_sra_library_strategy}</LIBRARY_STRATEGY>
            <LIBRARY_SOURCE>{experiment_sra_library_source}</LIBRARY_SOURCE>
            <LIBRARY_SELECTION>{experiment_sra_library_selection}</LIBRARY_SELECTION>
            <LIBRARY_LAYOUT>
                <PAIRED/>
            </LIBRARY_LAYOUT>
        </LIBRARY_DESCRIPTOR>
    </DESIGN>
    <PLATFORM>
        <{experiment_sra_platform}>
            <INSTRUMENT_MODEL>{experiment_sra_instrument_model}</INSTRUMENT_MODEL>
        </{experiment_sra_platform}>
    </PLATFORM>
    </EXPERIMENT>"""

    MANIFEST = [
        ["NAME", "{experiment_sra_alias}"],
        ["STUDY", "{experiment_sra_study_refname}"],
        ["PLATFORM", "{experiment_sra_platform}"],
        ["INSTRUMENT", "{experiment_sra_instrument_model}"],
        ["LIBRARY_STRATEGY", "{experiment_sra_library_strategy}"],
        ["LIBRARY_SOURCE", "{experiment_sra_library_source}"],
        ["LIBRARY_SELECTION", "{experiment_sra_library_selection}"],
        ["SAMPLE", "{experiment_sra_sample_refname}"]
    ]

    MAPPING = {
        "experiment_sra_alias": "experiment_alias",
        "experiment_sra_study_refname": "project_id",
        "experiment_sra_title": "experiment_title",
        "experiment_sra_instrument_model": "instrument_model",
        "experiment_sra_sample_refname": "sample_id",
        "experiment_sra_platform": "instrument_platform",
        "experiment_sra_library_strategy": "experiment_application_short",
        "experiment_sra_library_source": "experiment_sample_source",
        "experiment_sra_library_selection": "experiment_library_selection"
    }


class RunObj(ExperimentObj):

    fastq_cls = FastqFile

    def __init__(self, fields):
        super(RunObj, self).__init__(fields)
        self.fields["sequencing_run_fastq_files"] = [
            self.fastq_cls(
                fields={
                    "filepath": filepath,
                    "filetype": filetype,
                    "checksum": checksum,
                    "checksum_method": checksum_method
                }
            )
            for filepath, filetype, checksum, checksum_method in zip(
                self.fields["filepaths"],
                self.fields["filetypes"],
                self.fields["checksums"],
                self.fields["checksum_methods"])
        ]

    def to_json(self):
        fastq_json = [
            fastq.to_json()
            for fastq in self.fields["sequencing_run_fastq_files"]
        ]
        self.fields["fastq_files_json"] = json.dumps(
            fastq_json
        )
        return super(RunObj, self).to_json()

    def to_xml(self):
        fastq_xml = [
            fastq.to_xml()
            for fastq in self.fields["sequencing_run_fastq_files"]
        ]
        self.fields["fastq_files_xml"] = "".join(fastq_xml)
        return super(RunObj, self).to_xml()

    def to_manifest(self, extra_rows=None):
        extra_rows = extra_rows or []
        rows = [
            fastq.to_manifest()
            for fastq in self.fields["sequencing_run_fastq_files"]
        ] + extra_rows
        return super(RunObj, self).to_manifest(extra_rows=rows)


class NGIRunObj(RunObj):

    model_source = "ngi"
    fastq_cls = NGIFastqFile

    JSON_STRUCTURE = """
        {{
            "run_alias": "{sequencing_run_alias}",
            "run_center": "{sequencing_run_center}",
            "experiment": {{
                "alias": "{experiment_alias}",
                "project": {{
                    "project_id": "{project_id}"
                }},
                "sample": {{
                    "sample_id": "{sample_id}",
                    "sample_library_id": "{sample_library_id}",
                    "sample_library_tag": "{sample_library_tag}"
                }}
            }},
            "platform": {{
                "model_name": "{instrument_model_name}"
            }},
            "run_date": "{sequencing_run_date}",
            "run_attributes": [
                {{
                    "tag": "project_id",
                    "value": "{project_id}"
                }},
                {{
                    "tag": "sample_id",
                    "value": "{sample_id}"
                }},
                {{
                    "tag": "sample_library_id",
                    "value": "{sample_library_id}"
                }}
            ],
            "fastqfiles": {fastq_files_json}
        }}
    """

    MAPPING = {
        "sample_library_id": "sample_id",
        "fragment_size": "udf_fragment_size",
        "fragment_lower": "udf_fragment_lower",
        "fragment_upper": "udf_fragment_upper"
    }


class SRARunObj(RunObj):

    model_source = "sra"
    fastq_cls = SRAFastqFile

    JSON_STRUCTURE = """
        {{
            "center_name": "{sequencing_run_center}",
            "TITLE": "{sequencing_run_alias}",
            "EXPERIMENT_REF": {{
                "refname": "{experiment_alias}"
            }},
            "RUN_ATTRIBUTES": {{
                "RUN_ATTRIBUTE": [
                    {{
                        "TAG": "project_id",
                        "VALUE": "{project_id}"
                    }},
                    {{
                        "TAG": "sample_id",
                        "VALUE": "{sample_id}"
                    }},
                    {{
                        "TAG": "sample_library_id",
                        "VALUE": "{sample_library_id}"
                    }}
                ]
            }},
            "DATA_BLOCK": {{
                "FILES": {{
                    "FILE": {fastq_files_json}
                }}
            }},
            "run_date": "{sequencing_run_date}",
            "run_center": "{sequencing_run_center}"
        }}
    """

    XML_STRUCTURE = """
    <RUN center_name="{sequencing_run_center}" run_date="{sequencing_run_date}" run_center="{sequencing_run_center}">
        <TITLE>{sequencing_run_alias}</TITLE>
        <EXPERIMENT_REF refname="{experiment_alias}"/>
        <DATA_BLOCK>
            <FILES>{fastq_files_xml}
            </FILES>
        </DATA_BLOCK>
        <RUN_ATTRIBUTES>
            <RUN_ATTRIBUTE>
                <TAG>project_id</TAG>
                <VALUE>{project_id}</VALUE>
            </RUN_ATTRIBUTE>
            <RUN_ATTRIBUTE>
                <TAG>sample_id</TAG>
                <VALUE>{sample_id}</VALUE>
            </RUN_ATTRIBUTE>
            <RUN_ATTRIBUTE>
                <TAG>sample_library_id</TAG>
                <VALUE>{sample_library_id}</VALUE>
            </RUN_ATTRIBUTE>
        </RUN_ATTRIBUTES>
    </RUN>"""

    MANIFEST = []

    MAPPING = {
        "sample_library_id": "sample_id"
    }


class RunSetObj(MetaObj):

    sample_cls = MetaObj

    def __init__(self, fields):
        super(RunSetObj, self).__init__(fields)
        sample_csv_files = self.fields["sample_csv_files"]
        sample_csv_files = [sample_csv_files] \
            if type(sample_csv_files) is str else sample_csv_files
        self.fields["samples"] = [
            self.sample_cls.create_from_csv(
                sample_csv
            ) for sample_csv in sample_csv_files
        ]

    def to_json(self):
        samples_json = [
            sample.to_json()
            for sample in self.fields["samples"]
        ]
        self.fields["samples_json"] = json.dumps(
            samples_json
        )
        return super(RunSetObj, self).to_json()

    def to_xml(self):
        samples_xml = [
            sample.to_xml()
            for sample in self.fields["samples"]
        ]
        self.fields["samples_xml"] = "".join(samples_xml)
        return super(RunSetObj, self).to_xml()

    def to_manifest(self, extra_rows=None):
        extra_rows = extra_rows or []
        rows = [
            sample.to_manifest()
            for sample in self.fields["samples"]
        ] + extra_rows
        return super(RunSetObj, self).to_manifest(extra_rows=rows)

    def _export_to_format(self, super_fn, outdir, outname=None):
        outname = outname or self.fields['runfolder_name']
        return super_fn(outdir, outname=outname)

    def export_json(self, outdir, outname=None):
        return self._export_to_format(
            super(RunSetObj, self).export_json,
            outdir,
            outname=outname
        )

    def export_xml(self, outdir, outname=None):
        return self._export_to_format(
            super(RunSetObj, self).export_xml,
            outdir,
            outname=outname
        )

    def export_manifest(self, outdir, outname=None):
        return self._export_to_format(
            super(RunSetObj, self).export_manifest,
            outdir,
            outname=outname
        )

    def create_runfolder(self, outdir):
        runfolder_dir = os.path.join(outdir, self.fields["runfolder_name"])
        unaligned_dir = os.path.join(runfolder_dir, "Unaligned")
        md5_dir = os.path.join(runfolder_dir, "MD5")
        os.makedirs(unaligned_dir, exist_ok=True)
        os.makedirs(md5_dir, exist_ok=True)

        checksumfile = os.path.join(md5_dir, "checksums.md5")
        open(checksumfile, "w").close()
        samplesheet = os.path.join(runfolder_dir, self.fields["samplesheet"])
        samplesheet_entries = []
        for sample in self.fields["samples"]:
            sample.create_sample_folder(unaligned_dir)
            sample.write_checksum(checksumfile)
            samplesheet_entries.extend(
                sample.samplesheet_entries()
            )

        # sort the entries based on lane and then entry position
        def _cmp(a, b):
            return (a > b) - (a < b)

        sorted_entries = sorted(
            samplesheet_entries,
            key=cmp_to_key(
                lambda x, y:
                _cmp(x["entry_pos"], y["entry_pos"])
                if x["lane"] == y["lane"]
                else _cmp(x["lane"], y["lane"])
            )
        )

        columns = [
            "lane",
            "sample_id",
            "sample_name",
            "sample_plate",
            "sample_well",
            "i7_index_id",
            "index",
            "i5_index_id",
            "index2",
            "project_id",
            "description"
        ]
        with open(samplesheet, "w") as fh:
            fh.write(",".join(columns))
            for entry in sorted_entries:
                fh.write("\n")
                fh.write(
                    ",".join(
                        [
                            entry.get(col, "")
                            for col in columns
                        ]
                    )
                )


class SnpseqDataRunSetObj(RunSetObj):

    sample_cls = SnpseqDataSampleObj
    model_source = "snpseq"

    JSON_STRUCTURE = """
    {{
        "result": {{
            "name": "{flowcell_id}",
            "samples": {samples_json}
        }}
    }}
    """


class NGIRunSetObj(RunSetObj):

    sample_cls = NGIRunObj
    model_source = "ngi"

    JSON_STRUCTURE = """
    {{
        "runfolder_path": "{runfolder_path}",
        "runfolder_name": "{runfolder_name}",
        "flowcell_id": "{flowcell_id}",
        "samplesheet": "{samplesheet}",
        "run_parameters": "{run_parameters}",
        "checksum_method": "{checksum_method}",
        "platform": {{
            "model_name": "{instrument_model_name}"
        }},
        "run_date": "{run_date}",
        "sequencing_runs": {samples_json}
    }}
    """


class SRARunSetObj(RunSetObj):

    sample_cls = SRARunObj
    model_source = "sra"

    JSON_STRUCTURE = """
        {{
            "RUN": {samples_json}
        }}
    """

    XML_STRUCTURE = """<?xml version="1.0" encoding="UTF-8"?>
<RUN_SET>{samples_xml}
</RUN_SET>
    """

    MANIFEST = []


class ExperimentSetObj(RunSetObj):

    def _export_to_format(self, super_fn, outdir, outname=None):
        outname = f"{outname or ''}{self.fields['flowcell_id']}"
        return super_fn(outdir, outname=outname)

    def export_manifest(self, outdir, outname=None):
        # for all samples, do export_manifest but don't call super function
        manifest_files = [
            self._export_to_format(
                sample.export_manifest,
                outdir,
                outname=outname
            )
            for sample in self.fields["samples"]
        ]
        return manifest_files


class NGIExperimentSetObj(ExperimentSetObj):

    sample_cls = NGIExperimentObj
    model_source = "ngi"

    JSON_STRUCTURE = """
    {{
        "experiments": {samples_json}
    }}
    """


class SRAExperimentSetObj(ExperimentSetObj):

    sample_cls = SRAExperimentObj
    model_source = "sra"

    JSON_STRUCTURE = """
    {{
        "EXPERIMENT": {samples_json}
    }}
    """

    XML_STRUCTURE = """<?xml version="1.0" encoding="UTF-8"?>
<EXPERIMENT_SET>{samples_xml}
</EXPERIMENT_SET>
"""


if __name__ == '__main__':
    csvfile = sys.argv[1]
    obj = SnpseqDataRunSetObj.create_from_csv(csvfile)
    obj.export_json("export")

    obj = obj.to_class(NGIRunSetObj)
    obj.export_json("export")
    obj.create_runfolder("export")

    obj = obj.to_class(NGIExperimentSetObj)
    obj.export_json("export", outname="snpseq_data_")

    obj = obj.to_class(SRARunSetObj)
    obj.export_json("export")
    obj.export_xml("export")
    obj.export_manifest("export")

    obj = obj.to_class(SRAExperimentSetObj)
    obj.export_json("export", outname="snpseq_data_")
    obj.export_xml("export", outname="snpseq_data_")
    obj.export_manifest("export", outname="snpseq_data_")
