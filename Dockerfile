
FROM python:3.7.10-slim-buster

COPY . /snpseq_metadata
WORKDIR /snpseq_metadata

VOLUME /mnt/metadata

# specify the xsdata binary and schema URL as arguments
ARG xsdata=xsdata
ARG schema_url=ftp://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5

RUN pip install --upgrade pip setuptools wheel && pip install -r requirements_dev.txt -e .
RUN snpseq_metadata/scripts/generate_python_models.sh $xsdata $schema_url

CMD [ "snpseq_metadata" ]
