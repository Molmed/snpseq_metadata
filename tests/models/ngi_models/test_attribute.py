from snpseq_metadata.models.ngi_models import NGIAttribute


class TestNGIAttribute:
    def test_from_json(self, ngi_attribute_obj, ngi_attribute_json):
        attribute = NGIAttribute.from_json(json_obj=ngi_attribute_json)
        assert attribute == ngi_attribute_obj

    def test_to_json(self, ngi_attribute_obj, ngi_attribute_json):
        assert ngi_attribute_obj.to_json() == ngi_attribute_json
