# -*- coding: utf-8 -*-
"""
Assembly of the stress vectors
"""


def StressVectorsComputation(NumberOfNodes, DirectionVectors, TransverseDirVectors, NforceDef, TforceDef,
                             SystemSol, DeltaPerVect1, DeltaPerVect2):

    # Collect the final normal, shear and moment expressions
    NormalForceF = [[0] * 4 for _ in range(len(TransverseDirVectors))]  # du1/dx du1/dy du2/dx du2/dy
    ShearForceF = [[0] * 5 for _ in range(len(TransverseDirVectors))]  # du1/dx du1/dy du2/dx du2/dy phi

    for i in range(len(TransverseDirVectors)):
        # store the normal and the shear force without the unknowns
        for j in range(2*NumberOfNodes, 2*NumberOfNodes+4):  # store for du1/dx, du1/dy, du2/dx, du2/dy
            NormalForceF[i][j-2*NumberOfNodes] = NforceDef[i][j]
            ShearForceF[i][j-2*NumberOfNodes] = TforceDef[i][j]
        for j in range(2, 2*NumberOfNodes+NumberOfNodes):
            for k in range(4):
                if j < 2*NumberOfNodes:
                    NormalForceF[i][k] = NormalForceF[i][k]+SystemSol[j][k]*NforceDef[i][j]
                    ShearForceF[i][k] = ShearForceF[i][k]+SystemSol[j][k]*TforceDef[i][j]
                else:
                    NormalForceF[i][k] = NormalForceF[i][k]+SystemSol[j][k]*NforceDef[i][j+4]
                    ShearForceF[i][k] = ShearForceF[i][k]+SystemSol[j][k]*TforceDef[i][j+4]

    # initialize the stress and moment vectors
    StressVector1 = [[0]*5 for _ in range(2)]
    StressVector2 = [[0]*5 for _ in range(2)]

    # add to the stress vector based on the normal and shear forces
    for i in range(len(TransverseDirVectors)):
        # add the normal and the shear for du1/dx du1/dy, du2/dx, du2/dy
        for j in range(4):
            DPV1_x_NFF = DeltaPerVect1[i] * NormalForceF[i][j]
            DPV2_x_NFF = DeltaPerVect2[i] * NormalForceF[i][j]
            DPV1_x_SFF = DeltaPerVect1[i] * ShearForceF[i][j]
            DPV2_x_SFF = DeltaPerVect2[i] * ShearForceF[i][j]
            StressVector1[0][j] += DirectionVectors[i][0]*DPV1_x_NFF + TransverseDirVectors[i][0]*DPV1_x_SFF
            StressVector1[1][j] += DirectionVectors[i][1]*DPV1_x_NFF + TransverseDirVectors[i][1]*DPV1_x_SFF
            StressVector2[0][j] += DirectionVectors[i][0]*DPV2_x_NFF + TransverseDirVectors[i][0]*DPV2_x_SFF
            StressVector2[1][j] += DirectionVectors[i][1]*DPV2_x_NFF + TransverseDirVectors[i][1]*DPV2_x_SFF
        # add the last part of the rotation
        for j in range(4, 5):
            StressVector1[0][j] += TransverseDirVectors[i][0]*DeltaPerVect1[i]*ShearForceF[i][j]
            StressVector1[1][j] += TransverseDirVectors[i][1]*DeltaPerVect1[i]*ShearForceF[i][j]
            StressVector2[0][j] += TransverseDirVectors[i][0]*DeltaPerVect2[i]*ShearForceF[i][j]
            StressVector2[1][j] += TransverseDirVectors[i][1]*DeltaPerVect2[i]*ShearForceF[i][j]

    return [StressVector1, StressVector2]
