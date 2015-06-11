from GaudiConf import IOHelper
from Configurables import DaVinci, DecayTreeTuple
from DecayTreeTuple.Configuration import *

# Stream and stripping line we want to use
stream = 'Dimuon'
line = 'FullDSTDiMuonPsi2MuMuDetachedLine'
rootInTES = '/Event/{0}'.format(stream)
tesLoc = '/Event/{0}/Phys/{1}/Particles'.format(stream,line)

# Build the decay tree by adding two pions to the psi(2s)
# 1) Get the psi(2s)
# get the selection(s) created by the stripping
from PhysSelPython.Wrappers import Selection
from PhysSelPython.Wrappers import SelectionSequence
from PhysSelPython.Wrappers import DataOnDemand
from StandardParticles import StdLooseMergedPi0, StdLooseResolvedPi0, StdLooseKaons, StdLoosePions

psi2sSel = DataOnDemand(Location=tesLoc)
#pionSel = DataOnDemand(Location = '/Event/Phys/StdAllNoPIDsPions/Particles')

# 2) Get pions
#from CommonParticles.StdAllNoPIDsPions import StdAllNoPIDsPions as Pions

B_daughters = {'pi+' :  '(PT > 250*MeV) & (P > 4000*MeV) & (MIPCHI2DV(PRIMARY) > 3) & (TRCHI2DOF < 5 ) & (TRGHP < 0.47)',
               'pi-' :  '(PT > 250*MeV) & (P > 4000*MeV) & (MIPCHI2DV(PRIMARY) > 3) & (TRCHI2DOF < 5 ) & (TRGHP < 0.47)',
               'J/psi(1S)' : 'ALL'}

# 3) Combine into  B
from Configurables import CombineParticles

combCut = "(AM<7000*MeV) & (AM>4750*MeV)"

combB = CombineParticles('Combine_B',
                         Inputs = [tesLoc,"Phys/StdLoosePions/Particles"],
                         DecayDescriptor = '[B0]CC -> J/psi(1S) pi+ pi-',
                         DaughtersCuts = B_daughters,
                         CombinationCut = combCut,
                         MotherCut = '(VFASPF(VCHI2PDOF) < 9) & (BPVDIRA>0.999) & (PT>500*MeV) & (BPVLTIME()>0.2*ps) & (BPVIPCHI2()<25) ')

Bsel = Selection('Sel_B',
                 Algorithm=combB,
                 RequiredSelections=[psi2sSel, StdLoosePions])

Bseq = SelectionSequence('Seq_B',TopSelection=Bsel)                  

# Create an ntuple to capture D*+ decays from the StrippingLine line
dtt = DecayTreeTuple('b2Psi2sPiPi')
dtt.Inputs = [Bseq.outputLocation()]
dtt.Decay = '[B0]CC -> ^(J/psi(1S) -> ^mu+ ^mu-) ^pi+ ^pi-'

dtt.addBranches({'B0' : '[B0]CC -> (J/psi(1S) -> mu+ mu-) pi+ pi-'})
dtt.B0.addTupleTool('TupleToolDecayTreeFitter/DTF')
dtt.B0.DTF.constrainToOriginVertex = True
dtt.B0.DTF.Verbose = True
bssubs = {
'B0 -> ^J/psi(1S) pi+ pi-':'J/psi(2S)',
'B~0 -> ^J/psi(1S) pi+ pi-':'J/psi(2S)',
}
dtt.B0.DTF.Substitutions = bssubs 
dtt.B0.DTF.daughtersToConstrain = [ "J/psi(2S)"]
# Configure DaVinci
seq = GaudiSequencer('MyTupleSeq')
seq.Members += [Bseq.sequence()]
seq.Members += [dtt]
DaVinci().appendToMainSequence([seq])

DaVinci().InputType = 'DST'
#DaVinci().RootInTES = rootInTES 
DaVinci().TupleFile = 'b2psi2spipi.root'
DaVinci().DDDBtag = 'dddb-20130111'
DaVinci().CondDBtag = 'cond-20130114'
DaVinci().PrintFreq = 1000
DaVinci().DataType = '2012'
DaVinci().Simulation = False
# Only ask for luminosity information when not using simulated data
DaVinci().Lumi = not DaVinci().Simulation
DaVinci().EvtMax = -1

# Use the local input data
#IOHelper().inputFiles([
#  './00035742_00000002_1.allstreams.dst'
#], clear=True)
