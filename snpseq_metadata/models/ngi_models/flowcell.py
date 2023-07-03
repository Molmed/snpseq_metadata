import os
import datetime
import logging
import re
from typing import Dict, List, Optional, Type, TypeVar

import snpseq_metadata.utilities
from snpseq_metadata.exceptions import FastqFileLocationNotFoundException
from snpseq_metadata.models.ngi_models.attribute import NGIAttribute
from snpseq_metadata.models.ngi_models.metadata_model import NGIMetadataModel
from snpseq_metadata.models.ngi_models.experiment import NGIExperimentRef, NGIExperiment
from snpseq_metadata.models.ngi_models.file_models import NGIFastqFile
from snpseq_metadata.models.ngi_models.sequencing_run import NGIRun
from snpseq_metadata.models.ngi_models.sequencing_platform import (
    NGIIlluminaSequencingPlatform,
)

log = logging.getLogger(__name__)
T = TypeVar("T", bound="NGIFlowcell")


class NGIFlowcell(NGIMetadataModel):
    def __init__(
        self,
        runfolder_path: str,
        samplesheet: Optional[str] = None,
        run_parameters: Optional[str] = None,
        project_id: Optional[str] = None,
        sample_id: Optional[str] = None,
        sequencing_runs: List[NGIRun] = None,
    ) -> None:
        self.runfolder_path = runfolder_path
        self.runfolder_name = os.path.basename(self.runfolder_path)
        self.flowcell_id = self.get_flowcell_id_from_runfolder_name(self.runfolder_name)
        self.samplesheet = (
            os.path.basename(samplesheet)
            if samplesheet
            else snpseq_metadata.utilities.find_samplesheet(self.runfolder_path)[0]
        )
        self.run_parameters = (
            os.path.basename(run_parameters)
            if run_parameters
            else snpseq_metadata.utilities.find_run_parameters(self.runfolder_path)[0]
        )
        self.project_id = project_id
        self.sample_id = sample_id
        self.checksum_method = "MD5"
        self.platform = self.get_sequencing_platform()
        self.run_date = self.get_run_date()
        self.sequencing_runs = (
            sequencing_runs if sequencing_runs else self.get_sequencing_runs()
        )

    @staticmethod
    def get_flowcell_id_from_runfolder_name(runfolder_name: str) -> str:
        pattern = r"^((?:20)?\d{2}[01]\d[0123]\d)_([A-Z]+\d+)_(\d+)_([A-Z]?)([A-Z0-9-]+)$"
        m = re.match(pattern, runfolder_name)
        if m.groups():
            return m.group(5)

    def get_run_date(self) -> Optional[datetime.datetime]:
        datestr = self.runfolder_name.split("_")[0]
        try:
            return datetime.datetime.strptime(datestr[-6:], "%y%m%d")
        except ValueError:
            pass

    def get_sequencing_platform(self) -> NGIIlluminaSequencingPlatform:
        model_name = NGIIlluminaSequencingPlatform.model_name_from_id(
            model_id=self.runfolder_name.split("_")[1]
        )
        return NGIIlluminaSequencingPlatform(model_name=model_name)

    @classmethod
    def from_json(cls: Type[T], json_obj: Dict) -> T:
        sequencing_runs = [
            NGIRun.from_json(r) for r in json_obj.get("sequencing_runs", [])
        ]
        return cls(
            runfolder_path=json_obj.get("runfolder_path"),
            samplesheet=json_obj.get("samplesheet"),
            run_parameters=json_obj.get("run_parameters"),
            sequencing_runs=sequencing_runs,
        )

    def get_checksumfile(self) -> Optional[str]:
        checksumfile = os.path.join(
            self.runfolder_path, self.checksum_method, "checksums.md5"
        )
        return checksumfile if os.path.exists(checksumfile) else None

    def get_fastqdir_for_experiment_ref(self, experiment_ref: NGIExperimentRef) -> str:
        fastqdir = self.runfolder_path
        patterns = [
            ["Unaligned", "Demultiplexing"],
            [
                experiment_ref.project.project_id,
                f"Project_{experiment_ref.project.project_id}",
            ],
            [
                experiment_ref.sample.sample_library_id or experiment_ref.sample.sample_id,
                f"Sample_"
                f"{experiment_ref.sample.sample_library_id or experiment_ref.sample.sample_id}"
            ],
        ]
        try:
            for pattern in patterns:
                fastqdir = os.path.join(
                    fastqdir,
                    next(
                        filter(
                            lambda d: os.path.isdir(os.path.join(fastqdir, d))
                            and d in pattern,
                            os.listdir(fastqdir),
                        )
                    ),
                )
        except (IndexError, StopIteration):
            raise FastqFileLocationNotFoundException(
                sample_project=experiment_ref.project.project_id,
                sample_id=experiment_ref.sample.sample_id,
                search_path=fastqdir,
            )

        return fastqdir

    def get_experiments(self) -> List[NGIExperimentRef]:
        samplesheet_data = snpseq_metadata.utilities.parse_samplesheet_data(
            os.path.join(self.runfolder_path, self.samplesheet)
        )
        experiments = []
        for samplesheet_row in samplesheet_data:
            experiment = NGIExperimentRef.from_samplesheet_row(samplesheet_row)
            if all(
                [
                    experiment not in experiments,
                    self.project_id is None
                    or experiment.project.project_id == self.project_id,
                    self.sample_id is None
                    or experiment.sample.sample_id == self.sample_id,
                ]
            ):
                experiments.append(experiment)
        return experiments

    def get_files_for_experiment_ref(
        self, experiment_ref: NGIExperimentRef
    ) -> List[NGIFastqFile]:
        fastqdir = self.get_fastqdir_for_experiment_ref(experiment_ref)
        fastq_extensions = ["fastq.gz", "fastq", "fq.gz", "fq"]
        fastqfiles = []
        for fastqfile in filter(
            lambda f: any(map(f.endswith, fastq_extensions)),
            os.listdir(fastqdir),
        ):
            fastqpath = os.path.join(fastqdir, fastqfile)
            querypath = os.path.relpath(fastqpath, os.path.dirname(self.runfolder_path))
            checksum = None
            checksum_file = self.get_checksumfile()
            if checksum_file:
                try:
                    checksum = snpseq_metadata.utilities.lookup_checksum_from_file(
                        checksumfile=checksum_file, querypath=querypath
                    )
                except OSError:
                    pass
            if checksum is None:
                checksum = snpseq_metadata.utilities.calculate_checksum_from_file(
                    queryfile=fastqpath, method=self.checksum_method
                )
            fastqfiles.append(
                NGIFastqFile(
                    filepath=fastqpath,
                    checksum=checksum,
                    checksum_method=self.checksum_method,
                )
            )
        return sorted(fastqfiles, key=lambda f: f.filepath)

    def get_sequencing_runs(self) -> List[NGIRun]:
        return [
            self.get_sequencing_run_for_experiment_ref(experiment_ref=experiment_ref)
            for experiment_ref in self.get_experiments()
        ]

    def get_sequencing_run_for_experiment_ref(
        self, experiment_ref: NGIExperimentRef
    ) -> NGIRun:
        try:
            fastqfiles = self.get_files_for_experiment_ref(experiment_ref=experiment_ref)
        except FastqFileLocationNotFoundException as ex:
            log.warning(ex)
            fastqfiles = []

        run_attribute = [
            NGIAttribute(
                tag="project_id",
                value=experiment_ref.project.project_id
            ),
            NGIAttribute(
                tag="sample_id",
                value=experiment_ref.sample.sample_id
            )]
        if experiment_ref.sample.sample_library_id:
            run_attribute.append(
                NGIAttribute(
                    tag="sample_library_id",
                    value=experiment_ref.sample.sample_library_id
                ))
        return NGIRun(
            run_alias=f"{experiment_ref.alias}-{self.flowcell_id}",
            experiment=experiment_ref,
            platform=self.platform,
            run_date=self.run_date,
            fastqfiles=fastqfiles,
            run_attributes=run_attribute
        )

    def get_sequencing_run_for_experiment(
        self, experiment: NGIExperiment
    ) -> Optional[NGIRun]:
        try:
            return next(
                filter(
                    lambda run: run.experiment.is_reference_to(experiment),
                    self.sequencing_runs,
                )
            )
        except StopIteration:
            pass
