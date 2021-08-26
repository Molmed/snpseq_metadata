from typing import ClassVar, Tuple, Type, TypeVar, Optional

from snpseq_metadata.models.ngi_models import (
    NGIMetadataModel,
    NGISampleDescriptor,
    NGIStudyRef,
    NGIRun,
    NGIIlluminaSequencingPlatform,
    NGIFlowcell,
    NGIResultFile,
    NGIExperimentRef,
    NGIExperiment,
    NGIExperimentSet,
    NGILibrary,
)
from snpseq_metadata.models.sra_models import (
    SRAMetadataModel,
    SRASampleDescriptor,
    SRAStudyRef,
    SRARun,
    SRAIlluminaSequencingPlatform,
    SRARunSet,
    SRAResultFile,
    SRAExperimentRef,
    SRAExperiment,
    SRAExperimentSet,
    SRALibrary,
)

from snpseq_metadata.models.lims_models import (
    LIMSSequencingContainer,
    LIMSSample,
    LIMSMetadataModel,
)
from snpseq_metadata.models.ngi_to_sra_library_mapping import (
    ApplicationSampleTypeMapping,
)
from snpseq_metadata.exceptions import (
    LibraryStrategyNotRecognizedException,
    InstrumentModelNotRecognizedException,
    SomethingNotRecognizedException,
)

T = TypeVar("T", bound="Converter")


class Converter:
    """
    The main class for doing conversions between models. The idea is that the conversion is made by
    calling the appropriate class method and supplying the model instance to convert from. This
    pattern allows the models to be implemented independently of each other, i.e. the model modules
    themselves need not know anything about any other model.

    Example:
        sra_library_instance = Converter.ngi_to_sra(ngi_library_instance)
    """

    ngi_model_class: ClassVar[Type] = NGIMetadataModel
    sra_model_class: ClassVar[Type] = SRAMetadataModel
    lims_model_class: ClassVar[Type] = LIMSMetadataModel

    @classmethod
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        """
        Entry point to convert a NGI model class to a corresponding SRA model class. The method will
        iterate over subclasses to locate a subclass whose ngi_model_class matches the supplied
        ngi_model.

        :param ngi_model: an instance of NGIMetadataModel or any of its subclasses
        :return: an instance of a subclass of SRAMetadataModel, corresponding to the supplied
        ngi_model or None if no matching conversion could be made
        """
        # iterate over all subclasses to find one whose ngi_nodel_class variable matches the
        # supplied ngi_model, but only if this is called in the base class
        if cls == Converter:
            for subclass in cls.__subclasses__():
                if isinstance(ngi_model, subclass.ngi_model_class):
                    sra_model = subclass.ngi_to_sra(ngi_model=ngi_model)
                    if sra_model:
                        return sra_model

    @classmethod
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        """
        Entry point to convert a LIMS model class to a corresponding NGI model class. The method
        will iterate over subclasses to locate a subclass whose lims_model_class matches the
        supplied lims_model.

        :param lims_model: an instance of LIMSMetadataModel or any of its subclasses
        :return: an instance of a subclass of NGIMetadataModel, corresponding to the supplied
        lims_model or None if no matching conversion could be made
        """
        # iterate over all subclasses to find one whose lims_nodel_class variable matches the
        # supplied lims_model, but only if this is called in the base class
        if cls == Converter:
            for subclass in cls.__subclasses__():
                if isinstance(lims_model, subclass.lims_model_class):
                    ngi_model = subclass.lims_to_ngi(lims_model=lims_model)
                    if ngi_model:
                        return ngi_model


class ConvertSampleDescriptor(Converter):
    """
    Conversion between NGISampleDescriptor, SRASampleDescriptor and LIMSSample
    """

    ngi_model_class = NGISampleDescriptor
    sra_model_class = SRASampleDescriptor
    lims_model_class = LIMSSample

    @classmethod
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(refname=ngi_model.sample_id)

    @classmethod
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            return cls.ngi_model_class(sample_id=lims_model.sample_id)


