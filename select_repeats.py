#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import re
import ntpath
import traceback
import warnings
import argparse
import re
from datetime import datetime

# Improved warning handler with traceback
def warn_with_traceback(message, category, filename, lineno, file=None, line=None):
    log = file if hasattr(file, 'write') else sys.stderr
    traceback.print_stack(file=log)
    log.write(warnings.formatwarning(message, category, filename, lineno, line))

warnings.showwarning = warn_with_traceback

# Global variables
start_time = datetime.now()
param = {}
call = os.path.abspath(os.getcwd())
log = None
nseqs = -1
processed = 0
version = "1.6.4"

print('Select_repeats v{} - repeats regions selector\n'.format(version))

# Argument parsing
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-in', dest='in_')
parser.add_argument('-o')
parser.add_argument('-div')
parser.add_argument('-defi')
parser.add_argument('-conf')
parser.add_argument('-ir')
parser.add_argument('-er')
parser.add_argument('-s')
parser.add_argument('-version', action='store_true')
parser.add_argument('-h', '--help', action='store_true')
args = parser.parse_args()

# Map parsed arguments to param dictionary, using original keys
param = {}
for key, value in vars(args).items():
    if key == 'in_':
        param['in'] = value
    elif value is not None:
        param[key] = value

def print_help():
    """
    Prints a formatted help message for the select_repeats.py script, including usage instructions,
    mandatory and optional parameters, and additional information. The output is dynamically wrapped
    to fit the current terminal width.
    The help message includes:
    - Copyright and authorship information.
    - A link to the project's GitHub repository.
    - Usage examples for running the script with direct parameters or a configuration file.
    - A list of mandatory parameters with descriptions.
    - A list of optional parameters with descriptions.
    Terminal width is detected to ensure proper formatting and wrapping of the help text.
    """
    import os
    import shutil

    mandatory = {
        '-in <text file|folder>': 'Feature table in EMBL format or folder containing them',
        '-o <string>': 'Name of the output file (feature table in GenBank format)',
        '-div <three-letter string>': 'GenBank division',
        '-defi <string>': 'Sequence definition',
        '-conf <text file>': 'Text file with the parameters'
    }
    optional = {
        '-ir <integer>': 'Internal range of coordinates in which the repetition is accepted',
        '-er <integer>': 'External range of coordinates in which the repetition is accepted',
        '-s <csv table file>': 'CSV file that has the data for decision making in the selection'
    }

    def get_terminal_width():
        try:
            return os.get_terminal_size().columns
        except OSError:
            try:
                return int(shutil.get_terminal_size().columns)
            except Exception:
                try:
                    import subprocess
                    return int(subprocess.check_output("tput cols", shell=True))
                except Exception:
                    return 80  # fallback

    width = get_terminal_width()

    header = [
        '(c) 2022. Arthur Gruber & Giuliana Pola',
        'For more information access: https://github.com/GiulianaPola/select_repeats',
        '',
        'Usage:',
        '  select_repeats.py -in <EMBL file|folder containing EMBL files> -o <output filename> -div <GenBank division> -defi <sequence description> <optional parameters>',
        '  select_repeats.py -conf <parameters file>',
        '',
        'Mandatory parameters:'
    ]

    def wrap(text, indent=0):
        import textwrap
        return textwrap.fill(text, width=width, subsequent_indent=' ' * indent)

    print('\n'.join(wrap(line) for line in header))

    # Find max key width for alignment
    all_keys = list(mandatory.keys()) + list(optional.keys())
    max_key_len = max(len(k) for k in all_keys) + 2

    # Print mandatory parameters
    for key in sorted(mandatory.keys()):
        desc = mandatory[key]
        print('  ' + key.ljust(max_key_len) + wrap(desc, indent=max_key_len+2)[max_key_len+2:])

    print('\nOptional parameters:')
    for key in sorted(optional.keys()):
        desc = optional[key]
        print('  ' + key.ljust(max_key_len) + wrap(desc, indent=max_key_len+2)[max_key_len+2:])

def get_filename(path):
    """
    Returns the filename from a given path, handling both Unix and Windows paths.
    If the path ends with a separator, returns the last directory name.
    """
    if not path:
        return ''
    tail = ntpath.basename(path.rstrip(ntpath.sep))
    return tail

