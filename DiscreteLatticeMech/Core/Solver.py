from .ReadInput import ReadInpDataJSON
from .AsymptoticForcesMoments import GeomStrainParams, AsymptoticForm
from .AsymptSystemSol import SystemSolution
from .StressVector import StressVectorsComputation
from .StiffFlexibilTensors import StiffFlexTensors
from .EffectiveProperties import EffectProps


class Solver:

    def __init__(self):
        self.InputData=None
        self.CMatTensor = None
        self.FlexMatTensor = None
        self.Bulk = None
        self.Ex = None
        self.Ey = None
        self.Poissonyx = None
        self.Poissonxy = None
        self.G = None
        self.rho = None

    def solve(self, data):

        [DirectionVectors, PeriodicityVectors, NumberOfNodes, OriginBeams, EndBeams, DeltaPerVect1, DeltaPerVect2,
         AxialStiffness, BendingStiffness, ElemLengths, ElemThickn, L1, L2] = ReadInpDataJSON(data)

        [P1, P2, TransverseDirVectors, dU1, dU2] = GeomStrainParams(DirectionVectors, PeriodicityVectors, L1, L2)

        [NforceDef, TforceDef, MomEndDef, MomOrigDef] = AsymptoticForm(NumberOfNodes, DirectionVectors,
                                                                       TransverseDirVectors, OriginBeams, EndBeams,
                                                                       AxialStiffness, BendingStiffness, DeltaPerVect1,
                                                                       DeltaPerVect2, dU1, dU2, ElemLengths)

        # System computation
        SystemSol = SystemSolution(NumberOfNodes, DirectionVectors, TransverseDirVectors, OriginBeams, EndBeams,
                                   NforceDef, TforceDef, MomOrigDef, MomEndDef)

        # Stress vector computation
        [StressVector1, StressVector2] = StressVectorsComputation(NumberOfNodes, DirectionVectors,
                                                                  TransverseDirVectors, NforceDef, TforceDef,
                                                                  SystemSol, DeltaPerVect1, DeltaPerVect2)

        # Results of stiffness and flexibility matrix
        [self.CMatTensor, self.FlexMatTensor, Detg] = StiffFlexTensors(P1, P2, StressVector1, StressVector2)

        # Results of effective moduli and Poisson's ratio values
        [self.Bulk, self.Ex, self.Ey, self.Poissonyx, self.Poissonxy, self.G, self.rho] = \
            EffectProps(self.FlexMatTensor, ElemLengths, ElemThickn, Detg)
