#! /bin/sh

XSDATA_BIN="$1"
if [ -z "$2" ]
then
  URI="ftp://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5"
else
  URI="$2"
fi

# Download the ENA/SRA XSD schema using xsdata
for object in experiment run sample study
do
  "$XSDATA_BIN" download -o resources/schema "$URI/SRA.${object}.xsd"
done

# Generate the python models used in the package
"$XSDATA_BIN" generate -p snpseq_metadata.models.xsdata resources/schema