def rename_dir(directory):
    """
    Returns a new directory name by appending an incrementing suffix if the given directory exists.
    For example, if 'dir' exists, returns 'dir_2', 'dir_3', etc., until a non-existing name is found.
    """
    base = os.path.abspath(directory)
    i = 2
    while True:
        new_dir = "{}_{}".format(base, i)
        if not os.path.exists(new_dir):
            return new_dir
        i += 1

def rename_file(file):
    """
    Returns a new filename by appending an incrementing suffix before the extension
    if the given file already exists. For example, if 'file.txt' exists, returns
    'file_2.txt', 'file_3.txt', etc., until a non-existing name is found.
    """
    base, ext = os.path.splitext(file)
    i = 2
    while True:
        new_file = "{}_{}{}".format(base, i, ext)
        if not os.path.exists(new_file):
            return new_file
        i += 1
        
def validate_conf(conf):
            """
            Validates and parses a configuration file, updating the global 'param' dictionary
            with recognized parameters. Handles input/output paths, directories, and other options.
            Returns a string summary of the parsed parameters.
            """
            parameters = []
            # Recognized parameter names (for reference, not strictly enforced)
            names = [
                'conf', 'def', 'defi', 'div', 'er', 'in', 'input_dir', 'ir', 'o', 'out_dir', 's',
            ]
            if not os.path.isfile(conf):
                print("{} (-conf) doesn't exist!".format(get_filename(conf)))
                quit()
            with open(conf, 'r') as file:
                lines = [line.strip() for line in file if line.strip()]
            # Combine lines in reverse for multi-line values
            line = ''
            for lin in reversed(lines):
                if not line:
                    line = lin
                else:
                    line = lin + line
                if '=' not in line:
                    continue
                arg = line.split('=')[0].strip().strip('"').replace(" ", "_").lower()
                value = '='.join(line.split('=')[1:]).strip().strip('"')
                # Handle list values
                if ' e ' in value:
                    value = value.split(' e ')
                # Skip lines that look like flags or are empty
                if "--" in arg or arg.startswith('-') or not arg:
                    line = lin
                    continue
                # Map config keys to param keys
                if arg.startswith('input') or arg.startswith('i_') or arg in ('i', 'in'):
                    parameters.append(line)
                    path = find_path(value)
                    if path is None:
                        print("'{}' (-in) doesn't exist".format(value))
                        quit()
                    param['in'] = path
                    line = ''
                elif arg in ('def', 'defi'):
                    param['defi'] = value
                    parameters.append(line)
                    line = ''
                elif arg == 'div':
                    param['div'] = value
                    parameters.append(line)
                    line = ''
                elif arg == 'r':
                    param['er'] = value
                    param['ir'] = value
                    parameters.append(line)
                    line = ''
                elif arg in ('external_range', 'er'):
                    param['er'] = value
                    parameters.append(line)
                    line = ''
                elif arg in ('internal_range', 'ir'):
                    param['ir'] = value
                    parameters.append(line)
                    line = ''
                elif arg.startswith('csv') or arg == 's':
                    param['s'] = os.path.realpath(value)
                    parameters.append(line)
                    line = ''
                elif arg.startswith('out') or arg.startswith('o_') or arg == 'o':
                    param['o'] = value
                    parameters.append(line)
                    if 'dir' in arg:
                        param['outdir'] = os.path.realpath(value)
                        # Create output directory if needed
                        if not os.path.isdir(param['outdir']):
                            try:
                                os.mkdir(param['outdir'])
                                print("Creating directory '{}'...".format(get_filename(param['outdir'])))
                            except Exception:
                                param['outdir'] = os.path.join(call, param['outdir'])
                                if not os.path.isdir(param['outdir']):
                                    try:
                                        os.mkdir(param['outdir'])
                                        print("Creating directory '{}'...".format(get_filename(param['outdir'])))
                                    except Exception:
                                        print("Directory '{}' wasn't created!".format(get_filename(param['outdir'])))
                                        quit()
                                else:
                                    print("Directory '{}' already exists!".format(get_filename(param['outdir'])))
                                    param['outdir'] = rename_dir(param['outdir'])
                                    try:
                                        os.mkdir(param['outdir'])
                                        print("Creating directory '{}'...".format(get_filename(param['outdir'])))
                                    except Exception:
                                        print("Directory '{}' wasn't created!".format(get_filename(param['outdir'])))
                                        quit()
                        else:
                            print("Directory '{}' already exists!".format(get_filename(param['outdir'])))
                            param['outdir'] = rename_dir(param['outdir'])
                            try:
                                os.mkdir(param['outdir'])
                                print("Creating directory '{}'...".format(get_filename(param['outdir'])))
                            except Exception:
                                print("Directory '{}' wasn't created!".format(get_filename(param['outdir'])))
                                quit()
                    line = ''
                elif 'parameter_set' in arg or 'set' in arg:
                    parameters.append(line)
                    if 'sets' not in param:
                        param['sets'] = [value]
                    else:
                        param['sets'].append(value)
                    line = ''
                else:
                    line = lin
            # Remove empty entries
            parameters = [p for p in parameters if p]
            return "\n".join(sorted(parameters))

