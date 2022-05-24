# select_repeats - insertion repeats selector
(c) 2022. Arthur Gruber & Giuliana Pola

Usage: select_repeats.py -i *EMBL ft file* -o *output filename* -div *GenBank division* -defi *sequence description*

select_repeats.py -conf *parameters file*



**Mandatory parameters:**

- -i (text file) - Feature table in EMBL format

- -div (three-letter string) - GenBank division

- -defi (string) - Sequence definition

- -conf *text file* - Text file with the parameters

-o <string>     Name of the output file (feature table in GenBank format)

**Optional parameters:**
- -ir <integer>   Internal range of coordinates in which the repetition is accepted
- -er <integer>   External range of coordinates in which the repetition is accepted
- -s <csv table file>     CSV file that has the data for decision making in the selection

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

## 28/03/2022 (1.2.0)
-  addition of the UGENE find-repeats routine for each parameter set in the configuration file and for each input sequence

## 04/04/2022 (1.3.1)
- adding the routine that extracts the information from the repeats' annotation blocks, concatenates them into a single file, eliminates identical entries and saves them into one file, one for the direct and one for the inverted ones
- creation of the temporary folder in the UGENE output folder and removal from it at the end of the run

## 11/04/2022 (1.3.2)
- changing the name of the output file with the selected repeats
- changing the formatting of the output file with the selected repeats
- converting the parameters in the output file with the selected repeats to be able to open it on Artemis

## 20/04/2022 (1.3.3)
- fix when grabbing input files from a folder

## 22/04/2022 (1.4.0)
- adding the file.log file to the output folder, specifying program processing details
- displaying fewer messages on the screen, detail in the file.log file 
- adding the parameter -r (range), which specifies the coordinate range in which the repetition is accepted, and -s (selection), which specifies the CSV file that has the data for the selection decision
- validation of the -r and -s parameters

## 23/04/2022 (1.4.1)
- fix when calculating the coordinate limit that will be accepted

## 10/05/2022 (1.4.2)
- fix when checking for the existence of the input file or folder
- fix to ignore the -r and -s parameters if they are not given

## 24/05/2022 (1.5.0)
- changing the -i parameter to -in
- replacement of the -r parameter with -ir and -er