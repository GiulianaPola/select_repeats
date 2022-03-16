# select_repeats - insertion repeats selector
(c) 2022. Arthur Gruber & Giuliana Pola

Usage: select_repeats.py -i *EMBL ft file* -o *output filename* -div *GenBank division* -defi *sequence description*

select_repeats.py -conf *parameters file*



**Mandatory parameters:**

- -i (text file) - Feature table in EMBL format

- -o (string) - Name of the output file (feature table in GenBank format)

- -div (three-letter string) - GenBank division

- -defi (string) - Sequence definition

- -conf *text file* - Text file with the parameters

## 12/03/2022 (1.0.0)
- validation and addition of parameters -i (EMBL feature table),-defi (sequence definition), -div (GenBank division)
- adding a convertEMBL function that receives the feature table in EMBL format and converts it to GenBank format
