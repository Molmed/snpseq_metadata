import os

from snpseq_metadata.models.ngi_models import NGIResultFile
from snpseq_metadata.models.sra_models import SRAResultFile


class TestNGIResultFile:
    @staticmethod
    def _return_checksum(*args, **kwargs):
        return "this-is-a-calculated-checksum"

    @staticmethod
    def _return_alt_checksum(*args, **kwargs):
        return "this-is-another-calculated-checksum"

    def test___eq__(self):
        kwargs = {
            "filepath": os.path.join("/this", "is", "a", "path", "to", "a.file"),
            "filetype": "this-is-a-filetype",
            "checksum": "this-is-a-checksum",
            "checksum_method": "this-is-a-checksum-method",
        }
        obj_a = NGIResultFile(**kwargs)

        kwargs_b = kwargs.copy()
        kwargs_b["filepath"] = os.path.join(
            "/this", "is", "a", "..", "a", "path", "to", "a.file"
        )
        obj_b = NGIResultFile(**kwargs_b)

        assert obj_a == obj_b

        for kwarg in ["filepath", "filetype", "checksum", "checksum_method"]:
            kwargs_c = kwargs.copy()
            kwargs_c[kwarg] = "this-is-something-different"
            obj_c = NGIResultFile(**kwargs_c)

            assert obj_c != obj_a


class TestSRAResultFile:
    @staticmethod
    def _return_checksum(*args, **kwargs):
        return "this-is-a-calculated-checksum"

    @staticmethod
    def _return_alt_checksum(*args, **kwargs):
        return "this-is-another-calculated-checksum"

    def test_to_json(self):
        filepath = os.path.join("/this", "is", "a", "path", "to", "a.file")
        filetype = "fastq"
        checksum = "this-is-a-checksum"
        checksum_method = "MD5"
        expected_json = {
            "filename": filepath,
            "filetype": filetype,
            "checksum": checksum,
            "checksum_method": checksum_method,
        }
        fileobj = SRAResultFile.create_object(
            filepath=filepath,
            filetype=filetype,
            checksum=checksum,
            checksum_method=checksum_method,
        )

        assert fileobj.to_json() == expected_json

    def test_to_xml(self):
        filepath = os.path.join("/this", "is", "a", "path", "to", "a.file")
        filetype = "fastq"
        checksum = "this-is-a-checksum"
        checksum_method = "MD5"
        fileobj = SRAResultFile.create_object(
            filepath=filepath,
            filetype=filetype,
            checksum=checksum,
            checksum_method=checksum_method,
        )

        expected_xml = f'<FILE filename="{filepath}" filetype="{filetype}" checksum_method="{checksum_method}" checksum="{checksum}"/>'
        assert expected_xml in fileobj.to_xml()

    def test_serialize_deserialize(self):
        filepath = os.path.join("/this", "is", "a", "path", "to", "a.file")
        filetype = "fastq"
        checksum = "this-is-a-checksum"
        checksum_method = "MD5"

        original_obj = SRAResultFile.create_object(
            filepath=filepath,
            filetype=filetype,
            checksum=checksum,
            checksum_method=checksum_method,
        )

        serialized_obj = original_obj.to_json()
        deserialized_obj = SRAResultFile.create_object(
            filepath=filepath, filetype=filetype, checksum=checksum
        )

        assert deserialized_obj == original_obj
