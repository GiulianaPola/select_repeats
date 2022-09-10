#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback
import warnings
import io
import argparse
import sys
from datetime import datetime
import os
import re
import ntpath

def warn_with_traceback(message, category, filname, reno, fil=None, re=None):

    log = fil if hasattr(fil,'write') else sys.stderr
    traceback.print_stack(fil=log)
    log.write(warnings.formatwarning(message, category, filname, reno, re))

warnings.showwarning = warn_with_traceback


start_time = datetime.now()
param=dict()
call=os.path.abspath(os.getcwd())
log=None
nseqs=-1
processed=0

version="1.5.2"

print('Select_repeats v{} - repeats regions selector\n'.format(version))

#help = 'Select_repeats v{} - repeats regions selector\n'.format(version)
help = '(c) 2022. Arthur Gruber & Giuliana Pola\n'
help = help + 'Usage: select_repeats.py -in <EMBL file> -o <output filename> -div <GenBank division> -defi <sequence description>\n'
help = help + 'select_repeats.py -conf <parameters file>\n'
help = help + '\nMandatory parameters:\n'
help = help + '-in <text file>\tFeature table in EMBL format\n'
help = help + '-o <string>\tName of the output file (feature table in GenBank format)\n'
help = help + '-div <three-letter string>\tGenBank division\n'
help = help + '-defi <string>\tSequence definition\n'
help = help + '-conf <text file>\tText file with the parameters\n'
help = help + '\nOptional parameters:\n'
help = help + '-ir <integer>\tInternal range of coordinates in which the repetition is accepted\n'
help = help + '-er <integer>\tExternal range of coordinates in which the repetition is accepted\n'
help = help + '-s <csv table file>\tCSV file that has the data for decision making in the selection' 

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-in')
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
param = args.__dict__

