from snpseq_metadata.models.sra_models import SRAAttribute


class TestSRAAttribute:
    def test_from_json(self, sra_attribute_obj, sra_attribute_json):
        attribute = SRAAttribute.from_json(json_obj=sra_attribute_json)
        assert attribute == sra_attribute_obj.model_object

    def test_to_json(self, sra_attribute_obj, sra_attribute_json):
        assert sra_attribute_obj.to_json() == sra_attribute_json

    def test_to_manifest(self, sra_attribute_obj, sra_attribute_manifest):
        assert sra_attribute_obj.to_manifest() == sra_attribute_manifest

    def test_to_xml(self, sra_attribute_obj, sra_attribute_xml):
        assert sra_attribute_obj.to_xml(xml_declaration=False).split() == \
               sra_attribute_xml.split()

    def test___getattr__(self, sra_attribute_obj, sra_attribute_json):
        assert sra_attribute_obj.tag == sra_attribute_json["TAG"]
        assert sra_attribute_obj.value == sra_attribute_json["VALUE"]
        assert sra_attribute_obj.units == sra_attribute_json["UNITS"]

    def test___str__(self, sra_attribute_obj, sra_attribute_json):
        assert str(sra_attribute_obj) == f"{sra_attribute_json['TAG']} = " \
                                         f"{sra_attribute_json['VALUE']} " \
                                         f"{sra_attribute_json['UNITS']}"

    def test___eq__(self, sra_attribute_obj, sra_attribute_json):
        other_obj = SRAAttribute.create_object(
            tag=sra_attribute_json['TAG'],
            value=sra_attribute_json['VALUE'],
            units=sra_attribute_json['UNITS'])
        assert other_obj == sra_attribute_obj
        other_obj = SRAAttribute.create_object(
            tag=f"not-{sra_attribute_json['TAG']}",
            value=f"not-{sra_attribute_json['VALUE']}",
            units=f"not-{sra_attribute_json['UNITS']}")
        assert other_obj != sra_attribute_obj

    def test_create_object(self, sra_attribute_obj, sra_attribute_json):
        obj = SRAAttribute.create_object(
            tag=sra_attribute_json['TAG'],
            value=sra_attribute_json['VALUE'],
            units=sra_attribute_json['UNITS'])
        assert obj == sra_attribute_obj
