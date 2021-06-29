import os

from snpseq_metadata.models.ngi_models import NGIResultFile, NGIFastqFile


class TestNGIResultFile:
    def test_from_json(self, result_file_obj, result_file_json):
        result_file = NGIResultFile.from_json(json_obj=result_file_json)
        assert result_file == result_file_obj

    def test_to_json(self, result_file_obj, result_file_json):
        assert result_file_obj.to_json() == result_file_json

    def test___eq__(self, result_file_obj, result_file_json):
        kwargs = result_file_json.copy()
        new_obj = NGIResultFile(**kwargs)
        assert new_obj == result_file_obj

        kwargs = result_file_json.copy()
        kwargs["filepath"] = os.path.join(
            "/this", "is", "a", "identical", "..", "file.path"
        )
        new_obj = NGIResultFile(**kwargs)
        assert new_obj == result_file_obj

        for k in result_file_json.keys():
            kwargs = result_file_json.copy()
            kwargs[k] = "this-is-something-different"
            new_obj = NGIResultFile(**kwargs)
            assert new_obj != result_file_obj


class TestNGIFastqFile:
    def test_from_json(self, fastq_file_obj, fastq_file_json):
        fastq_file = NGIFastqFile.from_json(json_obj=fastq_file_json)
        assert fastq_file == fastq_file_obj

    def test_to_json(self, fastq_file_obj, fastq_file_json):
        assert fastq_file_obj.to_json() == fastq_file_json
