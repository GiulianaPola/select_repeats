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

version="1.3.2"

print('Select_repeats v{} - insertion repeats selector\n'.format(version))

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
param = args.__dict__

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
           param['i']=value
         elif 'def' in arg:
           param['defi']=value
         elif 'out' in arg or 'o_' in arg or arg=='o':
           #print(param['o'])
           param['o']=value
           if 'dir' in arg:
             param['dir']=os.path.realpath(value)
             if not os.path.isdir(param['dir']):
               try:
                 os.mkdir(param['dir'])
               except:
                 param['dir']=os.path.join(call,param['dir'])
                 if not os.path.isdir(param['dir']):
                   os.mkdir(param['dir'])
                   print("Creating directory {}...".format(param['dir']))
                   
                 else:
                   print("Directory {} already exists!".format(param['dir']))
                   param['dir']=renamedir(param['dir'])
                   os.mkdir(param['dir'])
                   print("Creating directory {}...".format(param['dir']))
               else:
                 print("Creating directory {}...".format(param['dir']))
                 
             else:
               print("Directory {} already exists!".format(param['dir']))
               param['dir']=renamedir(param['dir'])
               os.mkdir(param['dir'])
               print("Creating directory {}...".format(param['dir']))
               
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

def validateinput(file):
  if os.path.isfile(file):
    try:
      open(file,"r")
    except:
      print("{} (-i) couldn't be opened!".format(os.path.split(file)[-1]))
      quit()

def validateargs(param,id):
  if param['o'] is None:
    out=[id+'_UGENE.gbk',id+'_repeats.gbk']
  elif 'dir' in param.keys():
    out=[os.path.join(param['dir'],id+'_UGENE.gbk'),os.path.join(param['dir'],id+'_repeats.gbk')]
  else:
    if len(param['o'])==1:
      out=[id+'_UGENE.gbk',param['o']]
    else:
      out=param['o']
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
  param['o']=out2
  if 'defi' not in param.keys():
    print("Missing sequence definition (-defi)!")
    quit()
  elif not isinstance(param['defi'], str):
    print("Sequence definition (-defi) is not string!")
    quit()
  else:
    if '*' in param['defi']:
      param['defi']=param['defi'].replace('*',id)
    else:
      param['defi']=param['defi']

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
    if '*' in s:
      s=s.replace('*', id)
    valid.append(s)
    out=s.split('--out=')[1]
    out=out.split()[0]
    param['finds'].append(out)
  param['ugene']=valid

def convertEMBL(file,id):
  try:
    EMBL=open(file,"r")
  except:
    print("{} (-i) couldn't be opened, skipped!".format(os.path.split(file)[-1]))
    return False
  else:
    print("\nOpening {} (-i)...".format(os.path.split(file)[-1]))
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
          #print(param['o'])
          try:
            GenBank=open(param['o'][0],'w')
          except:
            print("GenBank feature table {} couldn't be written, skipped!".format(param['o'][0]))
            return False
          else:                      
            print("Writing GenBank converted file...")
            import datetime
            GenBank.write("LOCUS       {}             {} bp    DNA     linear {} {}\n".format(id,i,param['div'],datetime.datetime.now().strftime("%d-%b-%Y").upper()))
            GenBank.write("DEFINITION  {} {}\n".format(param['defi'],id))
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

def select_reps(finds,id):
  #print(finds)
  direct=dict()
  inverted=dict()
  for find in finds:
      file=open(find,"r")
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
        if '/rpt_type="inverted"' in repeat or '/ugene_name="TIR"' in repeat:
          if key not in inverted.keys():
            inverted[key]=repeat
        else:
          if key not in direct.keys():
            direct[key]=repeat
  print("Writing {} selected repeats table...".format(id))
  with open("{}_inverted_repeats_selected.gbk".format(id),'w') as ifile:
    lines=''.join(inverted.values()).split('\n')
    if '' in lines:
      lines.remove('')
    i=0
    for line in lines:
      if not line.lstrip()=='':
        if 'repeat_region   join' in line:
          words=line.split()
          if '' in words:
            words.remove('')
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
            line+=' '*21+'/color=255 204 204'
        ifile.write(line)
      i+=1
  with open("{}_direct_repeats_selected.gbk".format(id),'w') as dfile:
    lines=''.join(direct.values()).split('\n')
    if '' in lines:
      lines.remove('')
    i=0
    for line in lines:
      if not line.lstrip()=='':
        if 'repeat_region   join' in line:
          words=line.split()
          if '' in words:
            words.remove('')
          line=' '*5+words[0]+' '*3+words[1]+'\n'
          line+=' '*21+'/rpt_type=direct\n'
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
            line+=' '*21+'/color=204 239 255'
        dfile.write(line)
      i+=1

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
          print('Failed to delete %s. Reason: %s' % (file_path, e))

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
  if param['div'] is None:
    print("Missing GenBank division (-div)!")
    quit()
  else:
    validatediv(param['div'].strip())
  if param['i'] is None:
    print("Missing input file or dir (-i)!")
    quit()
  else:
    z=1
    param['i']=os.path.realpath(param['i'])
    if os.path.isdir(param['i']):
      if len(os.listdir(param['i'])) == 0:
        print("{} (-i) is empty!".format(param['i']))
        quit()
      else:
        param['i'] = [os.path.join(os.path.abspath(param['i']),f) for f in os.listdir(param['i']) if os.path.isfile(os.path.join(param['i'], f))]
        z=len(param['i'])
    a=0
    #print("param['i']={}".format(param['i']))
    while a<z:
      if z>1:
        input=param['i'][a]
      else:
        input=param['i']
      #print("input={}".format(input))
      validateinput(input)
      id=getid(input)
      if not id==False:
       validateargs(param,id)
       #print(param)
       if 'dir' in param.keys():
         os.chdir(param['dir'])
       converted=convertEMBL(input,id)
       if not converted==False:
         if 'sets' in param.keys():
           validatesets(param['sets'],id)
           ugene_time = datetime.now()
           for s in param['ugene']:
             #print(s)
             #print(os.getcwd())
             os.system(s)
           print("UGENE {} execution time:{}".format(id,datetime.now() - ugene_time))
           if os.path.isdir('tmp'):
             removedir('tmp')
             os.rmdir('tmp')
           elif 'tmp' in param.keys() and os.path.isdir(param['tmp']):
             removedir(param['tmp'])
             os.rmdir(param['tmp'])
           select_reps(param['finds'],id)
      if 'dir' in param.keys():
        param['o']=param['dir']
      else:
        param['o']=None
      a+=1
print("\nExecution time: {}".format(datetime.now() - start_time))