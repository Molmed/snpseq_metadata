
import logging
from functools import wraps
from typing import ClassVar, List, Tuple, Type, TypeVar, Optional

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
    NGILibraryLayout,
    NGIAttribute,
    NGIPool,
    NGIPoolMember,
    NGIReadLabel,
    NGILibraryKit,
    NGISource,
    NGIApplication,
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
    SRALibraryLayout,
    SRAAttribute
)

from snpseq_metadata.models.lims_models import (
    LIMSSequencingContainer,
    LIMSSample,
    LIMSMetadataModel,
    LIMSLibraryKit,
    LIMSApplication,
    LIMSSampleType,
)
from snpseq_metadata.models.ngi_to_sra_mapping import ModelMapper

from snpseq_metadata.exceptions import (
    LibraryStrategyNotRecognizedException,
    InstrumentModelNotRecognizedException,
    ModelConversionException
)

LOG = logging.getLogger(__name__)
T = TypeVar("T", bound="Converter")


# These exceptions are defined here, since this class will know about the different model systems
class NGIModelConversionException(ModelConversionException):
    pass


class SRAModelConversionException(ModelConversionException):
    pass


def catch_exception(f):
    """
    decorator function that will catch Exceptions raised by the decorated method, log the exception
    and raise a customized exception
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ModelConversionException:
            raise
        except Exception as ex:
            if f.__name__ == "ngi_to_sra":
                exception_cls = SRAModelConversionException
                source_cls = args[0].ngi_model_class
                target_cls = args[0].sra_model_class
            elif f.__name__ == "lims_to_ngi":
                exception_cls = NGIModelConversionException
                source_cls = args[0].lims_model_class
                target_cls = args[0].ngi_model_class
            else:
                exception_cls = ModelConversionException
                source_cls = None
                target_cls = None
            raised_ex = exception_cls(
                source=source_cls,
                target=target_cls,
                reason=ex,
            )
            LOG.debug(raised_ex)
            raise raised_ex from ex

    return wrapper


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
    @catch_exception
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        """
        Entry point to convert a NGI model class to a corresponding SRA model class. The method will
        iterate over subclasses to locate a subclass whose ngi_model_class matches the supplied
        ngi_model.

        Args:
            ngi_model: an instance of NGIMetadataModel or any of its subclasses

        Returns:
            an instance of a subclass of SRAMetadataModel, corresponding to the supplied
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
            # conversion was unsuccessful, raise the exception
            raise SRAModelConversionException(
                source=type(ngi_model),
                target=cls.sra_model_class
            )

    @classmethod
    @catch_exception
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        """
        Entry point to convert a LIMS model class to a corresponding NGI model class. The method
        will iterate over subclasses to locate a subclass whose lims_model_class matches the
        supplied lims_model.

        Args:
            lims_model: an instance of LIMSMetadataModel or any of its subclasses

        Returns:
            an instance of a subclass of NGIMetadataModel, corresponding to the supplied
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
            # conversion was unsuccessful, raise the exception
            raise NGIModelConversionException(
                source=type(lims_model),
                target=cls.ngi_model_class
            )


class ConvertSampleDescriptor(Converter):
    """
    Conversion between NGISampleDescriptor, SRASampleDescriptor and LIMSSample
    """

    ngi_model_class = NGISampleDescriptor
    sra_model_class = SRASampleDescriptor
    lims_model_class = LIMSSample

    @classmethod
    @catch_exception
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(refname=ngi_model.sample_name)

    @classmethod
    @catch_exception
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            try:
                sample_library_id = lims_model.udf_sample_library_id
            except AttributeError:
                sample_library_id = f"{lims_model.sample_name}_{lims_model.udf_id}"
            return cls.ngi_model_class(
                sample_name=lims_model.sample_name,
                sample_id=lims_model.sample_id,
                sample_library_id=sample_library_id,
                sample_library_tag=lims_model.index_tag())
        return None


class ConvertReadLabel(Converter):
    """
    Conversion between NGIReadLabel and LIMSSample
    """

    ngi_model_class = NGIReadLabel
    sra_model_class = SRASampleDescriptor
    lims_model_class = LIMSSample

    @classmethod
    @catch_exception
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        pass

    @classmethod
    @catch_exception
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[List[ngi_model_class]]:
        sample = ConvertPoolMember.lims_to_ngi(lims_model)
        if sample:
            return sample.read_labels()


class ConvertPoolMember(ConvertSampleDescriptor):
    """
    Conversion between NGIPoolMember and LIMSSample
    """

    ngi_model_class = NGIPoolMember
    sra_model_class = SRASampleDescriptor
    lims_model_class = LIMSSample


class ConvertPool(Converter):
    """
    Conversion between NGIPool and LIMSSample
    """

    ngi_model_class = NGIPool
    sra_model_class = SRASampleDescriptor
    lims_model_class = LIMSSequencingContainer

    @classmethod
    @catch_exception
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            samples = []
            for lims_sample in lims_model.samples or []:
                try:
                    samples.append(
                        ConvertPoolMember.lims_to_ngi(
                            lims_model=lims_sample
                        )
                    )
                except ModelConversionException as ex:
                    # log this as an error but continue with the other samples
                    LOG.error(f"{lims_sample} skipped - {str(ex)}")

            return cls.ngi_model_class(
                samples=list(
                    filter(
                        lambda s: s is not None,
                        samples
                    )
                )
            )


class ConvertStudyRef(Converter):
    """
    Conversion between NGIStudyRef, SRAStudyRef and LIMSSample
    """

    ngi_model_class = NGIStudyRef
    sra_model_class = SRAStudyRef
    lims_model_class = LIMSSample

    @classmethod
    @catch_exception
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(refname=ngi_model.project_id)

    @classmethod
    @catch_exception
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
    @catch_exception
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
                run_attributes=[
                    Converter.ngi_to_sra(run_attribute)
                    for run_attribute in ngi_model.run_attributes or []
                ] or None
            )


class ConvertSequencingPlatform(Converter):
    """
    Conversion between NGIIlluminaSequencingPlatform, SRAIlluminaSequencingPlatform and LIMSSample
    """

    ngi_model_class = NGIIlluminaSequencingPlatform
    sra_model_class = SRAIlluminaSequencingPlatform
    lims_model_class = LIMSSample

    @classmethod
    @catch_exception
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(model_name=ngi_model.model_name)

    @classmethod
    @catch_exception
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
    @catch_exception
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
    @catch_exception
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
    @catch_exception
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(experiment_name=ngi_model.alias)

    @classmethod
    @catch_exception
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            sample = ConvertSampleDescriptor.lims_to_ngi(lims_model=lims_model)
            project = ConvertStudyRef.lims_to_ngi(lims_model=lims_model)
            alias = lims_model.udf_sample_library_id
            return cls.ngi_model_class(
                alias=alias,
                sample=sample,
                project=project)


class ConvertExperimentSet(Converter):
    """
    Conversion between NGIExperimentSet, SRAExperimentSet and LIMSSequencingContainer
    """

    ngi_model_class = NGIExperimentSet
    sra_model_class = SRAExperimentSet
    lims_model_class = LIMSSequencingContainer

    @classmethod
    @catch_exception
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
    @catch_exception
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            experiments = []
            for lims_sample in lims_model.samples or []:
                try:
                    experiment = ConvertExperiment.lims_to_ngi(
                        lims_model=lims_sample
                    )
                    if experiment is not None:
                        experiments.append(experiment)
                except ModelConversionException as ex:
                    # log this as an error but continue with the other samples
                    LOG.error(f"{lims_sample} skipped - {str(ex)}")

            return cls.ngi_model_class(experiments=experiments)


class ConvertLibraryLayout(Converter):
    """
    Conversion between NGILibraryLayout, SRALibraryLayout and LIMSSample
    """

    ngi_model_class = NGILibraryLayout
    sra_model_class = SRALibraryLayout
    lims_model_class = LIMSSample

    @classmethod
    @catch_exception
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(
                is_paired=ngi_model.is_paired,
                fragment_size=ngi_model.fragment_size,
                fragment_upper=ngi_model.fragment_upper,
                fragment_lower=ngi_model.fragment_lower,
                target_insert_size=ngi_model.target_insert_size
            )

    @classmethod
    @catch_exception
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            return cls.ngi_model_class(
                is_paired=lims_model.is_paired(),
                fragment_size=lims_model.udf_fragment_size,
                fragment_lower=lims_model.udf_fragment_lower,
                fragment_upper=lims_model.udf_fragment_upper,
                target_insert_size=lims_model.udf_insert_size_bp
            )


class ConvertLibrary(Converter):
    """
    Conversion between NGILibrary, SRALibrary and LIMSSample
    """

    ngi_model_class = NGILibrary
    sra_model_class = SRALibrary
    lims_model_class = LIMSSample

    @classmethod
    @catch_exception
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            # use the ngi_to_sra_mapping.ModelMapper to map the NGI library to the corresponding
            # SRA library
            sra_library_design = ModelMapper.map_library(
                source=ngi_model.sample_type,
                application=ngi_model.application,
                library_kit=ngi_model.library_kit,
            )
            return cls.sra_model_class.create_object(
                sample=Converter.ngi_to_sra(ngi_model.sample),
                description=ngi_model.description,
                strategy=sra_library_design.strategy.value,
                source=sra_library_design.source.value,
                selection=sra_library_design.selection.value,
                layout=Converter.ngi_to_sra(ngi_model.layout),
                library_protocol=ngi_model.library_protocol,
            )

    @classmethod
    @catch_exception
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            sample = ConvertSampleDescriptor.lims_to_ngi(lims_model=lims_model)

            # use the logic defined in ngi_models.library_design.NGIObject to match the Clarity
            # LIMS UDF values to the corresponding NGI model object
            application = NGIApplication.match(
                str(lims_model.udf_application)
            )
            sample_type = NGISource.match(
                str(lims_model.udf_sample_type)
            )
            library_kit = NGILibraryKit.match(
                str(lims_model.udf_library_preparation_kit)
            )
            description = None
            layout = ConvertLibraryLayout.lims_to_ngi(lims_model=lims_model)
            library_protocol = str(lims_model.udf_library_preparation_kit or "")
            return cls.ngi_model_class(
                sample=sample,
                description=description,
                application=application,
                sample_type=sample_type,
                library_kit=library_kit,
                layout=layout,
                library_protocol=library_protocol
            )


class ConvertExperiment(Converter):
    """
    Conversion between NGIExperiment, SRAExperiment and LIMSSample
    """

    ngi_model_class = NGIExperiment
    sra_model_class = SRAExperiment
    lims_model_class = LIMSSample

    @classmethod
    @catch_exception
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
    @catch_exception
    def lims_to_ngi(
        cls: Type[T], lims_model: lims_model_class
    ) -> Optional[ngi_model_class]:
        if lims_model:
            sample = ConvertSampleDescriptor.lims_to_ngi(lims_model=lims_model)
            project = ConvertStudyRef.lims_to_ngi(lims_model=lims_model)
            platform = ConvertSequencingPlatform.lims_to_ngi(lims_model=lims_model)
            alias = lims_model.udf_sample_library_id
            library = ConvertLibrary.lims_to_ngi(lims_model=lims_model)
            title = f"{project.project_id} - " \
                    f"{sample.sample_name} - " \
                    f"{str(library.application)} - " \
                    f"{str(library.sample_type)} - " \
                    f"{str(library.library_kit)}"
            return cls.ngi_model_class(
                alias=alias,
                title=title,
                project=project,
                platform=platform,
                library=library,
            )


class ConvertAttribute(Converter):
    """
    Conversion between NGIAttribute and SRAAttribute
    """

    ngi_model_class = NGIAttribute
    sra_model_class = SRAAttribute

    @classmethod
    @catch_exception
    def ngi_to_sra(
        cls: Type[T], ngi_model: ngi_model_class
    ) -> Optional[sra_model_class]:
        if ngi_model:
            return cls.sra_model_class.create_object(
                tag=ngi_model.tag,
                value=ngi_model.value,
                units=ngi_model.units
            )