def validate_div(div):
    """
    Validates the GenBank division code.
    Ensures it is a three-letter alphabetic string.
    """
    if not isinstance(div, str):
        print("GenBank division (-div) is not string!")
        quit()
    if not div.isalpha():
        print(div)
        print("GenBank division (-div) hasn't only letters!")
        quit()
    if len(div) != 3:
        print("GenBank division (-div) must be only three letters!")
        quit()
    param['div'] = div.upper()


def validate_range(value):
    """
    Validates that the provided value is an integer (or can be converted to one).
    Returns the integer value if valid, otherwise prints an error and exits.
    """
    try:
        ivalue = int(value)
        return ivalue
    except (TypeError, ValueError):
        print("'{}' (range) isn't an integer!".format(value))
        quit()


def find_path(tail):
    """
    Attempts to resolve the absolute path for a given file or directory name.
    Tries the following locations in order:
    1. As given (absolute or relative to current working directory).
    2. Relative to the script's starting directory (`call`).
    3. Relative to the directory containing the config file (`param['conf']`), if provided.
    Returns the absolute path if found, otherwise None.
    """
    if not tail:
        return None

    # Direct path
    if os.path.exists(tail):
        return os.path.realpath(tail)

    # Try relative to current working directory
    candidates = [
        os.path.realpath(tail),
        os.path.join(call, tail)
    ]

    # Try relative to config file directory, if available
    conf_path = param.get('conf')
    if conf_path:
        conf_dir = os.path.dirname(os.path.realpath(conf_path))
        if conf_dir:
            candidates.append(os.path.join(conf_dir, tail))

    for p in candidates:
        if os.path.exists(p):
            return os.path.realpath(p)
    return None

def validate_input(file):
    """
    Validates that the input file exists and can be opened for reading.
    Logs and prints appropriate messages on failure or success.
    Returns True if the file is valid and accessible, otherwise False.
    """
    try:
        with open(file, "r"):
            pass
    except Exception as e:
        msg = "'{}' (-in) couldn't be opened, skipped!".format(get_filename(file))
        print(msg)
        if log:
            log.write("\n" + msg)
            log.write("\nReason: {}\n".format(e))
        return False
    else:
        msg = "\nOpening '{}' (-in)...".format(get_filename(file))
        print(msg)
        if log:
            log.write("\n\n" + msg + "\n")
        return True

def get_id(input_path):
    """
    Extracts a sequence identifier from the input filename. The ID is defined
    as the substring from the start of the filename up to and including the
    last digit found in the name.
    """
    try:
        name = get_filename(input_path)
        # Find the index of the last digit in the filename string
        last_digit_index = -1
        for i, char in enumerate(name):
            if char.isdigit():
                last_digit_index = i
        
        if last_digit_index == -1:
            raise ValueError("No digit found in filename")
        
        # The ID is the slice from the start of the name to the last digit
        param['id'] = name[:last_digit_index + 1]
        return True
    except ValueError as e:
        msg = "'{}' does not have a valid identifier format, skipped!".format(get_filename(input_path))
        print(msg)
        if log:
            log.write("\n" + msg)
        return False

