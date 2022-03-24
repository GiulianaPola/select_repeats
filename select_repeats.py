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
call=os.path.abspath(os.getcwd())

version="1.1.2"

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
my_dict = args.__dict__

def getid(input):
  try:
    name=os.path.split(input)[-1]
    m=re.search(r'(\d)[^\d]*$',name)
    #print(input,name,m)
    return name[0:m.start()+1]
  except:
    print("{} is not a GenBank file, skipped!".format(name))
    return False
    
def renamefile(file):
  i=2
  filename, file_extension = os.path.splitext(file)
  if not file_extension=='':
    out=filename+str(i)+'.'+file_extension
  else:
    out=filename+str(i)
  while os.path.isfile(out):
    i+=1
    if not file_extension=='':
      out=filename+str(i)+'.'+file_extension
    else:
      out=filename+str(i)
  return out
  
def renamedir(dir):
  i=2
  out=dir+str(i)
  while os.path.isdir(out):
    i+=1
    out=dir+str(i)
  return out

def validateconf(conf):
  if not os.path.isfile(conf):
      print("Configuration file (-conf) doesn't exist!")
      quit()
  else:
      file=open(conf,'r')
      lines=file.read().split('\n')
      if '' in lines:
        lines.remove('')
      if ' ' in lines:
        lines.remove(' ')
      for lin in lines:
        arg=lin.split('=')[0].strip().strip('\"')
        #print(arg)
        if not arg.isspace():
         value='='.join(lin.split('=')[1:]).strip().strip('\"')
         if ' e ' in value:
           value=value.split(' e ')
         if 'input' in arg or 'i_' in arg or arg=='i':
           my_dict['i']=value
         elif 'def' in arg:
           my_dict['defi']=value
         elif 'out' in arg or 'o_' in arg or arg=='o':
           #print(my_dict['o'])
           my_dict['o']=value
           if 'dir' in arg:
             my_dict['dir']=os.path.realpath(value)
             if not os.path.isdir(my_dict['dir']):
               try:
                 os.mkdir(my_dict['dir'])
               except:
                 my_dict['dir']=os.path.join(call,my_dict['dir'])
                 if not os.path.isdir(my_dict['dir']):
                   os.mkdir(my_dict['dir'])
                   print("Creating directory {}...".format(my_dict['dir']))
                 else:
                   print("Directory {} already exists!".format(my_dict['dir']))
                   my_dict['dir']=renamedir(my_dict['dir'])
                   os.mkdir(my_dict['dir'])
                   print("Creating directory {}...".format(my_dict['dir']))
               else:
                 print("Creating directory {}...".format(my_dict['dir']))
             else:
               print("Directory {} already exists!".format(my_dict['dir']))
               my_dict['dir']=renamedir(my_dict['dir'])
               os.mkdir(my_dict['dir'])
               print("Creating directory {}...".format(my_dict['dir']))
         elif 'parameter_set' in arg:
           if 'sets' not in my_dict:
             my_dict['sets']=[value] 
           else:
             my_dict['sets'].append(value)
         else:
           my_dict[str(arg)]=value

def validatediv(div):
  if not isinstance(div, str):
    print("GenBank division (-div) is not string!")
    quit()
  elif not div.isalpha():
    print(div)
    print("GenBank division (-div) hasn't only letters!")
    quit()
  elif not len(div)==3:
    print("GenBank division (-div) must be only three letters!")
    quit()
  else:
    my_dict['div']=div.upper()

def validateinput(file):
  if os.path.isfile(file):
    try:
      open(file,"r")
    except:
      print("{} (-i) couldn't be opened!".format(os.path.split(file)[-1]))
      quit()

def validateargs(my_dict,id):
  if my_dict['o'] is None:
    out=[id+'_UGENE.gbk',id+'_repeats.gbk']
  elif 'dir' in my_dict.keys():
    out=[os.path.join(my_dict['dir'],id+'_UGENE.gbk'),os.path.join(my_dict['dir'],id+'_repeats.gbk')]
  else:
    if len(my_dict['o'])==1:
      out=[id+'_UGENE.gbk',my_dict['o']]
    else:
      out=my_dict['o']
  out2=[]
  for o in out:
    if not isinstance(o, str):
      print("Output filename (-o) is not string!")
      quit()
    elif '*' in o:
      o=o.replace('*',id)
    if os.path.isfile(o):
      print("Output file already exist!")
      out2.append(renamefile(o))
    else:
      out2.append(o)
  my_dict['o']=out2
  if 'defi' not in my_dict.keys():
    print("Missing sequence definition (-defi)!")
    quit()
  elif not isinstance(my_dict['defi'], str):
    print("Sequence definition (-defi) is not string!")
    quit()
  else:
    if '*' in my_dict['defi']:
      my_dict['defi']=my_dict['defi'].replace('*',id)
    else:
      my_dict['defi']=my_dict['defi']

