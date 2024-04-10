from snpseq_metadata.models.ngi_to_sra_mapping import ModelMapper

from snpseq_metadata.models.ngi_models.library_design import (
    NGISource,
    NGISourceClasses,
    NGIApplication,
    NGIApplicationClasses,
    NGILibraryKit,
    NGILibraryKitClasses,
)


class TestApplicationSampleTypeMapping:

    mappings = ModelMapper.library_mapping

    def test_create_application_object(self):
        for inp, exp in self.mappings:
            # inp is a list of lists. iterate over all possible combinations
            for src in inp[0]:
                for app in inp[1]:
                    for lib in inp[2]:
                        assert type(
                            ModelMapper.map_library(
                                src("test-source"),
                                app("test-application"),
                                lib("test-library-kit")
                            ) is exp
                        ), f"Input {','.join([src.__name__, app.__name__, lib.__name__])} " \
                           f"did not get mapped to type {exp}"