def validate_out_args(param):
    """
    Validates and prepares output file arguments in the param dictionary.
    Ensures output filenames are set, unique, and properly formatted.
    Handles output directories and sequence definitions.
    Returns True if output arguments are valid, otherwise False.
    """
    returned = True

    # Determine output filenames
    if not param.get('o'):
        out = ["{}_UGENE.gbk".format(param['id']), "{}_repeats.gbk".format(param['id'])]
    elif 'outdir' in param:
        out = [
            os.path.join(param['outdir'], "{}_UGENE.gbk".format(param['id'])),
            os.path.join(param['outdir'], "{}_repeats.gbk".format(param['id']))
        ]
    else:
        if isinstance(param['o'], list) and len(param['o']) == 1:
            out = ["{}_UGENE.gbk".format(param['id']), param['o'][0]]
        else:
            out = param['o'] if isinstance(param['o'], list) else [param['o']]

    # Replace '*' with id and ensure unique filenames
    out2 = []
    for o in out:
        filename = o.replace('*', param['id']) if '*' in o else o
        if os.path.isfile(filename):
            newname = rename_file(filename)
            print("Output file '{}' already exists, creating '{}'!".format(filename, newname))
            if log:
                log.write("\nOutput file '{}' already exists, creating '{}'!".format(filename, newname))
            out2.append(newname)
        else:
            out2.append(filename)
    param['o'] = out2

    # Validate sequence definition
    defi = param.get('defi')
    if defi is None:
        print("Missing sequence definition (-defi), skipped!")
        if log:
            log.write("\nMissing sequence definition (-defi), skipped!")
        returned = False
    elif not isinstance(defi, str):
        print("Sequence definition (-defi) is not a string, skipped!")
        if log:
            log.write("\nSequence definition (-defi) is not a string, skipped!")
        returned = False
    else:
        param['defi'] = defi.replace('*', param['id']) if '*' in defi else defi

    return returned

def convert_EMBL(file, seq_id):
    """
    Converts an EMBL feature table to GenBank format robustly.
    
    This function correctly parses the feature table, base counts, and sequence blocks,
    and formats them according to GenBank specifications. This version specifically
    fixes the feature table indentation logic.

    Returns:
        True if conversion is successful, otherwise False.
    """
    try:
        with open(file, "r") as embl_file:
            content = embl_file.read()
    except IOError:
        log.write("\nError: Input file '{}' could not be opened, skipped.".format(get_filename(file)))
        print("\nError: Could not open '{}'".format(get_filename(file)))
        return False

    # Split the file into features and sequence sections
    parts = re.split(r'\nSQ\s+Sequence\s+', content, 1)
    if len(parts) != 2:
        log.write("\nError: Malformed EMBL file '{}': 'SQ Sequence' header not found.".format(get_filename(file)))
        print("\nError: Malformed EMBL file '{}'".format(get_filename(file)))
        return False

    feature_section, sequence_section = parts

    feature_lines = feature_section.strip().split('\n')
    genbank_feature_lines = []
    for line in feature_lines:
        if not line.startswith('FT'):
            continue  # Ignore any non-feature table lines

        # In EMBL, new feature keys (like 'gene', 'CDS') start at column 6 (index 5).
        # Qualifiers and their continuation lines have whitespace at this position and start at column 22 (index 21).
        is_new_feature_key = len(line) > 5 and not line[5].isspace()

        if is_new_feature_key:
            # This is a feature key. Indent with 5 spaces.
            # The content starts from column 6 onwards.
            content = line[5:]
            genbank_feature_lines.append(' ' * 5 + content)
        else:
            # This is a qualifier or a continuation line. Indent with 21 spaces.
            # The content starts from column 22 onwards.
            if len(line) > 21:
                content = line[21:]
                genbank_feature_lines.append(' ' * 21 + content)
            # If the line is shorter than 21, it's likely an empty FT line, which we can ignore.
            
    genbank_features = '\n'.join(genbank_feature_lines)
    
    # --- Parse Sequence Header and Block ---
    seq_lines = sequence_section.strip().split('\n')
    header_line = seq_lines[0]
    
    # Extract base counts safely using regex
    base_counts = {}
    for base in ['A', 'C', 'G', 'T']:
        match = re.search(r'(\d+)\s+{};'.format(base), header_line)
        if match:
            base_counts[base.lower()] = match.group(1)
        else:
            base_counts[base.lower()] = '0' 

    if len(base_counts) < 4:
        log.write("\nError: Malformed EMBL file '{}': Could not parse all base counts.".format(get_filename(file)))
        return False

    genbank_header = "BASE COUNT     {} a   {} c   {} g   {} t\nORIGIN\n".format(
        base_counts['a'], base_counts['c'], base_counts['g'], base_counts['t']
    )
    
    # Process sequence lines robustly until the '//' marker
    genbank_sequence_lines = []
    base_pos = 1
    total_len = 0
    for line in seq_lines[1:]:
        line = line.strip()
        if not line:
            continue
        if line.startswith('//'):
            break
            
        parts = line.split()
        sequence_str = "".join(parts[:-1])
        last_base_index = parts[-1]

        # Correct sequence validation
        if not all(char in 'acgtn' for char in sequence_str.replace(' ', '').lower()):
            log.write("\nError: Invalid characters found in sequence of '{}'.".format(get_filename(file)))
            return False
            
        try:
            total_len = int(last_base_index)
            genbank_sequence_lines.append("{:>9} {}\n".format(base_pos, " ".join(parts[:-1])))
            base_pos = total_len + 1
        except (ValueError, IndexError):
            log.write("\nError: Malformed sequence line in '{}': '{}'".format(get_filename(file), line))
            return False

    # --- Assemble the Final GenBank File ---
    today = datetime.now().strftime("%d-%b-%Y").upper()
    
    # Use proper fixed-width formatting for the LOCUS line
    locus_line = "LOCUS       {:<16}{:>11} bp    DNA     linear   {} {}\n".format(
        seq_id, total_len, param['div'], today
    )
    definition_line = "DEFINITION  {} {}\n".format(param['defi'], seq_id)
    features_header = "FEATURES             Location/Qualifiers"

    # Assemble with correct newlines for proper formatting
    final_content = (
        locus_line +
        definition_line +
        features_header + '\n' + # Added a newline here
        genbank_features + '\n' +
        genbank_header +
        "".join(genbank_sequence_lines) +
        "//"
    )
    
    # Write the final output file
    try:
        with open(param['o'][0], 'w') as gbk_file:
            gbk_file.write(final_content)
        print("\n'{}' EMBL table was converted successfully.".format(seq_id))
        log.write("\n'{}' EMBL table was converted successfully.".format(seq_id))
        return True
    except IOError:
        log.write("\nError: GenBank file '{}' could not be written.".format(param['o'][0]))
        print("\nError: Could not write output file.")
        return False

