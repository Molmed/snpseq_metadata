import click
import csv
import json
import os

from snpseq_metadata.models.ngi_models import NGIFlowcell, NGIExperimentSet
from snpseq_metadata.models.lims_models import LIMSSequencingContainer
from snpseq_metadata.models.sra_models import SRAMetadataModel
from snpseq_metadata.models.converter import Converter, ConvertExperimentSet


def common_options(function):
    function = click.option(
        "-o",
        "--outdir",
        type=click.Path(dir_okay=True),
        default=os.curdir,
        show_default=True,
    )(function)
    return function


# snpseq_metadata ...
@click.group()
def metadata():
    pass


# snpseq_metadata extract ...
@click.group()
def extract():
    pass


# snpseq_metadata extract runfolder ...
@click.group(chain=True)
@common_options
@click.argument("runfolder_path", nargs=1, type=click.Path(exists=True, dir_okay=True))
def runfolder(outdir, runfolder_path):
    pass


# snpseq_metadata extract snpseq_data ...
@click.group(chain=True)
@common_options
@click.argument(
    "snpseq_data_file", nargs=1, type=click.Path(exists=True, file_okay=True)
)
def snpseq_data(outdir, snpseq_data_file):
    pass


@runfolder.result_callback()
def extract_runfolder(processors, outdir, runfolder_path):
    # create NGI objects by parsing the supplied runfolder path and save to file
    ngi_flowcell = NGIFlowcell(runfolder_path=runfolder_path)
    outfile_prefix = os.path.join(outdir, ngi_flowcell.runfolder_name)
    for processor in processors:
        processor(ngi_flowcell, outfile_prefix)


@snpseq_data.result_callback()
def extract_snpseq_data(processors, outdir, snpseq_data_file):
    with open(snpseq_data_file, "rb") as fh:
        # create LIMS objects from the supplied JSON file
        # (extracted from Clarity by snpseq_data service)
        lims_experiments = LIMSSequencingContainer.from_json(json.load(fh))

        # convert the LIMS objects to NGI objects and save to file
        ngi_experiments = ConvertExperimentSet.lims_to_ngi(lims_model=lims_experiments)
    outfile_prefix = os.path.join(
        outdir, ".".join(os.path.basename(snpseq_data_file).split(".")[0:-1])
    )
    for processor in processors:
        processor(ngi_experiments, outfile_prefix)


# snpseq_metadata extract ... json
@click.command("json")
def extract_to_json():
    def processor(ngi_object, outfile_prefix):
        outfile = f"{outfile_prefix}.ngi.json"
        with open(outfile, "w") as fh:
            json.dump(ngi_object.to_json(), fh, indent=2)

    return processor


# snpseq_metadata export ...
@click.group(chain=True)
@common_options
@click.argument("runfolder_data", nargs=1, type=click.File("rb"))
@click.argument("snpseq_data", nargs=1, type=click.File("rb"))
def export(outdir, runfolder_data, snpseq_data):
    pass


@export.result_callback()
def export_pipeline(processors, outdir, runfolder_data, snpseq_data):
    # create NGI objects from the supplied JSON files
    ngi_flowcell = NGIFlowcell.from_json(json_obj=json.load(runfolder_data))
    ngi_experiments = NGIExperimentSet.from_json(json_obj=json.load(snpseq_data))

    # convert the NGI objects to SRA objects for export
    sra_run_set = Converter.ngi_to_sra(ngi_model=ngi_flowcell)
    sra_experiment_set = Converter.ngi_to_sra(ngi_experiments)

    projects = list(
        set(
            map(
                lambda exp: exp.study_ref,
                sra_experiment_set.experiments
            )
        )
    )
    for project in projects:
        # restrict the experiment_set and run_set to only include the objects corresponding to the
        # project. Will also match up the corresponding run and experiment objects
        project_experiment_set = sra_experiment_set.restrict_to_study(
            study_ref=project
        )
        project_run_set = sra_run_set.restrict_to_experiments(
            experiments=project_experiment_set
        )
        for processor in processors:
            processor(str(project), project_experiment_set, project_run_set, outdir)


# snpseq_metadata export ... xml
@click.command("xml")
def to_xml():
    def processor(project_id, experiment_set, run_set, outdir):
        for obj_type, sra_obj in [("experiment", experiment_set), ("run", run_set)]:
            outfile = os.path.join(outdir, f"{project_id}-{obj_type}.xml")
            with open(outfile, "w") as fh:
                fh.write(sra_obj.to_xml())

    return processor


# snpseq_metadata export ... json
@click.command("json")
def to_json():
    def processor(project_id, experiment_set, run_set, outdir):
        for obj_type, sra_obj in [("experiment", experiment_set), ("run", run_set)]:
            outfile = os.path.join(outdir, f"{project_id}-{obj_type}.json")
            with open(outfile, "w") as fh:
                json.dump(sra_obj.to_json(), fh, indent=2)

    return processor


# snpseq_metadata export ... manifest
@click.command("manifest")
def to_manifest():
    def processor(project_id, experiment_set, run_set, outdir):
        for sra_run in run_set.runs:
            outfile = os.path.join(
                outdir, f"{sra_run.experiment.alias}.manifest"
            )
            with open(outfile, "w") as fh:
                for row in sra_run.experiment.to_manifest() + sra_run.to_manifest():
                    fh.write("\t".join(row))
                    fh.write("\n")

    return processor


# snpseq_metadata export ... tsv
@click.command("tsv")
def to_tsv():
    def processor(project_id, experiment_set, run_set, outdir):
        project_tsv_list = []
        # add all samples to the project tsv list
        for sra_run in run_set.runs:
            experiment_tsv = sra_run.experiment.to_tsv()
            run_tsv = sra_run.to_tsv()
            # combine each entry in the experiment_tsv with all entries in run_tsv
            for experiment_dict in experiment_tsv:
                for run_dict in run_tsv:
                    tsv_dict = {}
                    tsv_dict.update(experiment_dict)
                    tsv_dict.update(run_dict)
                    project_tsv_list.append(tsv_dict)

        outfile = os.path.join(
            outdir, f"{project_id}.metadata.ena.tsv"
        )
        # set the dialect separator to tab
        dialect_tab = csv.unix_dialect
        dialect_tab.delimiter = "\t"

        # write the first line specifying the file type
        try:
            with open(outfile, "w", newline='') as fh:
                w = csv.writer(
                    fh,
                    dialect=dialect_tab
                )
                w.writerow(
                    [
                        "FileType",
                        project_tsv_list[0].get("FileType", ''),
                        "Read submission file type",
                    ]
                )

            # write the data header and rows
            with open(outfile, "a", newline='') as fh:
                dw = csv.DictWriter(
                    fh,
                    SRAMetadataModel.sra_tsv_fields,
                    dialect=dialect_tab,
                    restval='',
                    extrasaction='ignore',
                )
                dw.writeheader()
                dw.writerows(project_tsv_list)
        except IndexError:
            print(f"No TSV data to export for {project_id}")

    return processor


export.add_command(to_xml)
export.add_command(to_json)
export.add_command(to_manifest)
export.add_command(to_tsv)
metadata.add_command(export)

snpseq_data.add_command(extract_to_json)
runfolder.add_command(extract_to_json)
extract.add_command(snpseq_data)
extract.add_command(runfolder)
metadata.add_command(extract)


def entry_point():
    # catch any exceptions and write a comprehensive message to stdout and raise the exception for
    # stacktrace and exit code etc.
    try:
        return metadata.main(standalone_mode=False, obj={})
    except Exception as ex:
        print(str(ex))
        raise


if __name__ == "__main__":
    entry_point()
