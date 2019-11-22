# -*- coding: utf-8 -*-
"""
Effetive property computation
"""


def EffectProps(FlexMatTensor,ElemLengths,ElemThickn,Detg):
    # compute different mechanical parameters
    Bulk = 1/(FlexMatTensor[0][0]+FlexMatTensor[1][1]+FlexMatTensor[0][1]+FlexMatTensor[1][0])

    # Normal moduli
    Ex = 1/FlexMatTensor[0][0]
    Ey = 1/FlexMatTensor[1][1]

    # Poissons ratio values
    Poissonyx = -FlexMatTensor[0][1]*Ey
    Poissonxy = -FlexMatTensor[1][0]*Ex

    # Shear modulus
    G = 1/(2*FlexMatTensor[2][2])
    
    # Relative density
    rho=0;
    for i in range(len(ElemThickn)):
        rho=rho+ElemLengths[i]*ElemThickn[i];
    rho=rho/Detg;
    
    return [Bulk, Ex, Ey, Poissonyx, Poissonxy, G,rho]
