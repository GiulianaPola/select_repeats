# select_repeats - insertion repeats selector
(c) 2022. Arthur Gruber & Giuliana Pola

Usage: select_repeats.py -i *EMBL ft file* -o *output filename* -div *GenBank division* -defi *sequence description*

select_repeats.py -conf *parameters file*



**Mandatory parameters:**

- -i (text file) - Feature table in EMBL format

- -div (three-letter string) - GenBank division

- -defi (string) - Sequence definition

- -conf *text file* - Text file with the parameters

**Optional parameters:**
- -o (string) - Name of the output file (feature table in GenBank format)

## 12/03/2022 (1.0.0)
- validation and addition of parameters -i (EMBL feature table),-defi (sequence definition), -div (GenBank division)
- adding a convertEMBL function that receives the feature table in EMBL format and converts it to GenBank format

## 18/03/2022 (1.1.0)
- addition and validation of the -conf parameter that receives the configuration file, which contains the parameters to be used in the program and the -o parameter that receives the name of the output file
- correction of the extraction of the id from the filename
- validation of the -i parameter when it is a folder

## 19/03/2022 (1.1.1)
- validation of the -o parameter when it is an output folder, from the configuration file

## 23/03/2022 (1.1.2)
- creation of a folder with a new name (folder2) when the output folder exists
- when error in input file, move to next input file and display error message, instead of exiting program
