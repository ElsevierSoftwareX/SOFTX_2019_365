# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 14:50:01 2019

@author: nicka
"""


def EffectProps(FlexMatTensor):
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

    return [Bulk, Ex, Ey, Poissonyx, Poissonxy, G]