def validate_sets(sets, id):
        """
        Validates and prepares UGENE command sets for execution.
        Ensures required arguments are present, fills in defaults, and resolves paths.
        Populates param['finds'] with output file paths and param['ugene'] with full commands.
        Returns True if at least one valid set is found, otherwise False.
        """
        valid = []
        param['finds'] = []
        for s in sets:
            # Ensure '--in=' argument
            if '--in=' not in s:
                filename = os.path.basename(param['o'][0])
                s += ' --in=' + filename
            # Ensure 'ugene' command prefix
            if not s.strip().startswith('ugene'):
                s = 'ugene ' + s
            # Ensure '--tmp-dir=' argument and set param['tmp']
            if '--tmp-dir=' not in s:
                s += ' --tmp-dir=tmp'
                if 'outdir' in param:
                    param['tmp'] = os.path.join(param['outdir'], 'tmp')
                else:
                    param['tmp'] = os.path.join(call, 'tmp')
            else:
                tmp_dir = (s.split('--tmp-dir=')[1]).split()[0]
                if 'outdir' in param:
                    param['tmp'] = os.path.join(param['outdir'], tmp_dir)
                else:
                    param['tmp'] = os.path.join(call, tmp_dir)
            # Ensure '--name=' argument for repeat type
            if '--name=' not in s:
                if '--inverted=True' in s and '--name=TIR' not in s:
                    s += ' --name=TIR'
                elif '--inverted=False' in s and '--name=TDR' not in s:
                    s += ' --name=TDR'
            # Replace '*' with id
            if '*' in s:
                s = s.replace('*', id)
            valid.append(s)
            # Extract output file from '--out=' argument
            out = None
            for part in s.split():
                if part.startswith('--out='):
                    out = part[len('--out='):]
                    break
            if out:
                param['finds'].append(out)
            else:
                print("UGENE set missing '--out=' argument, skipped!")
                log.write("\nUGENE set missing '--out=' argument, skipped!")
        if not valid:
            print("UGENE sets aren't valid!")
            log.write("\nUGENE sets aren't valid!")
            return False
        else:
            param['ugene'] = valid
            return True

def remove_dir(folder):
    """
    Recursively deletes all files and subdirectories in the given folder.
    Logs any errors encountered during deletion.
    """
    import shutil
    import os

    if not os.path.isdir(folder):
        return

    for entry in os.scandir(folder):
        path = entry.path
        try:
            if entry.is_file() or entry.is_symlink():
                os.unlink(path)
            elif entry.is_dir():
                shutil.rmtree(path)
        except Exception as e:
            msg = "\nFailed to delete {}. Reason: {}".format(path, e)
            if log:
                log.write(msg)
            else:
                print(msg)

