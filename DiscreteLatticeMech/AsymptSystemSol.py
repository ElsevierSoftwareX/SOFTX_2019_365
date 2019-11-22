# -*- coding: utf-8 -*-
"""
Solution of the descrete system after expansion
"""
import sys
import numpy as np


def SystemSolution(NumberOfNodes, DirectionVectors, TransverseDirVectors, OriginBeams, EndBeams, NforceDef,
                   TforceDef, MomOrigDef, MomEndDef):

    # write the equilibrium equations
    ForceEq = [[0] * (2*NumberOfNodes+4+1*NumberOfNodes) for _ in range(2*NumberOfNodes)]
    MomentEq = [[0] * (2*NumberOfNodes+4+1*NumberOfNodes) for _ in range(NumberOfNodes)]

    for i in range(len(TransverseDirVectors)):
        NodeSt = OriginBeams[i]
        NodeEnd = EndBeams[i]
        for j in range(2*NumberOfNodes+4+1*NumberOfNodes):
            NforceDef_ij = NforceDef[i][j]
            TforceDef_ij = TforceDef[i][j]
            ForceEq[2*NodeSt-1-1][j] += -DirectionVectors[i][0]*NforceDef_ij - TransverseDirVectors[i][0]*TforceDef_ij
            ForceEq[2*NodeSt-1][j] += -DirectionVectors[i][1]*NforceDef_ij - TransverseDirVectors[i][1]*TforceDef_ij
            ForceEq[2*NodeEnd-1-1][j] += DirectionVectors[i][0]*NforceDef_ij + TransverseDirVectors[i][0]*TforceDef_ij
            ForceEq[2*NodeEnd-1][j] += DirectionVectors[i][1]*NforceDef_ij + TransverseDirVectors[i][1]*TforceDef_ij
            MomentEq[NodeEnd-1][j] = MomentEq[NodeEnd-1][j] + MomEndDef[i][j]
            MomentEq[NodeSt-1][j] = MomentEq[NodeSt-1][j] + MomOrigDef[i][j]

    # Join the equations and solve the system after reordering
    JoinedUnknownEquations = [[0]*(2*NumberOfNodes+NumberOfNodes) for _ in range(2*NumberOfNodes + NumberOfNodes)]
    JoinedKnownEquations = [[0]*4 for _ in range(2*NumberOfNodes + 1*NumberOfNodes)]

    # Unknowns: store first the force equation coefficients
    for i in range(2*NumberOfNodes):
        for j in range(2*NumberOfNodes+4+1*NumberOfNodes):
            if j < 2*NumberOfNodes or j > 2*NumberOfNodes+3:
                if j < 2*NumberOfNodes:
                    k = j
                else:
                    k = j-4
                JoinedUnknownEquations[i][k] = ForceEq[i][j]

    # put the moment equations in the unknowns
    for i in range(2*NumberOfNodes, 2*NumberOfNodes+NumberOfNodes):
        for j in range(2*NumberOfNodes+4+1*NumberOfNodes):
            if j < 2*NumberOfNodes or j > 2*NumberOfNodes+3:
                if j < 2*NumberOfNodes:
                    k = j
                else:
                    k = j-4
                JoinedUnknownEquations[i][k] = JoinedUnknownEquations[i][k]+MomentEq[i-2*NumberOfNodes][j]
    
    # Knowns: first the force equation coefficients
    for i in range(2*NumberOfNodes):
        for j in range(2*NumberOfNodes+4+1*NumberOfNodes):
            # TODO: optimize this
            if j >= 2*NumberOfNodes and j < 2*NumberOfNodes+4:
                k = j-2*NumberOfNodes
                JoinedKnownEquations[i][k] = -ForceEq[i][j]

    # put the moment equations in the unknowns
    for i in range(2*NumberOfNodes, 2*NumberOfNodes+NumberOfNodes):
        for j in range(2*NumberOfNodes+4+1*NumberOfNodes):
            # TODO: optimize this
            if j >= 2*NumberOfNodes and j < 2*NumberOfNodes+4:
                k = j-2*NumberOfNodes
                JoinedKnownEquations[i][k] = -MomentEq[i-2*NumberOfNodes][j]

    # fix the dx1 and dy1 displacements and unknowns
    for i in range(len(JoinedUnknownEquations)):
        JoinedUnknownEquations[0][i] = 0
        JoinedUnknownEquations[i][0] = 0
        JoinedUnknownEquations[1][i] = 0
        JoinedUnknownEquations[i][1] = 0

    JoinedUnknownEquations[0][0] = 1
    JoinedUnknownEquations[1][1] = 1

    for i in range(4):
        JoinedKnownEquations[0][i] = 0
        JoinedKnownEquations[1][i] = 0

    for i in range(len(JoinedUnknownEquations)):
        if abs(JoinedUnknownEquations[i][i]) < 1e-7:
            JoinedUnknownEquations[i][i] = 1

    # compute the solution of the system
    try:
        UnknownInv = np.linalg.inv(JoinedUnknownEquations)
    except np.linalg.LinAlgError as err:
        print("Fatal error: could not invert JoinedUnknownEquations. Error: {}".format(str(err)))
        sys.exit(1)

    SystemSol = UnknownInv.dot(JoinedKnownEquations)
    
    return SystemSol
