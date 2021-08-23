import click
import xmlschema


@click.command()
@click.argument("xml_file", type=click.File(mode="r"), required=True)
@click.argument("xsd_file", type=click.Path(exists=True), required=True)
def validate_xmlfile(xml_file, xsd_file):
    schema = xmlschema.XMLSchema(xsd_file)
    schema.validate(xml_file)


if __name__ == "__main__":
    validate_xmlfile()
