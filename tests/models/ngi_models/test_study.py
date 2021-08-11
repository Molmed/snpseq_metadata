from snpseq_metadata.models.ngi_models import NGIStudyRef


class TestNGIStudyRef:
    def test_from_json(self, ngi_study_obj, ngi_study_json):
        study = NGIStudyRef.from_json(json_obj=ngi_study_json)
        assert study == ngi_study_obj

    def test_to_json(self, ngi_study_obj, ngi_study_json):
        assert ngi_study_obj.to_json() == ngi_study_json
