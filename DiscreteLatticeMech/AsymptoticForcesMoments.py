# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 12:37:16 2019

@author: nicka
"""


def GeomStrainParams(DirectionVectors, PeriodicityVectors, L1, L2):

    P1 = []
    P2 = []
    TransverseDirVectors = [[0] * 2 for _ in range(len(DirectionVectors))]

    P1.append(L1*PeriodicityVectors[0][0])
    P1.append(L1*PeriodicityVectors[0][1])
    P2.append(L2*PeriodicityVectors[1][0])
    P2.append(L2*PeriodicityVectors[1][1])
    for i in range(len(DirectionVectors)):
        TransverseDirVectors[i][0] = -DirectionVectors[i][1]
        TransverseDirVectors[i][1] = DirectionVectors[i][0]

    # Create the dU1 and dU2 coefficient matrices
    dU1 = [0]*4
    dU2 = [0]*4  # each multiplies dU1/dx, dU1/dy, dU2/dx, DuU2/Dy
    dU1[0] = P1[0]
    dU1[1] = P1[1]
    dU1[2] = P1[0]
    dU1[3] = P1[1]
    dU2[0] = P2[0]
    dU2[1] = P2[1]
    dU2[2] = P2[0]
    dU2[3] = P2[1]

    # return the parameters
    return [P1, P2, TransverseDirVectors, dU1, dU2]


def AsymptoticForm(NumberOfNodes, DirectionVectors, TransverseDirVectors, OriginBeams, EndBeams, AxialStiffness,
                   BendingStiffness, DeltaPerVect1, DeltaPerVect2, dU1, dU2, ElemLengths):

    # initialize the matrix for the normal forces
    NforceDef = [[0] * (2*NumberOfNodes+4+1*NumberOfNodes) for _ in range(len(DirectionVectors))]
    for i in range(len(DirectionVectors)):
        Dend = [0] * (2*NumberOfNodes)
        Dend[2*(EndBeams[i]-1)] = Dend[2*(EndBeams[i]-1)] + DirectionVectors[i][0]
        Dend[2*(EndBeams[i]-1)+1] = Dend[2*(EndBeams[i]-1)+1] + DirectionVectors[i][1]
        Dend[2*(OriginBeams[i]-1)] = Dend[2*(OriginBeams[i]-1)] - DirectionVectors[i][0]
        Dend[2*(OriginBeams[i]-1)+1] = Dend[2*(OriginBeams[i]-1)+1] - DirectionVectors[i][1]
        for j in range(2*NumberOfNodes):
            NforceDef[i][j] = AxialStiffness[i]*Dend[j]
        for j in range(2*NumberOfNodes, 2*NumberOfNodes+4):
            if j < (2*NumberOfNodes+2):
                NforceDef[i][j] += AxialStiffness[i]*DirectionVectors[i][0]\
                                * (DeltaPerVect1[i]*dU1[j-2*NumberOfNodes]+DeltaPerVect2[i]*dU2[j-2*NumberOfNodes])
            else:
                NforceDef[i][j] += AxialStiffness[i]*DirectionVectors[i][1]\
                                * (DeltaPerVect1[i]*dU1[j-2*NumberOfNodes]+DeltaPerVect2[i]*dU2[j-2*NumberOfNodes])

    # initialize the matrix for the shear forces and moments
    TforceDef = [[0] * (2*NumberOfNodes+4+1*NumberOfNodes) for _ in range(len(DirectionVectors))]
    MomEndDef = [[0] * (2*NumberOfNodes+4+1*NumberOfNodes) for _ in range(len(DirectionVectors))]
    MomOrigDef = [[0] * (2*NumberOfNodes+4+1*NumberOfNodes) for _ in range(len(DirectionVectors))]

    for i in range(len(TransverseDirVectors)):
        Dend = [0] * (2*NumberOfNodes)
        Dend[2*(EndBeams[i]-1)] = Dend[2*(EndBeams[i]-1)]+TransverseDirVectors[i][0]
        Dend[2*(EndBeams[i]-1)+1] = Dend[2*(EndBeams[i]-1)+1]+TransverseDirVectors[i][1]
        Dend[2*(OriginBeams[i]-1)] = Dend[2*(OriginBeams[i]-1)]-TransverseDirVectors[i][0]
        Dend[2*(OriginBeams[i]-1)+1] = Dend[2*(OriginBeams[i]-1)+1]-TransverseDirVectors[i][1]
        for j in range(2*NumberOfNodes):
            TforceDef[i][j] = BendingStiffness[i]*Dend[j]
        for j in range(2*NumberOfNodes, 2*NumberOfNodes+4):
            if j < (2*NumberOfNodes+2):
                TforceDef[i][j] += BendingStiffness[i] * TransverseDirVectors[i][0] * \
                                   (DeltaPerVect1[i]*dU1[j-2*NumberOfNodes] + DeltaPerVect2[i]*dU2[j-2*NumberOfNodes])
            else:
                TforceDef[i][j] += BendingStiffness[i] * TransverseDirVectors[i][1] * \
                                   (DeltaPerVect1[i]*dU1[j-2*NumberOfNodes] + DeltaPerVect2[i]*dU2[j-2*NumberOfNodes])

        # Store the depl part for the moments
        for k in range(2*NumberOfNodes+4+1*NumberOfNodes):
            # store the corresponding moment development neglecting rotations
            MomEndDef[i][k] = MomEndDef[i][k]-(3*ElemLengths[i]/6)*TforceDef[i][k]
            MomOrigDef[i][k] = MomOrigDef[i][k]-(3*ElemLengths[i]/6)*TforceDef[i][k]

        # Add the nodal rotations to the shear forces
        phiN = [0] * NumberOfNodes  # One rotation per node
        phiN[EndBeams[i]-1] = phiN[EndBeams[i]-1] + 1
        phiN[OriginBeams[i]-1] = phiN[OriginBeams[i]-1] + 1
        TforceDef[i][2*NumberOfNodes+4-1+EndBeams[i]] -= BendingStiffness[i]*(ElemLengths[i]/2)*1
        TforceDef[i][2*NumberOfNodes+4-1+OriginBeams[i]] -= BendingStiffness[i]*(ElemLengths[i]/2)*1

        # Add the nodal rotations to the moments
        MomEndDef[i][2*NumberOfNodes+4-1+EndBeams[i]] += BendingStiffness[i]*(ElemLengths[i]/6)*ElemLengths[i]*2*1
        MomEndDef[i][2*NumberOfNodes+4-1+OriginBeams[i]] += BendingStiffness[i]*(ElemLengths[i]/6)*ElemLengths[i]*1
        MomOrigDef[i][2*NumberOfNodes+4-1+EndBeams[i]] += BendingStiffness[i]*(ElemLengths[i]/6)*ElemLengths[i]*1*1
        MomOrigDef[i][2*NumberOfNodes+4-1+OriginBeams[i]] += BendingStiffness[i]*(ElemLengths[i]/6)*ElemLengths[i]*2*1

    return [NforceDef, TforceDef, MomEndDef, MomOrigDef]
