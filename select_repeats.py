#!/usr/bin/python
import traceback
import warnings
def warn_with_traceback(message, category, filname, reno, fil=None, re=None):

    log = fil if hasattr(fil,'write') else sys.stderr
    traceback.print_stack(fil=log)
    log.write(warnings.formatwarning(message, category, filname, reno, re))

warnings.showwarning = warn_with_traceback

import argparse
import sys
from datetime import datetime
start_time = datetime.now()
import os
import re
param=dict()

version="1.0.0"

help = 'Select_repeats v{} - insertion repeats selector\n'.format(version)
help = help + '(c) 2022. Arthur Gruber & Giuliana Pola\n'
help = help + 'Usage: select_repeats.py -i <EMBL file> -o <output filename> -div <GenBank division> -defi <sequence description>\n'
help = help + 'select_repeats.py -conf <parameters file>\n'
help = help + '\nMandatory parameters:\n'
help = help + '-i <text file>\tFeature table in EMBL format\n'
help = help + '-o <string>\tName of the output file (feature table in GenBank format)\n'
help = help + '-div <three-letter string>\tGenBank division\n'
help = help + '-defi <string>\tSequence definition\n'
help = help + '-conf <text file>\tText file with the parameters\n'
help = help + '\nOptional parameters:\n'

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-i')
parser.add_argument('-o')
parser.add_argument('-div')
parser.add_argument('-defi')
parser.add_argument('-conf')
parser.add_argument('-version', action='store_true')
parser.add_argument('-h', '--help', action='store_true')
args = parser.parse_args()

def rename(name):
  i=2
  if "." in name:
    out='.'.join(name.split(".")[0:-1])+str(i)+name.split(".")[-1]
  else:
    out=name+str(i)
  while os.path.isfile(out):
    i+=1
    if "." in name:
      out='.'.join(name.split(".")[0:-1])+str(i)+name.split(".")[-1]
    else:
      out=name+str(i)
  return out

def validateargs(args):
  valid=True
  if args.i==None:
    print("Missing feature table in EMBL format (-i)")
    valid=False
  elif not os.path.isfile(args.i):
    print("EMBL feature table (-i) not exist!")
    valid=False
  else:
    try:
      open(args.i,"r")
    except:
      print("EMBL feature table (-i) couldn't be opened!")
      valid=False
    else:
      param['i']=args.i
      name=os.path.split(args.i)[-1]
      if "_all_results" in name:
        param['id']=name.split("_all_results")[0]
      elif "." in name:
        param['id']='.'.join(name.split(".")[0:-1])
      else:
        param['id']=name
#  if args.o==None:
#    out=param['id']+'_repeats.gbk'
#    if os.path.isfile(out):
#       print("Output file already exist!")
#       param['o']=rename(out)
#    else:
#       param['o']=out
#  else:
#    if not isinstance(args.o, str):
#      print("Output filename (-o) is not string!")
#      valid=False
#    elif os.path.isfile(args.o):
#      print("Output file already exist!")
#      param['o']=rename(args.o)
#    else:
#      param['o']=args.o
  if args.div==None:
    valid=False
    print("Missing GenBank division (-div)!")
  else:
    if not isinstance(args.div, str):
      print("GenBank division (-div) is not string!")
      valid=False
    elif not args.div.isalpha():
      print("GenBank division (-div) hasn't only letters!")
      valid=False
    elif not len(args.div)==3:
      print("GenBank division (-div) must be only three letters!")
      valid=False
    else:
      param['div']=args.div.upper()
  if args.defi==None:
    valid=False
    print("Missing sequence definition (-defi)!")
  elif not isinstance(args.defi, str):
    print("Sequence definition (-defi) is not string!")
    valid=False
  elif not args.defi.isalpha():
      print("Sequence definition (-defi) hasn't only letters!")
      valid=False
  else:
    param['defi']=args.defi
  return valid,param

def convertEMBL(fil):
  try:
    EMBL=open(fil,"r")
  except:
    print("EMBL feature table file (-i) couldn't be opened!")
    quit()
  else:
    print("Opening EMBL feature table...")
    text=EMBL.read()
    new=''
    if "SQ   Sequence " in text:
      new=text.split("SQ   Sequence ")[0]
      text=text.split("SQ   Sequence ")[1]
      if "FT" in new:
        new=new.replace("FT","  ")
        row=text.split('\n')[0]
        text=text.split('\n')[1:-1]
        row=row.split()
        #print("row: {}".format(row))
        new+='\nBASE COUNT     '
        if all(item in row for item in ["A;","C;","G;","T;"]):
          new+='{} a   '.format(row[row.index("A;")-1])
          new+='{} c   '.format(row[row.index("C;")-1])
          new+='{} g   '.format(row[row.index("G;")-1])
          new+='{} t\nORIGIN\n'.format(row[row.index("T;")-1])
          i=0
          text=text[0:-1]
          for row in text:
           seq=row.split()
           num=seq[-1]
           #print("num:{}".format(num))
           seq=seq[0:-1]
           if '' in seq:
             seq.remove('')
           seq=' '.join(seq)
           if all(item in [' ','a','c','g','t'] for item in seq.lower()):
             try:
               int(num)
             except:
               print("EMBL feature table file (-i) has wrong format, missing nucleotide count!")
               quit()
             else:
               new+=str(i+1).rjust(9," ")+' '+seq+'\n'
               i=int(num)
           else:
             print("EMBL feature table file (-i) has wrong format, sequence contains other than 'a','c','g','t'!")
             quit()
          name=os.path.split(args.i)[-1]
          if "." in name:
            name='.'.join(name.split(".")[0:-1])+"_converted."+name.split(".")[-1]
          else:
            name+="_converted"
          try:
            GenBank=open(name,'w')
          except:
            print("GenBank feature table couldn't be written!")
          else:                      
            print("Writing GenBank converted file...")
            import datetime
            GenBank.write("LOCUS       {}             {} bp    DNA     linear {} {}\n".format(param['id'],i,param['div'],datetime.datetime.now().strftime("%d-%b-%Y").upper()))
            GenBank.write("DEFINITION  {} {}\n".format(param['defi'],param['id']))
            GenBank.write("FEATURES             Location/Qualifiers\n")
            GenBank.write(new)
            GenBank.write("//")
            GenBank.close()
        else:
          print("EMBL feature table file (-i) doesn't contain base count!")
          quit()
      else:
        print("EMBL feature table file (-i) has wrong format, missing 'FT' in lines!")
        quit()
    else:
      print("EMBL feature table file (-i) has wrong format, missing sequence header!")
      quit()

if not len(sys.argv)>1:
  print(help)
elif args.help == True:
  print(help)
elif args.version == True:
  print(version)
else:
  valid,param=validateargs(args)
  if valid:
    print("Valid arguments!")
    convertEMBL(param['i'])