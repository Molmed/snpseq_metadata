import click
import json
import os

from snpseq_metadata.models.ngi_models import NGIFlowcell, NGIExperimentSet
from snpseq_metadata.models.lims_models import LIMSSequencingContainer
from snpseq_metadata.models.converter import Converter


def common_options(function):
    function = click.option(
        "-o",
        "--outdir",
        type=click.Path(dir_okay=True),
        default="current working directory",
        show_default=True,
    )(function)
    return function


@click.group()
def metadata():
    pass


@click.group()
def extract():
    pass


@click.group(chain=True)
@common_options
@click.argument("runfolder_path", nargs=1, type=click.Path(exists=True, dir_okay=True))
def runfolder(outdir, runfolder_path):
    pass


@click.group(chain=True)
@common_options
@click.argument(
    "snpseq_data_file", nargs=1, type=click.Path(exists=True, file_okay=True)
)
def snpseq_data(outdir, snpseq_data_file):
    pass


@runfolder.result_callback()
def extract_runfolder(processors, outdir, runfolder_path):
    ngi_flowcell = NGIFlowcell(runfolder_path=runfolder_path)
    outfile_prefix = os.path.join(outdir, ngi_flowcell.runfolder_name)
    for processor in processors:
        processor(ngi_flowcell, outfile_prefix)


@snpseq_data.result_callback()
def extract_snpseq_data(processors, outdir, snpseq_data_file):
    with open(snpseq_data_file, "rb") as fh:
        lims_experiments = LIMSSequencingContainer.from_json(json.load(fh))
        ngi_experiments = Converter.lims_to_ngi(lims_model=lims_experiments)
    outfile_prefix = os.path.join(
        outdir, ".".join(os.path.basename(snpseq_data_file).split(".")[0:-1])
    )
    for processor in processors:
        processor(ngi_experiments, outfile_prefix)


@click.command("json")
def extract_to_json():
    def processor(ngi_object, outfile_prefix):
        outfile = f"{outfile_prefix}.ngi.json"
        with open(outfile, "w") as fh:
            json.dump(ngi_object.to_json(), fh, indent=2)

    return processor


@click.group(chain=True)
@common_options
@click.argument("runfolder_data", nargs=1, type=click.File("rb"))
@click.argument("snpseq_data", nargs=1, type=click.File("rb"))
def export(outdir, runfolder_data, snpseq_data):
    pass


@export.result_callback()
def export_pipeline(processors, outdir, runfolder_data, snpseq_data):
    ngi_flowcell = NGIFlowcell.from_json(json_obj=json.load(runfolder_data))
    ngi_experiments = NGIExperimentSet.from_json(json_obj=json.load(snpseq_data))
    sra_run_set = Converter.ngi_to_sra(ngi_model=ngi_flowcell)
    sra_experiment_set = Converter.ngi_to_sra(ngi_experiments)

    projects = list(set(map(lambda exp: exp.study_ref, sra_experiment_set.experiments)))
    for project in projects:
        project_experiment_set = sra_experiment_set.restrict_to_study(study_ref=project)
        project_run_set = sra_run_set.restrict_to_experiments(
            experiments=project_experiment_set
        )
        for processor in processors:
            processor(str(project), project_experiment_set, project_run_set, outdir)


@click.command("xml")
def to_xml():
    def processor(project_id, experiment_set, run_set, outdir):
        for obj_type, sra_obj in [("experiment", experiment_set), ("run", run_set)]:
            outfile = os.path.join(outdir, f"{project_id}-{obj_type}.xml")
            with open(outfile, "w") as fh:
                fh.write(sra_obj.to_xml())

    return processor


@click.command("json")
def to_json():
    def processor(project_id, experiment_set, run_set, outdir):
        for obj_type, sra_obj in [("experiment", experiment_set), ("run", run_set)]:
            outfile = os.path.join(outdir, f"{project_id}-{obj_type}.json")
            with open(outfile, "w") as fh:
                json.dump(sra_obj.to_json(), fh, indent=2)

    return processor


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


export.add_command(to_xml)
export.add_command(to_json)
export.add_command(to_manifest)
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
        metadata.main(standalone_mode=False)
    except Exception as ex:
        print(str(ex))
        raise


if __name__ == "__main__":
    entry_point()