def getfilename(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def renamedir(dir):
  i=1
  out=dir+"("+str(i)+")"
  while os.path.isdir(out):
    i+=1
    out=dir+"("+str(i)+")"
  return out

def renamefile(file):
  i=1
  filename, file_extension = os.path.splitext(file)
  if not file_extension=='':
    out=filename+"("+str(i)+")"+'.'+file_extension
  else:
    out=filename+"("+str(i)+")"
  while os.path.isfile(out):
    i+=1
    if not file_extension=='':
      out=filename+"("+str(i)+")"+'.'+file_extension
    else:
      out=filename+"("+str(i)+")"
  return out

def validateconf(conf):
  parameters=[]
  #print("85 Validando configuração...")
  if not os.path.isfile(conf):
      print(getfilename(conf)," (-conf) doesn't exist!")
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
         if 'input' in arg or 'i_' in arg or arg=='i' or arg=='in':
           parameters.append(lin)
           path=findpath(value)
           if path == None:
             print("'{}' (-in) doesn't exist".format(value))
             quit()
           else:
             param['in']=path
         elif 'def' in arg:
           param['defi']=value
           parameters.append(lin)
         elif arg=='r':
           param['er']=value
           param['ir']=value
           parameters.append(lin)
         elif 'external range' in arg or arg=='er':
           param['er']=value
           parameters.append(lin)
         elif 'internal range' in arg or arg=='ir':
           param['ir']=value
           parameters.append(lin)
         elif 'csv' in arg or arg=='s':
           param['s']=os.path.realpath(value)
           parameters.append(lin)
         elif 'out' in arg or 'o_' in arg or arg=='o':
           #print(param['o'])
           param['o']=value
           parameters.append(lin)
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
                     print("Directory '{}' wasn't created!".format(getfilename(param['outdir'])))
                     quit()
                   else:
                     print("Creating directory '{}'...".format(getfilename(param['outdir'])))
                 else:
                   print("Directory '{}' already exists!".format(getfilename(param['outdir'])))
                   param['outdir']=renamedir(param['outdir'])
                   try:
                     os.mkdir(param['outdir'])
                   except:
                     print("Directory '{}' wasn't created!".format(getfilename(param['outdir'])))
                     quit()
                   else:
                     print("Creating directory '{}'...".format(getfilename(param['outdir'])))
               else:
                 print("Creating directory '{}'...".format(getfilename(param['outdir'])))
             else:
               print("Directory '{}' already exists!".format(getfilename(param['outdir'])))
               param['outdir']=renamedir(param['outdir'])
               try:
                 os.mkdir(param['outdir'])
               except:
                 print("Directory '{}' wasn't created!".format(getfilename(param['outdir'])))
                 quit()
               else:
                 print("Creating directory '{}'...".format(getfilename(param['outdir'])))
         elif 'parameter_set' in arg or 'set' in arg:
           parameters.append(lin)
           if 'sets' not in param:
             param['sets']=[value]
           else:
             param['sets'].append(value)
         else:
           param[str(arg)]=value
  return "\n".join(parameters)
           
def validatediv(div):
  #print("160 Validando div...")
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
  #print("175 Validando range...")
  try:
    int(range)
  except:
    print("'{}' (range) isn't integer!".format(range))
    quit() 
  else:
    #print("234 valid range: '{}'".format(param['r']))
    return int(range)

def findpath(tail):
  paths=[]
  paths.append(os.path.realpath(tail))
  paths.append(os.path.join(call,tail))
  if 'conf' in param:
    if not param['conf']==None:
      #print(param['conf'])
      path=os.path.split(os.path.realpath(param['conf']))
      if not path[0]==None:
       paths.append(os.path.join(path[0],tail))
  #print(paths)
  tail=None
  for p in paths:
    if os.path.exists(p):
      tail=p
      break
  #print("199 Input=",tail)
  return tail

def validateinput(file):
  #print("186 Validando input...")
  try:
    open(file,"r")
  except:
    print("'{}' (-in) couldn't be opened, skipped!".format(getfilename(file)))
    log.write("\n'{}' (-in) couldn't be opened, skipped!".format(getfilename(file)))
    return False
  else:
    print("\nOpening '{}' (-in)...".format(getfilename(file)))
    log.write("\n\nOpening '{}' (-in)...".format(getfilename(file)))
    return True

def getid(input):
  #print("200 Extraindo id...")
  try:
    name=getfilename(input)
    m=re.search(r'(\d)[^\d]*$',name)
    #print(input,name,m)
    param['id']=name[0:m.start()+1]
  except:
    print("'{}' is not a GenBank file, skipped!".format(getfilename(input)))
    log.write("\n'{}' is not a GenBank file, skipped!".format(getfilename(input)))
    return False
  else:
    return True

def validateoutargs(param):
  #print("214 Validando outargs....")
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
  #print("253 Convertendo EMBL...")
  returned=True
  try:
    EMBL=open(file,"r")
  except:
    log.write("\n'{}' (-in) couldn't be opened, skipped!".format(getfilename(file)))
    returned=False
  else:
    text=EMBL.read()
    new=''
    if "SQ   Sequence " in text:
      new='\n'+text.split("SQ   Sequence ")[0]
      text=text.split("SQ   Sequence ")[1]
      if "FT" in new:
        new=new.replace("\nFT","\n  ")
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
           if all(item in [' ','a','c','g','t','n'] for item in seq.lower()):
             try:
               int(num)
             except:
               log.write("\n'{}' (-in) has wrong format, missing nucleotide count, skipped!".format(getfilename(file)))
               returned=False
               break
             else:
               new+=str(i+1).rjust(9," ")+' '+seq+'\n'
               i=int(num)
           else:
             log.write("\n'{}' (-in) has wrong format, sequence contains other than 'a','c','g','t','n',skipped!".format(getfilename(file)))
             returned=False
             break
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
            GenBank.write("FEATURES             Location/Qualifiers")
            GenBank.write(new)
            GenBank.write("//")
            GenBank.close()
        else:
          log.write("\n'{}' (-in) doesn't contain base count, skipped!".format(getfilename(file)))
          returned=False
      else:
        log.write("\n'{}'(-in) has wrong format, missing 'FT' in lines, skipped!".format(getfilename(file)))
        returned=False
    else:
      log.write("\n'{}'(-in) has wrong format, missing sequence header, skipped!".format(getfilename(file)))
      returned=False
  if returned==False:
    print("'{}' EMBL table wasn't converted, skipped!".format(id))
  else:
    print("'{}' EMBL table was converted!".format(id))
    log.write("\n'{}' EMBL table was converted!".format(id))
  return returned

def validatesets(sets,id):
  #print('331 Validando sets...')
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
      if 'outdir' in param.keys():
        param['tmp']=os.path.join(param['outdir'],'tmp')
      else:
        param['tmp']=os.path.join(call,'tmp')
    else:
      if 'outdir' in param.keys():
        param['tmp']=os.path.join(param['outdir'],(s.split('--tmp-dir=')[1]).split()[0])
      else:
        param['tmp']=os.path.join(call,(s.split('--tmp-dir=')[1]).split()[0])
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
  #print("371 Excluindo pasta...")
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
  #print("429 Validando csv...{}".format(param['s']))
  returned=True
  if os.path.isfile(param['s']):
    file=param['s']
  else:
    file=os.path.join(call,param['s'])
  try:
    arquivo=open(file,"r")
  except:
    print("'{}' (-s) couldn't be opened!".format(getfilename(param['s'])))
    log.write("'{}' (-s) couldn't be opened!".format(getfilename(param['s'])))
    returned=False
  else:
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
        log.write("\nDecision table (-s) delimiter not recogninsed, selecting '{}' repeats without coordinate restriction!".format(param['id']))
      if returned==True:
        while '' in coordinates:
            coordinates.remove('')
        numbers=[]
        for element in coordinates:
          try:
            int(element)
          except:
            pass
          else:
            numbers.append(int(element))
        numbers=list(sorted(numbers))
        #print("474 Numbers: {}".format(numbers))
        if len(numbers)==2 and len(set(numbers))==len(numbers):
          log.write("\nCoordinates '{}': {}..{}".format(param['id'],numbers[0],numbers[1]))
          coordinates=[]
          if param['ir']==None and param['er']==None:
            coordinates=numbers
          elif param['er']==None and not param['ir']==None:
            coordinates.append(min(numbers)+param['ir'])
            coordinates.append(max(numbers)-param['ir'])
          elif param['ir']==None and not param['er']==None:
            coordinates.append(min(numbers)-param['er'])
            coordinates.append(max(numbers)+param['er'])
          elif not(param['ir']==None and param['er']==None):
            coordinates.append(min(numbers)-param['er'])
            coordinates.append(min(numbers)+param['ir'])
            coordinates.append(max(numbers)-param['ir'])
            coordinates.append(max(numbers)+param['er'])
          param['selection']=coordinates
        else:
          returned=False
          log.write("\nDecision table (-s) has only one unique coordinate, selecting '{}' repeats without coordinate restriction!".format(param['id']))
  if returned==False:
    print("Decision table (-s) is not valid, selecting '{}' repeats without coordinate restriction!".format(param['id']))

def select_reps(finds,id,selection):
  #print("499 Selecionando repetições {}...".format(selection))
  filtered=[]
  direct=dict()
  inverted=dict()
  if not selection==[]:
    if len(selection)==4:
      log.write("\nLimit of '{}' repeats filtering: {}..{}, {}..{}".format(id,selection[0],selection[1],selection[2],selection[3]))
      print("Limit of '{}' repeats filtering: {}..{}, {}..{}".format(id,selection[0],selection[1],selection[2],selection[3]))
    elif len(selection)==2:
      log.write("\nLimit of '{}' repeats filtering: {}..{}".format(id,selection[0],selection[1]))
      print("Limit of '{}' repeats filtering: {}..{}".format(id,selection[0],selection[1]))
  for find in finds:
      try:
        file=open(find,"r")
      except:
        log.write("\nUGENE '{}' file wasn't opened!".format(getfilename(find)))
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
          #print("param['selection']:'{}'".format(param['selection']))
          if not selection==[]:
            coordinates=[]
            for coordinate in key.split(","):
              #print(coordinate)
              if coordinates==[]:
                coordinates.append(int(coordinate.split("..")[0]))
              else:
                coordinates.append(int(coordinate.split("..")[-1]))
            coordinates=list(sorted(coordinates))
            #print("coordinates:'{}'".format(coordinates))
            if len(selection)==4:
              if coordinates[0]>=selection[0] and coordinates[0]<=selection[1] and coordinates[1]>=selection[2] and coordinates[1]<=selection[3]:
                valid=True
              else:
                valid=False
            elif len(selection)==2:
              if coordinates[0]>=selection[0] and coordinates[1]<=selection[-1]:
                valid=True
              else:
                valid=False
          if valid:
            if '/rpt_type="inverted"' in repeat or '/ugene_name="TIR"' in repeat:
              if key not in inverted.keys():
                inverted[key]=repeat
            else:
              if key not in direct.keys():
                direct[key]=repeat
          else:
            if '/rpt_type="inverted"' in repeat or '/ugene_name="TIR"' in repeat:
              if "Inverted '{}'".format(id) not in filtered:
                  log.write("\nInverted '{}' was filtered!".format(id))
                  filtered.append("Inverted '{}'".format(id))
              elif "Direct '{}'".format(id) not in filtered:
                log.write("\nDirect '{}' was filtered!".format(id))
                filtered.append("Direct '{}'".format(id))

  if not filtered==[] and not selection==[]:
    print("'{}' repeat regions were selected!".format(id))
    log.write("\n'{}' repeat regions were selected!".format(id))
  elif filtered==[]:
    print("All '{}' repeat regions are within the filtering limits!".format(id))

  if not direct=={}:
    writerepeatstable(direct,False,id)
    if not "Direct '{}'".format(id) in filtered:
      log.write("\nAll '{}' direct repeat regions are within the filtering limits!".format(id))
  elif "Direct '{}'".format(id) in filtered:
    log.write("\nAll '{}' direct repeat regions are outside the filtering limits!".format(id))

  if not inverted=={}:
    writerepeatstable(inverted,True,id)
    if not "Inverted '{}'".format(id) in filtered:
      log.write("\nAll '{}' inverted repeat regions are within the filtering limits!".format(id))
  elif "Inverted '{}'".format(id) in filtered:
    log.write("\nAll '{}' inverted repeat regions are outside the filtering limits!".format(id))

def writerepeatstable(repeats,inverted,id):
  #print("505 Escrevendo tabela de repetições...")
  if inverted==True:
    filename="{}_inverted_repeats_selected.gbk".format(id)
  else:
    filename="{}_direct_repeats_selected.gbk".format(id)
  try:
    open(filename,'w')
  except:
    if inverted==True:
      print("'{}' selected inverted repeats table wasn't written!".format(id))
      log.write("\n'{}' selected inverted repeat regions table wasn't written!".format(id))
    else:
      print("'{}' selected direct repeats table wasn't written!".format(id))
      log.write("\n'{}' selected direct repeats table wasn't written!".format(id))
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
    parameters=validateconf(param['conf'])
  while '' in param.keys():
    param.pop('')
  if param['div'] is None:
    print("Missing GenBank division (-div)!")
    quit()
  else:
    validatediv(param['div'].strip())
  if 'ir' in param.keys():
    if not param['ir']==None:
      param['ir']=validaterange(param['ir'])
  if 'er' in param.keys():
    if not param['er']==None:
      param['er']=validaterange(param['er'])
  if param['in'] is None:
    print("Missing input file or dir (-in)!")
    quit()
  else:
    nseqs=1
    param['in']=os.path.realpath(param['in'])
    if os.path.isdir(param['in']):
      if len(os.listdir(param['in'])) == 0:
        print("Directory '{}'  is empty!".format(param['in']))
        quit()
      else:
        param['in'] = [os.path.join(os.path.abspath(param['in']),f) for f in os.listdir(param['in']) if os.path.isfile(os.path.join(param['in'], f))]
        param['in'].sort()
        nseqs=len(param['in'])
    if 'outdir' in param.keys():
      os.chdir(param['outdir'])
    a=0
    log=open("file.log","w")
    log.write('Select_repeats v{} - repeats regions selector\n'.format(version))
    log.write('\nWorking directory:\n{}\n'.format(call))
    log.write('\nCommand line:\n{}\n'.format(' '.join(sys.argv)))
    log.write('\nParameters:\n{}\n'.format(parameters))
    log.write('\nDataset analysis:')
    log.close()
    #print("param['in']='{}'".format(param['in']))
    while a<nseqs:
      log=open("file.log","a")
      if nseqs>1:
        input=param['in'][a]
      else:
        input="".join(param['in'])
      #print("input='{}'".format(input))
      input=findpath(input)
      if (not input==None) and validateinput(input):
        if getid(input):
         validateoutargs(param)
         #print(param)
         if convertEMBL(input,param['id']):
           processed+=1
           if 'sets' in param.keys():
             if validatesets(param['sets'],param['id']):
                ugene_time = datetime.now()
                ugene_error=False
                nset=0
                for s in param['ugene']:
                  nset+=1
                  try:
                    os.system(s)
                  except:
                    ugene_error=True
                    print("'{}' UGENE set {} didn't finish, skipped!".format(nset,param['id']))
                    print("\n'{}' UGENE set {} didn't finish, skipped!".format(nset,param['id']))
                if ugene_error==True:
                  print("'{}' UGENE execution didn't finish, skipped!".format(param['id']))
                  log.write("\n'{}' UGENE execution didn't finish, skipped!".format(param['id']))
                else:
                  print("UGENE '{}' execution time: {}".format(param['id'],datetime.now() - ugene_time))
                  log.write("\nUGENE '{}' execution time: {}".format(param['id'],datetime.now() - ugene_time))
                  if 'tmp' in param.keys() and os.path.isdir(param['tmp']):
                    removedir(param['tmp'])
                    os.rmdir(param['tmp'])
                  if 's' in param.keys():
                    if not param['s']==None:
                      path=findpath(param['s'])
                      if not path==None:
                        param['s']=path
                        validatecsv(param)
                  if 'selection' in param.keys() and not param['selection']==[]:
                    select_reps(param['finds'],param['id'],param['selection'])
                  else:
                    select_reps(param['finds'],param['id'],[])
      if 'selection' in param.keys():
        param.pop('selection')
      if 'outdir' in param.keys():
        param['o']=param['outdir']
      else:
        param['o']=None
      a+=1
      log.close()
  log=open("file.log","a")
  execution=datetime.now() - start_time
  if not log==None:
    log.write("\n\nExecution time: {}".format(execution))
    log.write("\nNumber of processed files: {}".format(processed))
    if processed>0:
      log.write("\nExecution time per file: {}".format(execution/processed))
    log.close()
  print("\nExecution time: {}".format(execution))
  if processed>0:
    print("Number of processed files: {}".format(processed))
    print("Execution time per file: {}".format(execution/processed))