def validate_csv(param):
    """
    Validates and parses the CSV decision table. It finds the line that
    matches the exact sequence ID (param['id']), extracts its coordinates,
    and computes the selection window based on internal/external ranges.
    """
    returned = True
    selection_file_path = param.get('s')
    if not selection_file_path:
        return False

    if not os.path.isfile(selection_file_path):
        selection_file_path = os.path.join(call, selection_file_path)

    try:
        with open(selection_file_path, "r") as file_handler:
            matching_line = None
            for line in file_handler:
                # Check if the line starts with the exact ID, followed by a delimiter
                if re.match(r'^{}[;\t, ]'.format(re.escape(param['id'])), line.strip()):
                    matching_line = line.strip()
                    break
            
            if not matching_line:
                raise ValueError("ID not found in table")

            # Proceed to parse coordinates from the verified matching line
            parts = [p for p in re.split(r'[;\t, ]', matching_line) if p]
            numbers = sorted([int(p) for p in parts[1:] if p.isdigit()])

            if len(numbers) == 2:
                if log:
                    log.write("\nCoordinates for '{}': {}..{}".format(param['id'], numbers[0], numbers[1]))
                
                selection = []
                ir = param.get('ir')
                er = param.get('er')
                min_n, max_n = numbers
                
                if ir is None and er is None:
                    selection.extend([min_n, max_n])
                elif er is None:
                    selection.extend([min_n + ir, max_n - ir])
                elif ir is None:
                    selection.extend([min_n - er, max_n + er])
                else:
                    selection.extend([min_n - er, min_n + ir, max_n - ir, max_n + er])
                param['selection'] = selection
            else:
                raise ValueError("Invalid number of coordinates for ID")

    except Exception as e:
        msg_template = "\n'{}' was not found in the decision table, selecting repeats without coordinate restriction!"
        msg = msg_template.format(param['id'])
        print(msg.strip())
        if log:
            log.write(msg)
        returned = False

    return returned

