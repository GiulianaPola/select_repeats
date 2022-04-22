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
filtered=[]
log=''
z=-1

version="1.4.0"

print('Select_repeats v{} - repeats regions selector\n'.format(version))

help = 'Select_repeats v{} - repeats regions selector\n'.format(version)
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
help = help + '-r <integer>\tRange of coordinates in which the repetition is accepted\n'
help = help + '-s <csv table file>\tCSV file that has the data for decision making in the selection' 

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-i')
parser.add_argument('-o')
parser.add_argument('-div')
parser.add_argument('-defi')
parser.add_argument('-conf')
parser.add_argument('-r')
parser.add_argument('-s') 
parser.add_argument('-version', action='store_true')
parser.add_argument('-h', '--help', action='store_true')
args = parser.parse_args()
param = args.__dict__

def renamedir(dir):
  i=2
  out=dir+str(i)
  while os.path.isdir(out):
    i+=1
    out=dir+str(i)
  return out

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
           param['i']=value
         elif 'def' in arg:
           param['defi']=value
         elif 'range' in arg or arg=='r':
           param['r']=value
         elif 'csv' in arg or arg=='s':
           param['s']=value 
         elif 'out' in arg or 'o_' in arg or arg=='o':
           #print(param['o'])
           param['o']=value
           if 'dir' in arg:
             param['outdir']=os.path.realpath(value)
             if not os.path.isdir(param['outdir']):
               try:
                 os.mkdir(param['outdir'])
               except:
                 param['outdir']=os.path.join(call,param['outdir'])
                 if not os.path.isdir(param['outdir']):
                   try:
                     os.mkdir(param['outdir'])
                   except:
                     print("Directory '{}' wasn't created!".format(os.path.split(param['outdir'])[-1]))
                     quit()
                   else:
                     print("Creating directory '{}'...".format(os.path.split(param['outdir'])[-1]))
                 else:
                   print("Directory '{}' already exists!".format(os.path.split(param['outdir'])[-1]))
                   param['outdir']=renamedir(param['outdir'])
                   try:
                     os.mkdir(param['outdir'])
                   except:
                     print("Directory '{}' wasn't created!".format(os.path.split(param['outdir'])[-1]))
                     quit()
                   else:
                     print("Creating directory '{}'...".format(os.path.split(param['outdir'])[-1]))
               else:
                 print("Creating directory '{}'...".format(os.path.split(param['outdir'])[-1]))
             else:
               print("Directory '{}' already exists!".format(os.path.split(param['outdir'])[-1]))
               param['outdir']=renamedir(param['outdir'])
               try:
                 os.mkdir(param['outdir'])
               except:
                 print("Directory '{}' wasn't created!".format(os.path.split(param['outdir'])[-1]))
                 quit()
               else:
                 print("Creating directory '{}'...".format(os.path.split(param['outdir'])[-1]))
         elif 'parameter_set' in arg:
           if 'sets' not in param:
             param['sets']=[value] 
           else:
             param['sets'].append(value)
         else:
           param[str(arg)]=value
           
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
    param['div']=div.upper()

def validaterange(range):
  try:
    int(range)
  except:
    print("'{}' (-r) isn't integer!".format(range))
    quit() 
  else:
    #print("234 valid range: '{}'".format(param['r']))
    param['r']=int(range)

def validateinput(file):
  if os.path.isfile(file):
    try:
      open(file,"r")
    except:
      print("'{}' (-i) couldn't be opened, skipped!".format(os.path.split(file)[-1]))
      log.write("\n'{}' (-i) couldn't be opened, skipped!".format(os.path.split(file)[-1]))
      return False
    else:
      return True

def getid(input):
  try:
    name=os.path.split(input)[-1]
    m=re.search(r'(\d)[^\d]*$',name)
    #print(input,name,m)
    param['id']=name[0:m.start()+1]
  except:
    print("'{}' is not a GenBank file, skipped!".format(name))
    log.write("\n'{}' is not a GenBank file, skipped!".format(name))
    return False
  else:
    return True

