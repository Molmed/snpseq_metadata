#! /bin/bash

# run through the test examples and validate the generated XML files
ROOTPATH="$1"
OUTPATH="$2"
OUTTEST="$OUTPATH/test_data"

mkdir -p "$OUTTEST"
snpseq_metadata extract runfolder -o "$OUTPATH" "$ROOTPATH/tests/resources/210415_A00001_0123_BXYZ321XY" json
snpseq_metadata extract snpseq-data -o "$OUTPATH" "$ROOTPATH/tests/resources/snpseq_data_XYZ321XY.json" json
snpseq_metadata export -o "$OUTPATH" "$OUTPATH/210415_A00001_0123_BXYZ321XY.ngi.json" "$OUTPATH/snpseq_data_XYZ321XY.ngi.json" json xml manifest
snpseq_metadata export -o "$OUTTEST" "$ROOTPATH/tests/resources/210415_A00001_0123_BXYZ321XY.ngi.json" "$ROOTPATH/tests/resources/snpseq_data_XYZ321XY.ngi.json" json xml manifest
for DIR in "$OUTPATH" "$OUTTEST"
do
  for TYPE in run experiment
  do
    find "$DIR" -maxdepth 1 -mindepth 1 -name "*.${TYPE}.xml" |while read xml
    do
      python "$ROOTPATH/tests/validate_xml_file.py" "$xml" "$ROOTPATH/resources/schema/SRA.${TYPE}.xsd"
    done
  done
done
