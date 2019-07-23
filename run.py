import os, sys
from optparse import OptionParser

# Global variables
MG_DIR = "MG5_aMC_v2_6_5"
rivetProcessDict = {"ggh":"GGF"}

def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~ EFT2OBS RUN (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~"
  sys.exit(1)

def get_options():
  parser = OptionParser()
  parser.add_option('--mode', dest='mode', default='setup', help='Running option: [setup,prepare,generate,classification]')
  parser.add_option('--process', dest='process', default='ggh', help='Signal process')
  parser.add_option('--runLabel', dest='runLabel', default='pilot', help='Run label')
  parser.add_option('--inputHepmc', dest='inputHepmc', default='', help='Input hepmc file path')
  return parser.parse_args()

(opt,args) = get_options()

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EFT2OBS RUN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

# Check if in allowed modes
if opt.mode not in ['setup','prepare','generate','classification']:
  print " --> [ERROR] mode (%s) not allowed. Please use one of [setup,prepare,generate,classification]. Leaving..."%opt.mode
  leave()
  
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP: to set up mg5 process

if opt.mode == 'setup':

  print " --> Using setup mode, process = %s"%opt.process
  
  # Check if process already exists as mg5 dir
  if os.path.isdir( "%s/%s"%(MG_DIR,opt.process) ):
    overwrite = input(" --> Configuration for process %s already exists in ./%s. Do you want to overwrite [yes=1,no=0]:"%(opt.process,MG_DIR))
    if overwrite:
      print " --> Writing over ./%s/%s"%(MG_DIR,opt.process)
    else:
      print " --> Please rename process %s in ./Cards directory to avoid overwriting. Leaving..."%opt.process
      leave() 

  # Check relevant process is in the Cards directory, with proc card
  if not os.path.isdir( "Cards/%s"%opt.process ):
    print " --> [ERROR] No information for process %s in ./Cards directory. Please add all cards here {proc,param,pythia8,reweight,run}_card.dat. Leaving..."%opt.process
    leave()
  if not os.path.exists( "Cards/%s/proc_card.dat"%opt.process ):
    print " --> [ERROR] No proc_card.dat for process %s. Leaving..."%opt.process
    leave()

  print " --> Setting up mg5 process: %s"%opt.process
  print " --> Using proc card: ./Cards/%s/proc_card.dat"%opt.process

  # Run setup of process
  os.system("pushd %s; ./bin/mg5_aMC ../Cards/%s/proc_card.dat; popd"%(MG_DIR,opt.process))

  print " --> Finished setup of %s"%opt.process

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PREPARE: copy cards across and make mg run script

elif opt.mode == 'prepare':

  print " --> Using prepare mode, process = %s"%opt.process

  #Check process has been setup
  print " --> Checking process %s has been setup..."%opt.process
  if not os.path.isdir("%s/%s"%(MG_DIR,opt.process)):
    print " --> [ERROR] Process %s does not exist. Please setup using --mode setup first. Leaving..."%opt.process
    leave()

  # Copy cards across: first check if they exist
  for card in ['param','pythia8','reweight','run']:
    missingCardFlag = False
    if not os.path.exists( "./Cards/%s/%s_card.dat"%(opt.process,card) ):
      print " [ERROR] %s_card.dat for process %s does not exist. Please add to ./Cards/%s"%(card,opt.process,opt.process)
      missingCardFlag = True
  if missingCardFlag: leave()

  #Copy cards across to relevant dir
  print " --> Copying ./Cards/%s/*_card.dat to %s/%s/Cards/"%(opt.process,MG_DIR,opt.process)
  os.system("cp Cards/%s/{param,pythia8,reweight,run}_card.dat %s/%s/Cards"%(opt.process,MG_DIR,opt.process))

  # Change pythia card for name of output hepmc
  os.system("sed -i \"s/= auto/= %s.hepmc/g\" %s/%s/Cards/pythia8_card.dat"%(opt.process,MG_DIR,opt.process))

  #Create MG config
  print " --> Creating MG run script..."
  os.system("pushd %s/%s; { echo \"shower=Pythia8\"; echo \"reweight=ON\"; echo \"done\"; } > mgrunscript; popd"%(MG_DIR,opt.process))

  print " --> Finished preparing process %s"%opt.process


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GENERATE: > generate events for specified process
#           > using options defined in {param,pythia8,reweight,run}_card.dat

elif opt.mode == 'generate':

  print " --> Using generate mode, process = %s"%opt.process

  # Check if run label already exists: if so then ask user if they want to overwrite
  if os.path.isdir("%s/%s/Events/%s"%(MG_DIR,opt.process,opt.runLabel)):
    overwrite = input(" --> Run label (%s) already exists in %s/%s/Events. Do you want to overwrite [1=yes,0=no]:"%(opt.runLabel,MG_DIR,opt.process))
    if not overwrite:
      print " --> Please use a different run label (--runLabel). Leaving..."
      leave()

  # Run command
  print " --> Generating events using run label: %s"%opt.runLabel
  os.system("pushd %s/%s; ./bin/generate_events %s < mgrunscript; popd"%(MG_DIR,opt.process,opt.runLabel))
  print " --> Successfully generated events."

  # Set up directory for process (if do not already exists)
  if not os.path.isdir("Events"): os.system("mkdir ./Events")
  if not os.path.isdir("./Events/%s"%opt.process): os.system("mkdir ./Events/%s"%opt.process)

  # Gunzip hepmc file and move to corresponding folder
  os.system("gunzip %s/%s/Events/%s/%s.hepmc.gz"%(MG_DIR,opt.process,opt.runLabel,opt.process))
  print " --> Moving output hepmc to ./Events/%s/hepmc/%s/%s.hepmc"%(opt.process,opt.runLabel,opt.process)
  if not os.path.isdir("./Events/%s/hepmc"%opt.process): os.system("mkdir ./Events/%s/hepmc"%opt.process)
  if not os.path.isdir("./Events/%s/hepmc/%s"%(opt.process,opt.runLabel)): os.system("mkdir ./Events/%s/hepmc/%s"%(opt.process,opt.runLabel))

  if os.path.exists("./Events/%s/hepmc/%s/%s.hepmc"%(opt.process,opt.runLabel,opt.process)):
    overwrite = input(" --> /Events/%s/hepmc/%s/%s.hepmc already exists. Do you want to overwrite [yes=1,no=0]:"%(opt.process,opt.runLabel,opt.process))
    if overwrite:
      os.system("mv %s/%s/Events/%s/%s.hepmc ./Events/%s/hepmc/%s/%s.hepmc"%(MG_DIR,opt.process,opt.runLabel,opt.process,opt.process,opt.runLabel,opt.process))
      print " --> Overwritten. Saved ./Events/%s/hepmc/%s/%s.hepmc"%(opt.process,opt.runLabel,opt.process)
    else: 
      rename = raw_input(" --> Please rename hepmc file:")
      os.system("mv %s/%s/Events/%s/%s.hepmc ./Events/%s/hepmc/%s/%s.hepmc"%(MG_DIR,opt.process,opt.runLabel,opt.process,opt.process,opt.runLabel,rename))
      print " --> Saved ./Events/%s/hepmc/%s/%s.hepmc"%(opt.process,opt.runLabel,rename) 
  else:
    os.system("mv %s/%s/Events/%s/%s.hepmc ./Events/%s/hepmc/%s/%s.hepmc"%(MG_DIR,opt.process,opt.runLabel,opt.process,opt.process,opt.runLabel,opt.process))
    print " --> Saved ./Events/%s/hepmc/%s/%s.hepmc"%(opt.process,opt.runLabel,opt.process)
  
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLASSIFICATION:

elif opt.mode == 'classification':

  print " --> Using classification mode, process = %s"%opt.process

  # Check if hepmc for process exists
  if opt.inputHepmc != '': 
    if not os.path.exists( opt.inputHepmc ):
      print " --> [ERROR] input hepmc file does not exist: %s. Leaving..."%opt.inputHepmc
      leave()
    else:
      f_hepmc = opt.inputHepmc
  else:
    f_hepmc = "./Events/%s/hepmc/%s/%s.hepmc"%(opt.process,opt.runLabel,opt.process)
    if not os.path.exists( f_hepmc ):
      print " --> [ERROR] input hepmc file does not exist: %s. Leaving..."%f_hepmc
      leave()

  print " --> Input hepmc file: %s"%f_hepmc
  
  # Make cmd line to run: set up environment
  cmdLine = "source local/rivetenv.sh; export RIVET_ANALYSIS_PATH=./Classification; export HIGGSPRODMODE=%s;"%rivetProcessDict[opt.process]
      
  # Make directories to store yoda and root files
  if not os.path.isdir("./Events/%s/yoda"%opt.process): os.system("mkdir ./Events/%s/yoda"%opt.process)
  if not os.path.isdir("./Events/%s/yoda/%s"%(opt.process,opt.runLabel)): os.system("mkdir ./Events/%s/yoda/%s"%(opt.process,opt.runLabel))
  if not os.path.isdir("./Events/%s/root"%opt.process): os.system("mkdir ./Events/%s/root"%opt.process)
  if not os.path.isdir("./Events/%s/root/%s"%(opt.process,opt.runLabel)): os.system("mkdir ./Events/%s/root/%s"%(opt.process,opt.runLabel))

  # Add running rivet to cmd line
  f_yoda = "./Events/%s/yoda/%s/%s.yoda"%(opt.process,opt.runLabel,opt.process)  
  if os.path.exists( f_yoda ):
    rename = raw_input("%s already exists. Rename file:"%f_yoda)
    f_yoda = "./Events/%s/yoda/%s/%s.yoda"%(opt.process,opt.runLabel,rename)
  f_root = f_yoda.replace("yoda","root")
    
  cmdLine += " rivet --analysis=HiggsTemplateCrossSections \"%s\" -o %s; yoda2root %s %s"%(f_hepmc,f_yoda,f_yoda,f_root)
      
  # Running command line
  os.system( cmdLine )

  print " --> Output yoda file: %s"%f_yoda
  print " --> Converting to root: %s"%f_root

print "~~~~~~~~~~~~~~~~~~~~~~~~~~ EFT2OBS RUN (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~"


