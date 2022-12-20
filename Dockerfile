FROM python:3.11.1-slim-buster

COPY . /snpseq_metadata
WORKDIR /snpseq_metadata

VOLUME /mnt/metadata

# specify the xsdata binary and schema URL as arguments
ARG xsdata=xsdata
ARG schema_url=ftp://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5

ENV PATH="/snpseq_metadata/.venv/bin:$PATH"

RUN \
  python -m venv --upgrade-deps .venv && \
  .venv/bin/pip install . && \
  .venv/bin/pip install .[test]

RUN .venv/bin/generate_python_models.sh $xsdata $schema_url

CMD [ ".venv/bin/snpseq_metadata" ]
