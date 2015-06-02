from GaudiConf import IOHelper
from Configurables import DaVinci, DecayTreeTuple
from DecayTreeTuple.Configuration import *

# Stream and stripping line we want to use
stream = 'DiMuon'
line = 'FullDSTDiMuonPsi2MuMuDetachedLine'
tesLoc = '/Event/{0}/Phys/{1}/Particles'.format(stream, line)

# Build the decay tree by adding two pions to the psi(2s)
# 1) Get the psi(2s)
# get the selection(s) created by the stripping
from PhysSelPython.Wrappers import Selection
from PhysSelPython.Wrappers import SelectionSequence
from PhysSelPython.Wrappers import DataOnDemand

psi2sSels = [DataOnDemand(Location=tesLoc)] 

# 2) Get pions
from CommonParticles.StdAllNoPIDsPions import StdAllNoPIDsPions as Pions

B_daughters = {'pi+' :  '(PT > 750*MeV) & (P > 4000*MeV) & (MIPCHI2DV(PRIMARY) > 4) & (TRCHI2DOF < 5 )',
               'pi-' :  '(PT > 750*MeV) & (P > 4000*MeV) & (MIPCHI2DV(PRIMARY) > 4) & (TRCHI2DOF < 5 )',
               'psi(2s)' : 'ALL'}

# 3) Combine into  B
from Configurables import CombineParticles

combCut = "(ASUM(SUMTREE(PT,(ISBASIC | (ID=='gamma')),0.0))>5000*MeV) & (AM<7000*MeV) & (AM>4750*MeV)"

combB = CombineParticles('Combine_B',
                     Decay = '[B0 -> (psi(2s) -> mu+ mu-) pi+ pi-]CC',
                     DaughterCuts = B_daughters,
                     CombinationCut = combCut,
                     MotherCut = '(VFASPF(VCHI2PDOF) < 10) & (BPVDIRA>0.999)')

Bsel = Selection('Sel_B',
                 Algorithm=combB,
                 RequiredSelections=[psi2sSels[:],Pions])

Bseq = SelectionSequence('Seq_B',TopSelection=Bsel)                  

# Create an ntuple to capture D*+ decays from the StrippingLine line
dtt = DecayTreeTuple('b2Psi2sPiPi')
dtt.Inputs = [Bseq.outputLocation()]
dtt.Decay = '[B0 -> (psi(2s) -> mu+ mu-) pi+ pi-]CC'

# Configure DaVinci
seq = GaudiSequencer('MyTupleSeq')
seq.Members += [Bseq.sequence()]
seq.Members += [dtt]
DaVinci().appendToMainSequence([seq])

DaVinci().InputType = 'DST'
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