def select_reps(finds, id, selection):
    """
    Filters and writes repeat regions from UGENE output files based on selection coordinates.
    Handles both direct and inverted repeats, logs filtering results, and writes output tables.
    """
    filtered = set()
    direct = {}
    inverted = {}

    # Log selection limits if provided
    if selection:
        if len(selection) == 4:
            msg = "\nLimit of '{}' repeats filtering: {}..{}, {}..{}".format(id, selection[0], selection[1], selection[2], selection[3])
        elif len(selection) == 2:
            msg = "\nLimit of '{}' repeats filtering: {}..{}".format(id, selection[0], selection[1])
        else:
            msg = "\nLimit of '{}' repeats filtering: {}".format(id, selection)
        print(msg)
        if log:
            log.write(msg)

    for find in finds:
        try:
            with open(find, "r") as file:
                text = file.read()
        except Exception:
            msg = "\nUGENE '{}' file wasn't opened!".format(get_filename(find))
            if log:
                log.write(msg)
            continue

        import re
        starts = [m.start() for m in re.finditer("repeat_region   join", text)]
        starts.append(len(text))
        regions = [text[starts[i]:starts[i + 1]] for i in range(len(starts) - 1)]

        for region in regions:
            key = region[region.find("(") + 1:region.find(")")]
            end = region.find("\n", region.find("/ugene_name=")) + 3
            repeat = region[:end]

            # Determine repeat type
            is_inverted = '/rpt_type="inverted"' in repeat or '/ugene_name="TIR"' in repeat
            is_direct = '/rpt_type="direct"' in repeat or '/ugene_name="TDR"' in repeat

            # Check if this repeat type is expected in the current set
            valid_type = True
            sets_str = ' '.join(param.get('sets', []))
            if is_inverted:
                valid_type = '--inverted=True' in sets_str or '--name=TIR' in sets_str
            elif is_direct:
                valid_type = '--inverted=False' in sets_str or '--name=TDR' in sets_str

            if not valid_type:
                continue

            # Filter by selection coordinates if provided
            valid_coords = True
            if selection:
                coordinates = []
                for coordinate in key.split(","):
                    parts = coordinate.split("..")
                    if not coordinates:
                        coordinates.append(int(parts[0]))
                    else:
                        coordinates.append(int(parts[-1]))
                coordinates = sorted(coordinates)
                if len(selection) == 4:
                    valid_coords = (selection[0] <= coordinates[0] <= selection[1] and
                                    selection[2] <= coordinates[1] <= selection[3])
                elif len(selection) == 2:
                    valid_coords = (selection[0] <= coordinates[0] and coordinates[1] <= selection[1])
                else:
                    valid_coords = False

            # Store or filter repeat
            if valid_coords:
                if is_inverted and key not in inverted:
                    inverted[key] = repeat
                if is_direct and key not in direct:
                    direct[key] = repeat
            else:
                if is_inverted and "Inverted '{}'".format(id) not in filtered:
                    filtered.add("Inverted '{}'".format(id))
                    if log:
                        log.write("\nInverted '{}' was filtered!".format(id))

                if is_direct and "Direct '{}'".format(id) not in filtered:
                    filtered.add("Direct '{}'".format(id))
                    if log:
                        log.write("\nDirect '{}' was filtered!".format(id))

    # Print summary of filtering
    if filtered and selection:
        if "Direct '{}'".format(id) in filtered and "Inverted '{}'".format(id) not in filtered:
            print("'{}' direct repeat regions were selected!".format(id))
            log.write("\n'{}' direct repeat regions were selected!".format(id))
        elif "Inverted '{}'".format(id) in filtered and "Direct '{}'".format(id) not in filtered:
            print("'{}' inverted repeat regions were selected!".format(id))
            log.write("\n'{}' inverted repeat regions were selected!".format(id))
        else:
            print("'{}' direct and inverted repeat regions were selected!".format(id))
            log.write("\n'{}' direct and inverted repeat regions were selected!".format(id))
    elif not filtered:
        print("All '{}' direct and inverted repeat regions are within the filtering limits!".format(id))
        log.write("\nAll '{}' direct and inverted repeat regions are within the filtering limits!".format(id))

    # Write output tables and log results
    if direct:
        write_repeats_table(direct, False, id)
        if "Direct '{}'".format(id) not in filtered and log:
            log.write("\nAll '{}' direct repeat regions are within the filtering limits!".format(id))
    elif "Direct '{}'".format(id) in filtered and log:
        log.write("\nAll '{}' direct repeat regions are outside the filtering limits!".format(id))

    if inverted:
        write_repeats_table(inverted, True, id)
        if "Inverted '{}'".format(id) not in filtered and log:
            log.write("\nAll '{}' inverted repeat regions are within the filtering limits!".format(id))
    elif "Inverted '{}'".format(id) in filtered and log:
        log.write("\nAll '{}' inverted repeat regions are outside the filtering limits!".format(id))

def write_repeats_table(repeats, inverted, id):
    """
    Writes a GenBank-formatted table of selected repeat regions to a file.
    Handles both direct and inverted repeats, formats output, and logs errors.
    """
    filename = "{}_{}_repeats_selected.gbk".format(id, 'inverted' if inverted else 'direct')
    try:
        with open(filename, 'w') as file:
            lines = ''.join(repeats.values()).split('\n')
            lines = [line for line in lines if line.strip()]
            first_feature = True
            for line in lines:
                if 'repeat_region   join' in line:
                    words = line.split()
                    if inverted is False:
                        # Add /rpt_type=direct for direct repeats
                        line += ' ' * 21 + '/rpt_type=direct\n'
                    # Format feature line
                    line = ' ' * 5 + words[0] + ' ' * 3 + words[1] + '\n'
                    if not first_feature:
                        file.write('\n\n')
                    file.write(line)
                    first_feature = False
                elif '/' in line:
                    # Replace and format qualifiers
                    if '/repeat_len=' in line:
                        line = line.replace('/repeat_len=', '/rpt_unit_range=')
                    elif '/repeat_dist=' in line:
                        line = line.replace('/repeat_dist=', '/note="repeat distance is ') + ' bp"'
                    elif '/repeat_identity=' in line:
                        line = line.replace('/repeat_identity=', '/note="repeat identity is ') + '%"'
                    elif '/ugene_name=' in line:
                        line = line.replace('/ugene_name=', '/standard_name=')
                    line = line.lstrip()
                    file.write(' ' * 21 + line + '\n')
                    # Add color annotation after standard_name
                    if "/standard_name=" in line:
                        color = '255 204 204' if inverted else '204 239 255'
                        file.write(' ' * 21 + '/color={}\n'.format(color))
    except Exception:
        msg = "'{}' selected {} repeats table wasn't written!".format(id, 'inverted' if inverted else 'direct')
        print(msg)
        if log:
            log.write("\n" + msg)

