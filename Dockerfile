
FROM python:3.7.10-slim-buster

COPY . /snpseq_metadata
WORKDIR /snpseq_metadata

VOLUME /mnt/metadata

RUN pip install --upgrade pip setuptools wheel && pip install -r requirements_dev.txt -e .
RUN snpseq_metadata/scripts/generate_python_models.sh xsdata

CMD [ "snpseq_metadata" ]
