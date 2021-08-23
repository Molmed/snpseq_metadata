
FROM python:3.7.10-slim-buster

COPY . /snpseq_metadata
WORKDIR /snpseq_metadata

VOLUME /mnt/metadata

RUN python -m pip install --upgrade pip setuptools wheel && python -m venv venv
RUN venv/bin/python -m pip install -r requirements_dev.txt -e .

ENV PATH=/snpseq_metadata/venv/bin:$PATH

CMD [ "venv/bin/snpseq_metadata" ]
