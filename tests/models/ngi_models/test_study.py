from snpseq_metadata.models.ngi_models import NGIStudyRef


class TestNGIStudyRef:
    def test_from_json(self, study_obj, study_json):
        study = NGIStudyRef.from_json(json_obj=study_json)
        assert study == study_obj

    def test_to_json(self, study_obj, study_json):
        assert study_obj.to_json() == study_json