def validateoutargs(param):
  returned=True
  if param['o'] is None:
    out=[param['id']+'_UGENE.gbk',param['id']+'_repeats.gbk']
  elif 'outdir' in param.keys():
    out=[os.path.join(param['outdir'],param['id']+'_UGENE.gbk'),os.path.join(param['outdir'],param['id']+'_repeats.gbk')]
  else:
    if len(param['o'])==1:
      out=[id+'_UGENE.gbk',param['o']]
    else:
      out=param['o']
  out2=[]
  for o in out:
    if '*' in o:
      o=o.replace('*',param['id'])
    if os.path.isfile(o):
      newname=renamefile(o)
      print("Output file '{}' already exist, creating '{}'!".format(o,newname))
      log.write("\nOutput file '{}' already exist, creating '{}'!".format(o,newname))
      out2.append(newname)
    else:
      out2.append(o)
  param['o']=out2
  if 'defi' not in param.keys():
    print("Missing sequence definition (-defi), skipped!")
    log.write("\nMissing sequence definition (-defi), skipped!")
    returned=False
  elif not isinstance(param['defi'], str):
    print("Sequence definition (-defi) is not string, skipped!")
    log.write("\nSequence definition (-defi) is not string, skipped!")
    returned=False
  else:
    if '*' in param['defi']:
      param['defi']=param['defi'].replace('*',param['id'])
    else:
      param['defi']=param['defi']
  return returned

def convertEMBL(file,id):
  returned=True
  try:
    EMBL=open(file,"r")
  except:
    log.write("\n'{}' (-i) couldn't be opened, skipped!".format(os.path.split(file)[-1]))
    returned=False
  else:
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
        #print("row: '{}'".format(row))
        new+='BASE COUNT     '
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
           #print("num:'{}'".format(num))
           seq=seq[0:-1]
           if '' in seq:
             seq.remove('')
           seq=' '.join(seq)
           if all(item in [' ','a','c','g','t'] for item in seq.lower()):
             try:
               int(num)
             except:
               log.write("\n'{}' (-i) has wrong format, missing nucleotide count, skipped!".format(os.path.split(file)[-1]))
               returned=False
             else:
               new+=str(i+1).rjust(9," ")+' '+seq+'\n'
               i=int(num)
           else:
             log.write("\n'{}' (-i) has wrong format, sequence contains other than 'a','c','g','t',skipped!".format(os.path.split(file)[-1]))
             returned=False
          #print(param['o'])
          try:
            GenBank=open(param['o'][0],'w')
          except:
            log.write("\nGenBank feature table '{}' couldn't be written, skipped!".format(param['o'][0]))
            returned=False
          else:                    
            import datetime
            GenBank.write("LOCUS       {}             {} bp    DNA     linear {} {}\n".format(id,i,param['div'],datetime.datetime.now().strftime("%d-%b-%Y").upper()))
            GenBank.write("DEFINITION  {} {}\n".format(param['defi'],id))
            GenBank.write("FEATURES             Location/Qualifiers\n")
            GenBank.write(new)
            GenBank.write("//")
            GenBank.close()
        else:
          log.write("\n'{}' (-i) doesn't contain base count, skipped!".format(os.path.split(file)[-1]))
          returned=False
      else:
        log.write("\n'{}'(-i) has wrong format, missing 'FT' in lines, skipped!".format(os.path.split(file)[-1]))
        returned=False
    else:
      log.write("\n'{}'(-i) has wrong format, missing sequence header, skipped!".format(os.path.split(file)[-1]))
      returned=False
  if returned==False:
    print("'{}' EMBL table wasn't converted, skipped!".format(id))
  return returned

def validatesets(sets,id):
  valid=[]
  param['finds']=[]
  for s in sets:
    if not '--in=' in s:
      filename = os.path.basename(param['o'][0])
      s+=' --in='+filename
    if not 'ugene' in s:
      s='ugene '+s
    if not '--tmp-dir=' in s:
      s+=' --tmp-dir=tmp'
    else:
      param['tmp']=(s.split('--tmp-dir=')[1]).split()[0]
    if not '--name=' in s:
      if '--inverted=True' in s:
        s+=' --name=TIR'
      elif '--inverted=False' in s:
        s+=' --name=TIR'
    if '*' in s:
      s=s.replace('*', id)
    valid.append(s)
    out=s.split('--out=')[1]
    out=out.split()[0]
    param['finds'].append(out)
  if valid==[]:
    print("UGENE sets aren't valid!")
    log.write("\nUGENE sets aren't valid!")
    return False
  else:
    param['ugene']=valid
    return True

def removedir(folder):
  import os, shutil
  for filename in os.listdir(folder):
      file_path = os.path.join(folder, filename)
      try:
          if os.path.isfile(file_path) or os.path.islink(file_path):
              os.unlink(file_path)
          elif os.path.isdir(file_path):
              shutil.rmtree(file_path)
      except Exception as e:
          log.write('\nFailed to delete %s. Reason: %s' % (file_path, e))

