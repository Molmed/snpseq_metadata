import click
import json
import os

from snpseq_metadata.models.ngi_models import NGIFlowcell
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


@click.group(chain=True)
@common_options
@click.argument("runfolder", nargs=1, type=click.Path(exists=True, dir_okay=True))
def extract(outdir, runfolder):
    pass


@extract.result_callback()
def extract_pipeline(processors, outdir, runfolder):
    ngi_flowcell = NGIFlowcell(runfolder_path=runfolder)
    outfile_prefix = os.path.join(outdir, ngi_flowcell.runfolder_name)
    for processor in processors:
        processor(ngi_flowcell, outfile_prefix)


@click.command("json")
def extract_to_json():
    def processor(ngi_flowcell, outfile_prefix):
        outfile = f"{outfile_prefix}.json"
        with open(outfile, "w") as fh:
            json.dump(ngi_flowcell.to_json(), fh, indent=2)

    return processor


@click.group(chain=True)
@common_options
@click.argument("runfolder", nargs=1, type=click.File("rb"))
@click.argument("data", nargs=1, type=click.File("rb"))
def export(outdir, runfolder, data):
    pass


@export.result_callback()
def export_pipeline(processors, outdir, runfolder, data):
    ngi_flowcell = NGIFlowcell.from_json(json_obj=json.load(runfolder))
    lims_experiments = LIMSSequencingContainer.from_json(json.load(data))
    ngi_experiments = Converter.lims_to_ngi(lims_model=lims_experiments)
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
            sample_id = str(sra_run.experiment.library.sample)
            outfile = os.path.join(outdir, f"{project_id}-{sample_id}.manifest")
            with open(outfile, "w") as fh:
                for row in sra_run.to_manifest():
                    fh.write("\t".join(row))
                    fh.write("\n")

    return processor


export.add_command(to_xml)
export.add_command(to_json)
export.add_command(to_manifest)
metadata.add_command(export)

extract.add_command(extract_to_json)
metadata.add_command(extract)

if __name__ == "__main__":
    metadata()
