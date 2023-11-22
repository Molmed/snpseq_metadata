
from snpseq_metadata.models.ngi_models import \
    NGIPool, \
    NGIPoolMember, \
    NGIReadLabel


class TestNGIReadLabel:

    def test_from_json(self, ngi_read_label_obj, ngi_read_label_json):
        label = NGIReadLabel.from_json(json_obj=ngi_read_label_json)
        assert label == ngi_read_label_obj

    def test_to_json(self, ngi_read_label_obj, ngi_read_label_json):
        assert ngi_read_label_obj.to_json() == ngi_read_label_json


class TestNGIPoolMember:

    def test_from_json(self, ngi_pool_member_obj, ngi_pool_member_json):
        member = NGIPoolMember.from_json(json_obj=ngi_pool_member_json)
        assert member == ngi_pool_member_obj

    def test_to_json(self, ngi_pool_member_obj, ngi_pool_member_json):
        assert ngi_pool_member_obj.to_json() == ngi_pool_member_json


class TestNGIPool:

    def test_from_json(self, ngi_pool_obj, ngi_pool_json):
        pool = NGIPool.from_json(json_obj=ngi_pool_json)
        assert pool == ngi_pool_obj

    def test_to_json(self, ngi_pool_obj, ngi_pool_json):
        assert ngi_pool_obj.to_json() == ngi_pool_json