def validatecsv(param):
  returned=True
  if os.path.isfile(param['s']):
    try:
      with open(param['s'],"r") as arquivo:
        text='\n'+arquivo.read().replace("\r","")+'\n'
        index=text.rfind(param['id'])
        if index==-1:
          log.write("\n'{}' was not found in the decision table, selecting '{}' repeats without coordinate restriction!".format(param['id'], param['id']))
          returned=False
        else:
          start=text.rfind('\n',0,index)
          end=text.find('\n',index)
          coordinates=text[start+1:end]
          if ";" in coordinates:
            coordinates=coordinates.split(";")
          elif "\t" in coordinates:
            coordinates=coordinates.split("\t")
          elif "," in coordinates:
            coordinates=coordinates.split(",")
          elif " " in coordinates:
            coordinates=coordinates.split(" ")
          else:
            returned=False
            log.write("\nDecision table (-s) delimiter not recognized, selecting '{}' repeats without coordinate restriction!".format(param['id']))
          if returned==True:
            while '' in coordinates:
                coordinates.remove('')
            #print("385 Coordinates: '{}'".format(coordinates))
            numbers=[]
            for element in coordinates:
              try:
                int(element)
              except:
                pass
              else:
                numbers.append(int(element))
            numbers=list(sorted(numbers))
            #print("395 Numbers: '{}'".format(numbers))
            if len(numbers)==2:
              coordinates=[]
              for number in numbers:
                coordinates.append(number-param['r'])
                coordinates.append(number+param['r'])
              #print("401 Coordinates: '{}'".format(coordinates))
            else:
              returned=False
              log.write("\nDecision table (-s) has only one coordinate, selecting '{}' repeats without coordinate restriction!".format(param['id']))
            if len(coordinates)==4 and (len(set(coordinates)) == len(coordinates)):
              param['coordinates']=coordinates
            else:
              returned=False
              log.write("\nTwo or more coordinates of acceptable range are equal, selecting '{}' repeats without coordinate restriction!".format(param['id']))
    except:
      log.write("\n'{}' (-s) couldn't be opened!".format(os.path.split(param['s'])[-1]))
      returned=False
  if returned==False:
    print("Decision table is not valid, selecting '{}' repeats without coordinate restriction!".format(param['id']))

def select_reps(finds,id):
  log.write("\nFiltering '{}' regions from {} to {} and {} to {}...".format(id,param['coordinates'][0],param['coordinates'][1],param['coordinates'][2],param['coordinates'][3]))
  direct=dict()
  inverted=dict()
  for find in finds:
      try:
        file=open(find,"r")
      except:
        log.write("\nUGENE '{}' file wasn't opened!".format(os.path.split(find)[-1]))
      else:
        text=file.read()
        import re
        start=[m.start() for m in re.finditer("repeat_region   join", text)]
        start.append(len(text))
        regions=[text[start[i]:start[i+1]] for i in range(len(start)-1)]
        for region in regions:
          key=region[region.find("(")+1:region.find(")")]
          end=region.find("\n",region.find("/ugene_name="))+3
          repeat=region[0:end]
          #print(repeat)
          valid=True
          #print("param['coordinates']:'{}'".format(param['coordinates']))
          if 'coordinates' in param.keys():
            coordinates=[]
            for coordinate in key.split(","):
              if coordinates==[]:
                coordinates.append(int(coordinate.split("..")[0]))
              else:
                coordinates.append(int(coordinate.split("..")[-1]))
            coordinates=list(sorted(coordinates))
            #print("coordinates:'{}'".format(coordinates))
            if coordinates[0]>=param['coordinates'][0] and coordinates[0]<=param['coordinates'][1] and coordinates[1]>=param['coordinates'][2] and coordinates[1]<=param['coordinates'][3]:
              valid=True
            else:
              valid=False
              if '/rpt_type="inverted"' in repeat or '/ugene_name="TIR"' in repeat:
                if "Inverted '{}'".format(id) not in filtered:
                  log.write("\nInverted '{}' was filtered!".format(id))
                  filtered.append("Inverted '{}'".format(id))
              elif "Direct '{}'".format(id) not in filtered:
                log.write("\nDirect '{}' was filtered!".format(id))
                filtered.append("Direct '{}'".format(id))
          if valid:
            if '/rpt_type="inverted"' in repeat or '/ugene_name="TIR"' in repeat:
              if key not in inverted.keys():
                inverted[key]=repeat
            else:
              if key not in direct.keys():
                direct[key]=repeat
  writerepeatstable(direct,False,id)
  writerepeatstable(inverted,True,id)

