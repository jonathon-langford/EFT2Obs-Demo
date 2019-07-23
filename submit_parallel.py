import os, sys
from optparse import OptionParser

# Global variables
MG_DIR = "MG5_aMC_v2_6_5"

def get_options():
  parser = OptionParser()
  parser.add_option('--mode', dest='mode', default='generate', help='Running option: [generate,classification]')
  parser.add_option('--process', dest='process', default='ggh', help='Signal process')
  parser.add_option('--nJobs', dest='nJobs', default=1, type='int', help='Number of jobs')
  parser.add_option('--nEvents', dest='nEvents', default='10', help='Number of events per job')
  parser.add_option('--deleteMG5RunDir', dest='deleteMG5RunDir', default=1, type='int', help="Delete MG5 run directory after producing hepmc [yes=1,no=0]")
  parser.add_option('--queue', dest='queue', default='microcentury', help="HTCondor Queue" )
  return parser.parse_args()

(opt,args) = get_options()

# Only allowed for two modes: generate and classification
if opt.mode not in ['generate','classification']:
  print " --> [ERROR] mode (%s) not allowed. Please use one of [generate,classification]. Leaving..."%opt.mode
  sys.exit(1)

#Submission details
f_sub_name = "submit_%s_%s.sub"%(opt.mode,opt.process)
sub_handle = "%s_%s_run$(procID)"%(opt.mode,opt.process)
N_process = opt.nJobs

# Make job directories
if not os.path.isdir("./Jobs"): os.system("mkdir Jobs")
if not os.path.isdir("./Jobs/%s"%opt.process): os.system("mkdir ./Jobs/%s"%opt.process)
if not os.path.isdir("./Jobs/%s/err"%opt.process):
  os.system("mkdir ./Jobs/%s/err"%opt.process)
  os.system("mkdir ./Jobs/%s/log"%opt.process)
  os.system("mkdir ./Jobs/%s/out"%opt.process)

# Create condor submission file
print " --> Creating HTCondor submission file: %s"%f_sub_name
f_sub = open("%s"%f_sub_name,"w+")
f_sub.write("plusone = $(Process) + 1\n")
f_sub.write("procID = $INT(plusone,%d)\n\n")
f_sub.write("executable          = parallel.sh\n")
f_sub.write("arguments           = %s %s %s $(procID) %s %g\n"%(os.environ['PWD'],opt.mode,opt.process,opt.nEvents,opt.deleteMG5RunDir))
f_sub.write("output              = Jobs/%s/out/%s.out\n"%(opt.process,sub_handle))
f_sub.write("error               = Jobs/%s/err/%s.err\n"%(opt.process,sub_handle))
f_sub.write("log                 = Jobs/%s/log/%s.log\n"%(opt.process,sub_handle))
f_sub.write("+JobFlavour         = \"%s\"\n"%opt.queue)
f_sub.write("queue %s\n"%N_process)
f_sub.close()

# Submit
print " --> Submitting..."
os.system("condor_submit %s"%f_sub_name)
# Delete submission file
print " --> Delete submission file"
os.system("rm %s"%f_sub_name)