def validatesets(sets,id):
  sets=';'.join(sets)
  if '*' in sets:
    sets=sets.replace('*', id)
    sets=sets.split(';')
    my_dict['sets']=sets
  else:
    my_dict['sets']=sets

def convertEMBL(file,id):
  try:
    EMBL=open(file,"r")
  except:
    print("{} (-i) couldn't be opened, skipped!".format(os.path.split(file)[-1]))
    return False
  else:
    print("Opening {} (-i)...".format(os.path.split(file)[-1]))
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
               print("{} (-i) has wrong format, missing nucleotide count, skipped!".format(os.path.split(file)[-1]))
               return False
             else:
               new+=str(i+1).rjust(9," ")+' '+seq+'\n'
               i=int(num)
           else:
             print("{} (-i) has wrong format, sequence contains other than 'a','c','g','t',skipped!".format(os.path.split(file)[-1]))
             return False
          #print(my_dict['o'])
          try:
            GenBank=open(my_dict['o'][0],'w')
          except:
            print("GenBank feature table {} couldn't be written, skipped!".format(my_dict['o'][0]))
            return False
          else:                      
            print("Writing GenBank converted file...")
            import datetime
            GenBank.write("LOCUS       {}             {} bp    DNA     linear {} {}\n".format(id,i,my_dict['div'],datetime.datetime.now().strftime("%d-%b-%Y").upper()))
            GenBank.write("DEFINITION  {} {}\n".format(my_dict['defi'],id))
            GenBank.write("FEATURES             Location/Qualifiers\n")
            GenBank.write(new)
            GenBank.write("//")
            GenBank.close()
            return True
        else:
          print("{} (-i) doesn't contain base count,skipped!".format(os.path.split(file)[-1]))
          return False
      else:
        print("{}(-i) has wrong format, missing 'FT' in lines, skipped!".format(os.path.split(file)[-1]))
        return False
    else:
      print("{}(-i) has wrong format, missing sequence header, skipped!".format(os.path.split(file)[-1]))
      return False

if not len(sys.argv)>1:
  print(help)
elif my_dict['help'] == True:
  print(help)
elif my_dict['version'] == True:
  print(version)
else:
  #print(my_dict)
  if not my_dict['conf'] is None:
    validateconf(my_dict['conf'])
  if my_dict['div'] is None:
    print("Missing GenBank division (-div)!")
    quit()
  else:
    validatediv(my_dict['div'].strip())
  if my_dict['i'] is None:
    print("Missing input file or dir (-i)!")
    quit()
  else:
    z=1
    my_dict['i']=os.path.realpath(my_dict['i'])
    if os.path.isdir(my_dict['i']):
      if len(os.listdir(my_dict['i'])) == 0:
        print("{} (-i) is empty!".format(my_dict['i']))
        quit()
      else:
        my_dict['i'] = [os.path.join(os.path.abspath(my_dict['i']),f) for f in os.listdir(my_dict['i']) if os.path.isfile(os.path.join(my_dict['i'], f))]
        z=len(my_dict['i'])
    a=0
    #print("my_dict['i']={}".format(my_dict['i']))
    while a<z:
      if z>1:
        input=my_dict['i'][a]
      else:
        input=my_dict['i']
      #print("input={}".format(input))
      validateinput(input)
      id=getid(input)
      if not id==False:
       validateargs(my_dict,id)
       #print(param)
       converted=convertEMBL(input,id)
       if not converted==False:
         if 'sets' in my_dict.keys():
           validatesets(my_dict['sets'],id)
      if 'dir' in my_dict.keys():
        my_dict['o']=my_dict['dir']
      else:
        my_dict['o']=None
      a+=1