def writerepeatstable(repeats,inverted,id):
  if inverted==True:
    filename="{}_inverted_repeats_selected.gbk".format(id)
  else:
    filename="{}_direct_repeats_selected.gbk".format(id)
  try:
    open(filename,'w')
  except:
    print("'{}' selected repeat regions table wasn't written!".format(id))
    log.write("\n'{}' selected repeat regions table wasn't written!".format(id))
  else:
    with open(filename,'w') as file:
      lines=''.join(repeats.values()).split('\n')
      if '' in lines:
        lines.remove('')
      i=0
      for line in lines:
        if not line.lstrip()=='':
          if 'repeat_region   join' in line:
            words=line.split()
            if '' in words:
              words.remove('')
            if inverted==False:
              line+=' '*21+'/rpt_type=direct\n' 
            line=' '*5+words[0]+' '*3+words[1]+'\n'
            if i>0:
              line='\n\n'+line
          
          elif '/' in line:
            if '/repeat_len=' in line:
              line=line.replace('/repeat_len=','/rpt_unit_range=')
            elif '/repeat_dist=' in line:
              line=line.replace('/repeat_dist=','/note="repeat distance is ')+' bp"'
            elif '/repeat_identity=' in line:
              line=line.replace('/repeat_identity=','/note="repeat identity is ')+'%"'
            elif '/ugene_name=' in line:
              line=line.replace('/ugene_name=','/standard_name=')
            line=line.lstrip()
            line=' '*21+line+'\n'
            if "/standard_name=" in line:
              if inverted==True:
                line+=' '*21+'/color=255 204 204'
              else:
                line+=' '*21+'/color=204 239 255'
          file.write(line)
        i+=1

if not len(sys.argv)>1:
  print(help)
elif param['help'] == True:
  print(help)
elif param['version'] == True:
  print(version)
else:
  #print(param)
  if not param['conf'] is None:
    validateconf(param['conf'])
  while '' in param.keys():
    param.pop('')
  if param['div'] is None:
    print("Missing GenBank division (-div)!")
    quit()
  else:
    validatediv(param['div'].strip())
  if 'r' in param.keys():
    validaterange(param['r'])
  if param['i'] is None:
    print("Missing input file or dir (-i)!")
    quit()
  else:
    z=1
    param['i']=os.path.realpath(param['i'])
    parameters='\n'.join(str(param)[1:-1].split(', '))
    if os.path.isdir(param['i']):
      if len(os.listdir(param['i'])) == 0:
        print("Directory '{}' (-i) is empty!".format(param['i']))
        quit()
      else:
        param['i'] = [os.path.join(os.path.abspath(param['i']),f) for f in os.listdir(param['i']) if os.path.isfile(os.path.join(param['i'], f))]
        z=len(param['i'])
    a=0
    if 'outdir' in param:
      log=open(os.path.join(param['outdir'],"file.log"),"w")
    else:
      log=open("file.log","w")
    log.write('Current working directory: {}'.format(call))
    log.write('\n{}\n'.format(' '.join(sys.argv)))
    log.write('\nSelect_repeats v{} - repeats regions selector\n'.format(version))
    log.write('\nParameters:\n{}'.format(parameters))
    #print("param['i']='{}'".format(param['i']))
    while a<z:
      if z>1:
        input=param['i'][a]
      else:
        input="".join(param['i'])
      #print("input='{}'".format(input))
      log.write("\n\nOpening '{}' (-i)...".format(os.path.split(input)[-1]))
      print("\nOpening '{}' (-i)...".format(os.path.split(input)[-1]))
      if validateinput(input):
        if getid(input):
         validateoutargs(param)
         #print(param)
         if 'outdir' in param.keys():
               os.chdir(param['outdir'])
         if convertEMBL(input,param['id']):
           if 'sets' in param.keys():
             if validatesets(param['sets'],param['id']):
                ugene_time = datetime.now()
                print("Executing UGENE...")
                for s in param['ugene']:
                  os.system(s)
                print("UGENE '{}' execution time: {}".format(param['id'],datetime.now() - ugene_time))
                log.write("\nUGENE '{}' execution time: {}".format(param['id'],datetime.now() - ugene_time))
                if os.path.isdir('tmp'):
                  removedir('tmp')
                  os.rmdir('tmp')
                elif 'tmp' in param.keys() and os.path.isdir(param['tmp']):
                  removedir(param['tmp'])
                  os.rmdir(param['tmp'])
                if 's' in param.keys():
                  validatecsv(param) 
                select_reps(param['finds'],param['id'])
        if 'coordinates' in param.keys():
          param.pop('coordinates')
        if 'outdir' in param.keys():
          param['o']=param['outdir']
        else:
          param['o']=None
        a+=1
import io
if isinstance(log, io.TextIOBase):
  log.write("\n\nExecution time: {}".format(datetime.now() - start_time))
  log.close()
print("\nExecution time: {}".format(datetime.now() - start_time))