class ConvertStudyRef(Converter):
    """
    Conversion between NGIStudyRef, SRAStudyRef and LIMSSample
    """

    ngi_model_class = NGIStudyRef
    sra_model_class = SRAStudyRef
    lims_model_class = LIMSSample

    @classmethod
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(refname=ngi_model.project_id)

    @classmethod
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            return cls.ngi_model_class(project_id=lims_model.project_id)


class ConvertRun(Converter):
    """
    Conversion between NGIRun and SRARun
    """

    ngi_model_class = NGIRun
    sra_model_class = SRARun

    @classmethod
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(
                run_alias=ngi_model.run_alias,
                run_date=ngi_model.run_date,
                experiment=Converter.ngi_to_sra(ngi_model.experiment.get_reference()),
                run_center=ngi_model.run_center,
                fastqfiles=[
                    Converter.ngi_to_sra(n) for n in ngi_model.fastqfiles or []
                ],
            )


class ConvertSequencingPlatform(Converter):
    """
    Conversion between NGIIlluminaSequencingPlatform, SRAIlluminaSequencingPlatform and LIMSSample
    """

    ngi_model_class = NGIIlluminaSequencingPlatform
    sra_model_class = SRAIlluminaSequencingPlatform
    lims_model_class = LIMSSample

    @classmethod
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(model_name=ngi_model.model_name)

    @classmethod
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            try:
                return cls.ngi_model_class(
                    model_name=lims_model.udf_sequencing_instrument
                )
            except AttributeError:
                raise InstrumentModelNotRecognizedException(needle="None")


class ConvertRunSet(Converter):
    """
    Conversion between NGIFlowcell and SRARunSet
    """

    ngi_model_class = NGIFlowcell
    sra_model_class = SRARunSet

    @classmethod
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(
                runs=[Converter.ngi_to_sra(f) for f in ngi_model.sequencing_runs or []]
            )


class ConvertResultFile(Converter):
    """
    Conversion between NGIResultFile and SRAResultFile
    """

    ngi_model_class = NGIResultFile
    sra_model_class = SRAResultFile

    @classmethod
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(
                filepath=ngi_model.filepath,
                filetype=ngi_model.filetype,
                checksum=ngi_model.checksum,
                checksum_method=ngi_model.checksum_method,
            )


class ConvertExperimentRef(Converter):
    """
    Conversion between NGIExperimentRef, SRAExperimentRef and LIMSSample
    """

    ngi_model_class = NGIExperimentRef
    sra_model_class = SRAExperimentRef
    lims_model_class = LIMSSample

    @classmethod
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(experiment_name=ngi_model.alias)

    @classmethod
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            sample = ConvertSampleDescriptor.lims_to_ngi(lims_model=lims_model)
            project = ConvertStudyRef.lims_to_ngi(lims_model=lims_model)
            platform = ConvertSequencingPlatform.lims_to_ngi(lims_model=lims_model)
            alias = f"{project.project_id}-{sample.sample_id}-{platform.model_name}"
            return cls.ngi_model_class(alias=alias, sample=sample, project=project)


class ConvertExperimentSet(Converter):
    """
    Conversion between NGIExperimentSet, SRAExperimentSet and LIMSSequencingContainer
    """

    ngi_model_class = NGIExperimentSet
    sra_model_class = SRAExperimentSet
    lims_model_class = LIMSSequencingContainer

    @classmethod
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(
                experiments=[
                    Converter.ngi_to_sra(ngi_experiment)
                    for ngi_experiment in ngi_model.experiments or []
                ]
            )

    @classmethod
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            return cls.ngi_model_class(
                list(
                    filter(
                        lambda e: e is not None,
                        [
                            ConvertExperiment.lims_to_ngi(lims_model=lims_sample)
                            for lims_sample in lims_model.samples or []
                        ],
                    )
                )
            )


