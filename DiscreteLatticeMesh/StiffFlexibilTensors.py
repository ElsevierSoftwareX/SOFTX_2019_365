# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 14:26:35 2019

@author: nicka
"""
import math
import numpy as np 


def StiffFlexTensors(P1, P2, StressVector1, StressVector2):
    # compute the determinant of the transformation matrix
    g = [[0]*2 for _ in range(2)]
    g[0][0] = P1[0]
    g[0][1] = P2[0]
    g[1][0] = P1[1]
    g[1][1] = P2[1]
    Detg = round(np.linalg.det(g), 8)
    
    # Compute the derivatives of the position vectors
    dR1 = [0]*2
    dR2 = [0]*2
    dR1[0] = P1[0]
    dR1[1] = P1[1]
    dR2[0] = P2[0]
    dR2[1] = P2[1]
    
    # compute the stiffness matrix and the moment matrix
    sigma = [[0]*(2*5) for _ in range(2)]
    for i in range(2):  # runs over columns
        for j in range(2):  # runs over rows
            for k in range(5):  # runs over the entries of the stress vector
                sigma[j][i*5+k] = sigma[j][i*5+k]+(1/Detg)*StressVector1[j][k]*dR1[i]
                sigma[j][i*5+k] = sigma[j][i*5+k]+(1/Detg)*StressVector2[j][k]*dR2[i]
              
    # computation of the rigidity matrix 
    Cmat = [[0]*4 for _ in range(4)]
    # loop over the sigma matrix to extract the coefficients (Order: dU1/dx, dU1/dy, dU2/dx, dU2/dy)
    for i in range(4):
        Cmat[0][i] = sigma[0][i]
        Cmat[1][i] = sigma[1][5+i]
        Cmat[2][i] = sigma[0][5+i]
        Cmat[3][i] = sigma[1][i]

    # reorder so that dU1/dx, dU2/dy, dU1/dy, dU2/dx
    dU2dy = [0]*4
    dU1dy = [0]*4
    dU2dx = [0]*4
    for i in range(4):
        dU2dy[i] = Cmat[i][3]
        dU1dy[i] = Cmat[i][1]
        dU2dx[i] = Cmat[i][2]
        Cmat[i][1] = dU2dy[i]
        Cmat[i][2] = dU1dy[i]
        Cmat[i][3] = dU2dx[i]

    # Transform to Voigt notation
    CmatV = [[0]*3 for _ in range(3)]
    CmatV[0][0] = Cmat[0][0]
    CmatV[0][1] = Cmat[0][1]
    CmatV[1][0] = Cmat[1][0]
    CmatV[1][1] = Cmat[1][1]
    CmatV[0][2] = Cmat[0][2]+Cmat[0][3]
    CmatV[1][2] = Cmat[1][2]+Cmat[1][3]
    CmatV[2][2] = Cmat[2][2]+Cmat[2][3]
    CmatV[2][0] = CmatV[0][2]
    CmatV[2][1] = CmatV[1][2]
    
    # Transform to tensor notation
    CMatTensor = [[0.0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            CMatTensor[i][j] = CmatV[i][j]
    CMatTensor[0][2] = math.sqrt(2)*CMatTensor[0][2]
    CMatTensor[1][2] = math.sqrt(2)*CMatTensor[1][2]
    CMatTensor[2][2] = CMatTensor[2][2]  # check for the transformation
    CMatTensor[2][0] = CMatTensor[0][2]
    CMatTensor[2][1] = CMatTensor[1][2]

    # compute compliance matrix
    FlexMatTensor = np.linalg.inv(CMatTensor)
    
    return [CMatTensor, FlexMatTensor]
