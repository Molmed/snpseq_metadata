import os

from snpseq_metadata.models.ngi_models import NGIResultFile, NGIFastqFile


class TestNGIResultFile:
    def test_from_json(self, ngi_result_file_obj, ngi_result_file_json):
        result_file = NGIResultFile.from_json(json_obj=ngi_result_file_json)
        assert result_file == ngi_result_file_obj

    def test_to_json(self, ngi_result_file_obj, ngi_result_file_json):
        assert ngi_result_file_obj.to_json() == ngi_result_file_json

    def test___eq__(self, ngi_result_file_obj, ngi_result_file_json):
        kwargs = ngi_result_file_json.copy()
        new_obj = NGIResultFile(**kwargs)
        assert new_obj == ngi_result_file_obj

        kwargs = ngi_result_file_json.copy()
        kwargs["filepath"] = os.path.join(
            "/this", "is", "a", "identical", "..", "file.path"
        )
        new_obj = NGIResultFile(**kwargs)
        assert new_obj == ngi_result_file_obj

        for k in ngi_result_file_json.keys():
            kwargs = ngi_result_file_json.copy()
            kwargs[k] = "this-is-something-different"
            new_obj = NGIResultFile(**kwargs)
            assert new_obj != ngi_result_file_obj


class TestNGIFastqFile:
    def test_from_json(self, ngi_fastq_file_obj, ngi_fastq_file_json):
        fastq_file = NGIFastqFile.from_json(json_obj=ngi_fastq_file_json)
        assert fastq_file == ngi_fastq_file_obj

    def test_to_json(self, ngi_fastq_file_obj, ngi_fastq_file_json):
        assert ngi_fastq_file_obj.to_json() == ngi_fastq_file_json
