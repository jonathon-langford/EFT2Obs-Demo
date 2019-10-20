import os, sys
from optparse import OptionParser

# Global variables
MG_DIR = "MG5_aMC_v2_6_6"
rivetProcessDict = {"ggh":"GGF", "vbf":"VBF", "wh":"WH", "zh":"QQ2ZH", "ggzh":"GG2ZH", "tth":"TTH"}

def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~ EFT2OBS RUN (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~"
  sys.exit(1)

def get_options():
  parser = OptionParser()
  parser.add_option('--process', dest='process', default='ggh', help='Signal process')
  parser.add_option('--runLabel', dest='runLabel', default='pilot', help='Run label')
  parser.add_option('--nEvents', dest='nEvents', default='', help='Number of events per run')
  parser.add_option('--disableReweight', dest='disableReweight', default=0, type='int', help='Disable reweight option')
  parser.add_option('--classificationOnly', dest='classificationOnly', default=0, type='int', help='Only run classification stage (Rivet)')
  parser.add_option('--saveMG5RunDir', dest='saveMG5RunDir', default=0, type='int', help="Save MG5 run directory [yes=1,no=0]")
  parser.add_option('--saveHepMC', dest='saveHepMC', default=0, type='int', help="Save HepMC output [yes=1,no=0]")
  return parser.parse_args()
(opt,args) = get_options()

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EFT2OBS RUN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

if not opt.classificationOnly:
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # SETUP: set up mg5 process

  print " --> Process = %s, runLabel = %s"%(opt.process,opt.runLabel)
  # Make run directory in MG dir
  if not os.path.isdir( "%s/run"%MG_DIR ): 
    os.system("mkdir %s/run"%MG_DIR )
    print " --> Making %s/run directory for running process"%MG_DIR
  
  # Check if process already exists in run dir: if so then delete
  if os.path.isdir( "%s/run/%s_%s"%(MG_DIR,opt.process,opt.runLabel) ):
    print " --> Configuration for process %s already exists for chosen run label: ./%s/run/%s_%s. Will delete current run directory."%(opt.process,MG_DIR,opt.process,opt.runLabel)
    os.system("rm -Rf ./%s/run/%s_%s"%(MG_DIR,opt.process,opt.runLabel))

  # Check relevant process is in the Cards directory, with proc card
  if not os.path.isdir( "Cards/%s"%opt.process ):
    print " --> [ERROR] No information for process %s in ./Cards directory. Please add all cards here {proc,param,pythia8,reweight,run}_card.dat. Leaving..."%opt.process
    leave()
  if not os.path.exists( "Cards/%s/proc_card.dat"%opt.process ):
    print " --> [ERROR] No proc_card.dat for process %s. Leaving..."%opt.process
    leave()

  #Copy proc_card into run directory and change name of output to include run label
  os.system("cp ./Cards/%s/proc_card.dat ./%s/run/proc_card_%s_%s.dat"%(opt.process,MG_DIR,opt.process,opt.runLabel))
  os.system("sed -i \"s/.*output.*/output %s_%s -nojpeg/g\" %s/run/proc_card_%s_%s.dat"%(opt.process,opt.runLabel,MG_DIR,opt.process,opt.runLabel))
  print " --> Setting up mg5 process: %s_%s"%(opt.process,opt.runLabel)
  print " --> Using proc card: ./Cards/%s/proc_card.dat"%opt.process

  # Run setup of process
  os.system("pushd %s/run; ../bin/mg5_aMC proc_card_%s_%s.dat; popd"%(MG_DIR,opt.process,opt.runLabel))
  print " --> Finished setup of %s_%s"%(opt.process,opt.runLabel)

  # Delete tmp proc card in run folder
  os.system("rm ./%s/run/proc_card_%s_%s.dat"%(MG_DIR,opt.process,opt.runLabel))

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # PREPARE: copy cards across and make mg run script

  print " --> Preparing %s_%s"%(opt.process,opt.runLabel)

  # Copy cards across: first check if they exist
  if opt.disableReweight: cardNames = ['param','pythia8','run']
  else: cardNames = ['param','pythia8','reweight','run']
  for card in cardNames:
    missingCardFlag = False
    if not os.path.exists( "./Cards/%s/%s_card.dat"%(opt.process,card) ):
      print " [ERROR] %s_card.dat for process %s does not exist. Please add to ./Cards/%s"%(card,opt.process,opt.process)
      missingCardFlag = True
  if missingCardFlag: leave()

  #Copy cards across to relevant dir
  if opt.disableReweight: 
    print " --> Copying ./Cards/%s/{param,pythia8,run}_card.dat to %s/run/%s_%s/Cards/"%(opt.process,MG_DIR,opt.process,opt.runLabel)
    os.system("cp Cards/%s/{param,pythia8,run}_card.dat %s/run/%s_%s/Cards"%(opt.process,MG_DIR,opt.process,opt.runLabel))
  else:
    print " --> Copying ./Cards/%s/{param,pythia8,reweight,run}_card.dat to %s/run/%s_%s/Cards/"%(opt.process,MG_DIR,opt.process,opt.runLabel)
    os.system("cp Cards/%s/{param,pythia8,reweight,run}_card.dat %s/run/%s_%s/Cards"%(opt.process,MG_DIR,opt.process,opt.runLabel))

  # Change pythia card for name of output hepmc
  os.system("sed -i \"s/HEPMCoutput:file.*/HEPMCoutput:file         = %s_%s.hepmc/g\" %s/run/%s_%s/Cards/pythia8_card.dat"%(opt.process,opt.runLabel,MG_DIR,opt.process,opt.runLabel))

  # Change run card if specify number of events
  if opt.nEvents != '':
    print " --> Adapting run_card.dat for %s_%s: N_events = %s"%(opt.process,opt.runLabel,opt.nEvents)
    os.system("sed -i \"s/.*Number of unweighted events requested.*/  %s = nevents ! Number of unweighted events requested/g\" %s/run/%s_%s/Cards/run_card.dat"%(opt.nEvents,MG_DIR,opt.process,opt.runLabel))

  #Create MG config
  print " --> Creating MG run script..."
  if opt.disableReweight: os.system("pushd %s/run/%s_%s; { echo \"shower=Pythia8\"; echo \"done\"; } > mgrunscript; popd"%(MG_DIR,opt.process,opt.runLabel))
  else: os.system("pushd %s/run/%s_%s; { echo \"shower=Pythia8\"; echo \"reweight=ON\"; echo \"done\"; } > mgrunscript; popd"%(MG_DIR,opt.process,opt.runLabel))

  print " --> Finished preparing %s_%s"%(opt.process,opt.runLabel)
   
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # GENERATE: > generate events for specified process

  print " --> Generating events for %s_%s"%(opt.process,opt.runLabel)

  # Run command
  os.system("pushd %s/run/%s_%s; ./bin/generate_events %s < mgrunscript; popd"%(MG_DIR,opt.process,opt.runLabel,opt.runLabel))
  print " --> Successfully generated events."

  # Check hepmc exists:
  if not os.path.exists("%s/run/%s_%s/Events/%s/%s_%s.hepmc"%(MG_DIR,opt.process,opt.runLabel,opt.runLabel,opt.process,opt.runLabel)):
    print " --> [ERROR] HepMC file production has not been successful. Check log. Leaving..."
    leave()

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # MOVE: hepmc output to directory
  # Set up directory for process (if do not already exists)
  if not os.path.isdir("Events"): os.system("mkdir ./Events")
  if not os.path.isdir("./Events/%s"%opt.process): os.system("mkdir ./Events/%s"%opt.process)

  # Move hepmc to output directory
  print " --> Moving output hepmc to ./Events/%s/hepmc/"%(opt.process)
  if not os.path.isdir("./Events/%s/hepmc"%opt.process): os.system("mkdir ./Events/%s/hepmc"%opt.process)

  # If file already exists, then add suffix
  if os.path.exists("./Events/%s/hepmc/%s_%s.hepmc"%(opt.process,opt.process,opt.runLabel)):
    saved = False
    suffix = 1
    while not saved:
      if not os.path.exists("./Events/%s/hepmc/%s_%s_%g.hepmc"%(opt.process,opt.process,opt.runLabel,suffix)):
        os.system("mv %s/run/%s_%s/Events/%s/%s_%s.hepmc ./Events/%s/hepmc/%s_%s_%g.hepmc"%(MG_DIR,opt.process,opt.runLabel,opt.runLabel,opt.process,opt.runLabel,opt.process,opt.process,opt.runLabel,suffix))
        print " --> Saved: ./Events/%s/hepmc/%s_%s_%g.hepmc"%(opt.process,opt.process,opt.runLabel,suffix)
        saved = True
      else:
        suffix += 1
  #Else: save as normal
  else:
    os.system("mv %s/run/%s_%s/Events/%s/%s_%s.hepmc ./Events/%s/hepmc/%s_%s.hepmc"%(MG_DIR,opt.process,opt.runLabel,opt.runLabel,opt.process,opt.runLabel,opt.process,opt.process,opt.runLabel))
    print " --> Saved: ./Events/%s/hepmc/%s_%s.hepmc"%(opt.process,opt.process,opt.runLabel)

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # DELETE MGDIR
  if not opt.saveMG5RunDir:
    print " --> Deleting %s/run/%s_%s ..."%(MG_DIR,opt.process,opt.runLabel)  
    os.system("rm -Rf %s/run/%s_%s"%(MG_DIR,opt.process,opt.runLabel))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLASSIFICATION:

print " --> Classification for process = %s, run label = %s"%(opt.process,opt.runLabel)

# Check if hepmc for process exists
f_hepmc = "./Events/%s/hepmc/%s_%s.hepmc"%(opt.process,opt.process,opt.runLabel)
if not os.path.exists( f_hepmc ):
  print " --> [ERROR] HepMC file (%s) does not exist. Check log. Leaving..."%f_hepmc
  leave()

print " --> Input hepmc file: %s"%f_hepmc
  
# Make cmd line to run: set up environment
cmdLine = "source local/rivetenv.sh; export RIVET_ANALYSIS_PATH=./Classification; export HIGGSPRODMODE=%s;"%rivetProcessDict[opt.process.split("_")[0]]
      
# Make directories to store yoda file
if not os.path.isdir("./Events/%s/yoda"%opt.process): os.system("mkdir ./Events/%s/yoda"%opt.process)

# Add running rivet to cmd line
f_yoda = "./Events/%s/yoda/%s_%s.yoda"%(opt.process,opt.process,opt.runLabel)  
cmdLine += " rivet --analysis=HiggsTemplateCrossSections \"%s\" -o %s"%(f_hepmc,f_yoda)
      
# Running command line
os.system( cmdLine )

print " --> Output yoda file: %s"%f_yoda

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DELETE HEPMC FILE
if not opt.saveHepMC:
  print " --> Deleting HepMC file: %s"%f_hepmc
  os.system("rm %s"%f_hepmc)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# END OF PROGRAM
leave()



