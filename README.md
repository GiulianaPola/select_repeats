# Select_repeats - Tool for selecting insertion repeats

Select_repeats is a python language program that runs a repeat search tool from the UGENE package, selects the repeats according to context, discards redundancies, and generates an automatic annotation that can be inspected in the Artemis program. 

##   Instalation

Select_repeats does not need to be installed. The user should only download the select_repeats.py file.

## Requirements

## Usage
```
python select_repeats.py -i <EMBL FT file> -o <output filename> -div <GenBank division> -defi <sequence description> <optional parameters>
python select_repeats.py -conf <parameters file> <optional parameters>
```
### Mandatory parameters:
```
-i <filename>	 	  Feature table in EMBL format (text file)
-div <string>	 	  GenBank division(three-letter string)
-defi <string>	  Sequence definition
-conf <filename>  Text file with the parameters
-o <string>       Name of the output file (feature table in GenBank format)
```

### Optional parameters:
```
-ir <integer>	 	Internal range of coordinates in which the repetition is accepted
-er <integer>	 	External range of coordinates in which the repetition is accepted
-s <filename>	 	CSV file that has the data for decision making in the selection
``` 

## Contact

To report bugs, to ask for help and to give any feedback, please contact Arthur Gruber (argruber@usp.br) or Giuliana L. Pola (giulianapola@usp.br).

## Versions

### 1.5.3
- Broken lines from the configuration file are joined together
- The names of the output folders have been fixed: the parentheses have been removed from the name, an underscore has been added to the name and the numbering starts with 2 (ex: outputfolder_2)

### 1.5.2
- removal of space in protein sequences in genbank files
- correction when archiving selected repeat regions if all the repeat regions are within the defined limit

### 1.5.1
- inclusion of 'n' in the nucleotides accepted in the sequence
- modification in the file.log formatting: inclusion of the config file parameters and inclusion of the selection coordinates of each sequence
- addition of the error message that informs in which of the UGENE sets an error occurred
- sorting of the sequences to be processed in alphabetical order
- processing of the file.log after the processing of each sequence

### 1.5.0
- changing the -i parameter to -in
- replacement of the -r parameter with -ir and -er

### 1.4.2
- fix when checking for the existence of the input file or folder
- fix to ignore the -r and -s parameters if they are not given

### 1.4.1
- fix when calculating the coordinate limit that will be accepted

### 1.4.0
- adding the file.log file to the output folder, specifying program processing details
- displaying fewer messages on the screen, detail in the file.log file 
- adding the parameter -r (range), which specifies the coordinate range in which the repetition is accepted, and -s (selection), which specifies the CSV file that has the data for the selection decision
- validation of the -r and -s parameters

### 1.3.3
- fix when grabbing input files from a folder

### 1.3.2
- changing the name of the output file with the selected repeats
- changing the formatting of the output file with the selected repeats
- converting the parameters in the output file with the selected repeats to be able to open it on Artemis

### 1.3.1
- adding the routine that extracts the information from the repeats' annotation blocks, concatenates them into a single file, eliminates identical entries and saves them into one file, one for the direct and one for the inverted ones
- creation of the temporary folder in the UGENE output folder and removal from it at the end of the run

### 1.2.0
-  addition of the UGENE find-repeats routine for each parameter set in the configuration file and for each input sequence

### 1.1.2
- creation of a folder with a new name (folder2) when the output folder exists
- when error in input file, move to next input file and display error message, instead of exiting program

### 1.1.1
- validation of the -o parameter when it is an output folder, from the configuration file

### 1.1.0
- addition and validation of the -conf parameter that receives the configuration file, which contains the parameters to be used in the program and the -o parameter that receives the name of the output file
- correction of the extraction of the id from the filename
- validation of the -i parameter when it is a folder

### 1.0.0
- validation and addition of parameters -i (EMBL feature table),-defi (sequence definition), -div (GenBank division)
- adding a convertEMBL function that receives the feature table in EMBL format and converts it to GenBank format