class ConvertLibrary(Converter):
    """
    Conversion between NGILibrary, SRALibrary and LIMSSample
    """

    ngi_model_class = NGILibrary
    sra_model_class = SRALibrary
    lims_model_class = LIMSSample

    @classmethod
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            (
                library_selection,
                library_source,
                library_strategy,
            ) = cls.objects_from_application_info(
                application=ngi_model.application,
                sample_type=ngi_model.sample_type,
                library_kit=ngi_model.library_kit,
            )
            return cls.sra_model_class.create_object(
                sample=Converter.ngi_to_sra(ngi_model.sample),
                description=ngi_model.description,
                strategy=library_strategy,
                source=library_source,
                selection=library_selection,
                is_paired=ngi_model.is_paired,
            )

    @classmethod
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            sample = ConvertSampleDescriptor.lims_to_ngi(lims_model=lims_model)
            application = lims_model.udf_application
            sample_type = lims_model.udf_sample_type
            library_kit = lims_model.udf_library_preparation_kit
            description = None
            is_paired = lims_model.is_paired()
            return cls.ngi_model_class(
                sample=sample,
                description=description,
                application=application,
                sample_type=sample_type,
                library_kit=library_kit,
                is_paired=is_paired,
            )

    @classmethod
    def objects_from_application_info(
        cls: Type[T], application: str, sample_type: str, library_kit: str
    ) -> Tuple[str, str, str]:
        """
        Look up the SRA values for library strategy, source and selection corresponding to the
        supplied NGI application, sample_type and library_kit, by using the
        ApplicationSampleTypeMapping class.

        :param application: the sample application, specified in e.g. Clarity LIMS
        :param sample_type: the sample type, specified in e.g. Clarity LIMS
        :param library_kit: the library kit, specified in e.g. Clarity LIMS
        :return: a tuple with the corresponding SRA library selection, library source and libnrary
        strategy
        :raises LibraryStrategyNotRecognizedException: if corresponding values could not be
        determined
        """
        mapping_obj = ApplicationSampleTypeMapping.create_object(
            application=application,
            sample_type=sample_type,
            sample_prep_kit=library_kit,
        )
        if not mapping_obj:
            raise LibraryStrategyNotRecognizedException(
                needle=f"{application}:{sample_type}:{library_kit}"
            )
        return (
            mapping_obj.sra_library_selection.value,
            mapping_obj.sra_library_source.value,
            mapping_obj.sra_library_strategy.value,
        )


class ConvertExperiment(Converter):
    """
    Conversion between NGIExperiment, SRAExperiment and LIMSSample
    """

    ngi_model_class = NGIExperiment
    sra_model_class = SRAExperiment
    lims_model_class = LIMSSample

    @classmethod
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(
                alias=ngi_model.alias,
                title=ngi_model.title,
                study_ref=Converter.ngi_to_sra(ngi_model=ngi_model.project),
                platform=Converter.ngi_to_sra(ngi_model=ngi_model.platform),
                library=Converter.ngi_to_sra(ngi_model=ngi_model.library),
            )

    @classmethod
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            try:
                sample = ConvertSampleDescriptor.lims_to_ngi(lims_model=lims_model)
                project = ConvertStudyRef.lims_to_ngi(lims_model=lims_model)
                platform = ConvertSequencingPlatform.lims_to_ngi(lims_model=lims_model)
                alias = f"{project.project_id}-{sample.sample_id}-{platform.model_name}"
                library = ConvertLibrary.lims_to_ngi(lims_model=lims_model)
                title = f"{project.project_id} - {sample.sample_id} - {library.application} - {library.sample_type} - {library.library_kit}"
            except SomethingNotRecognizedException as ex:
                print(ex)
                return None
            return cls.ngi_model_class(
                alias=alias,
                title=title,
                project=project,
                platform=platform,
                library=library,
            )