def main():
    global log
    if not len(sys.argv) > 1:
        print_help()
        return

    if param.get('help'):
        print_help()
        return

    if param.get('version'):
        print(version)
        return

    parameters = ""
    if param.get('conf'):
        parameters = validate_conf(param['conf'])

    # Clean up empty keys
    param.pop('', None)

    if not param.get('div'):
        print("Missing GenBank division (-div)!")
        quit()
    else:
        validate_div(param['div'].strip())

    for rng in ('ir', 'er'):
        if rng in param and param[rng] is not None:
            param[rng] = validate_range(param[rng])

    if not param.get('in'):
        print("Missing input file or dir (-in)!")
        quit()

    nseqs = 1
    param['in'] = os.path.realpath(param['in'])
    if os.path.isdir(param['in']):
        files = [os.path.join(os.path.abspath(param['in']), f)
                    for f in os.listdir(param['in'])
                    if os.path.isfile(os.path.join(param['in'], f))]
        if not files:
            print("Directory '{}' is empty!".format(param['in']))
            quit()
        param['in'] = sorted(files)
        nseqs = len(param['in'])
    else:
        param['in'] = [param['in']]

    if 'outdir' in param:
        os.chdir(param['outdir'])

    log = open("file.log", "w")
    log.write('Select_repeats v{} - repeats regions selector\n'.format(version))
    log.write('\nWorking directory:\n{}\n'.format(call))
    log.write('\nCommand line:\n{}\n'.format(" ".join(sys.argv)))
    log.write('\nParameters:\n{}\n'.format(parameters))
    log.write('\nDataset analysis:')
    log.close()

    processed = 0
    for a, input_file in enumerate(param['in']):
        log = open("file.log", "a")
        input_path = find_path(input_file)
        if input_path and validate_input(input_path):
            if get_id(input_path):
                if validate_out_args(param):
                    if convert_EMBL(input_path, param['id']):
                        processed += 1
                        if 'sets' in param and validate_sets(param['sets'], param['id']):
                            ugene_time = datetime.now()
                            ugene_error = False
                            for nset, s in enumerate(param['ugene'], 1):
                                try:
                                    os.system(s)
                                    log.write("{}\n".format(s))
                                except Exception:
                                    ugene_error = True
                                    print("'{}' UGENE set {} didn't finish, skipped!".format(nset, param['id']))
                                    log.write("'{}' UGENE set {} didn't finish, skipped!\n".format(nset, param['id']))
                            if ugene_error:
                                print("'{}' UGENE execution didn't finish, skipped!".format(param['id']))
                                log.write("\n'{}' UGENE execution didn't finish, skipped!".format(param['id']))
                            else:
                                print("UGENE '{}' execution time: {}".format(param['id'], str(datetime.now() - ugene_time)))
                                log.write("UGENE '{}' execution time: {}".format(param['id'], str(datetime.now() - ugene_time)))
                                if 'tmp' in param and os.path.isdir(param['tmp']):
                                    remove_dir(param['tmp'])
                                    os.rmdir(param['tmp'])
                                if param.get('s'):
                                    path = find_path(param['s'])
                                    if path:
                                        param['s'] = path
                                        validate_csv(param)
                                if param.get('selection'):
                                    select_reps(param['finds'], param['id'], param['selection'])
                                else:
                                    select_reps(param['finds'], param['id'], [])
        param.pop('selection', None)
        if 'outdir' in param:
            param['o'] = param['outdir']
        else:
            param['o'] = None
        log.close()

    log = open("file.log", "a")
    execution = datetime.now() - start_time
    log.write("\n\nExecution time: {}".format(execution))
    log.write("\nNumber of processed files: {}".format(processed))
    if processed > 0:
        log.write("\nExecution time per file: {}".format(execution / processed))
    log.close()

    print("\nExecution time: {}".format(execution))
    if processed > 0:
        print("Number of processed files: {}".format(processed))
        print("Execution time per file: {}".format(execution / processed))
    print("\nDone.")

if __name__ == "__main__":
    main()