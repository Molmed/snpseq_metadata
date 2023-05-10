import csv
import hashlib
import logging
import os
from functools import wraps
from typing import Dict, List, Optional

from snpseq_metadata.exceptions import (
    NoSampleSheetDataFoundException,
    SampleSheetNotFoundException,
    RunParametersNotFoundException,
)


log = logging.getLogger(__name__)


def calculate_checksum_from_file(queryfile: str, method: str) -> str:
    if method == "MD5":
        hasher = hashlib.md5()
    else:
        hasher = hashlib.new(method)

    with open(queryfile, "rb") as fh:
        hasher.update(fh.read())
    return hasher.hexdigest()


def lookup_checksum_from_file(checksumfile: str, querypath: str) -> Optional[str]:
    with open(checksumfile) as fh:
        for row in fh:
            splits = row.split()
            if len(splits) == 2 and splits[1] == querypath:
                return splits[0]


def parse_samplesheet_data(samplesheet: str) -> List[Dict[str, str]]:
    with open(samplesheet) as fh:
        row = ""
        try:
            # discard all rows until we encounter "[Data]"
            while not row.startswith("[Data]"):
                row = next(fh)
        except StopIteration:
            raise NoSampleSheetDataFoundException(samplesheet)

        # use a DictReader to parse the data
        reader = csv.DictReader(fh, dialect="excel")
        return [{key.lower(): value for key, value in row.items()} for row in reader]


def find_samplesheet(search_path: str, suffix: str = "samplesheet.csv") -> List[str]:
    csvfiles = find_file(search_path, suffix)
    if not csvfiles:
        raise SampleSheetNotFoundException(search_path)
    return csvfiles


def find_run_parameters(
    search_path: str, suffix: str = "runparameters.xml"
) -> List[str]:
    csvfiles = find_file(search_path, suffix)
    if not csvfiles:
        raise RunParametersNotFoundException(search_path)
    return csvfiles


def find_file(search_path: str, suffix: str) -> List[str]:
    csvfiles = list(
        filter(
            lambda f: f.lower().endswith(suffix),
            os.listdir(search_path),
        )
    )
    return csvfiles


def log_exception(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as ex:
            log.error(ex)
            raise
    return wrapper
