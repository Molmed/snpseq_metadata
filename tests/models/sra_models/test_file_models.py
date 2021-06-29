from snpseq_metadata.models.sra_models import SRAResultFile


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
