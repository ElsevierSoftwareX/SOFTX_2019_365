# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 13:24:31 2019

@author: nicka
"""
import sys
import os
import json
from DiscreteLatticeMech import Solver, Writer

tests_location = os.path.dirname(os.path.abspath(__file__))


def test_carrereentrantex():

    filepath = tests_location + '/InputData_CarreReentrantEx.json'

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except IOError as error:
        print("could not open input file {}".format(filepath))
        sys.exit(1)

    solver = Solver()
    solver.solve(data)

    print("solver.CMatTensor=", solver.CMatTensor)
    print("solver.FlexMatTensor=", solver.FlexMatTensor)
    print("solver.Bulk=", solver.Bulk)
    print("solver.Ex=", solver.Ex)
    print("solver.Ey=", solver.Ey)
    print("solver.Poissonyx=", solver.Poissonyx)
    print("solver.Poissonxy=", solver.Poissonxy)
    print("solver.G=", solver.G)
    print("solver.rho=", solver.rho)

    CMatTensor_ref = [[0.242, -0.130, -0.000], [-0.130,  0.242,  0.000], [-0.000,  0.000,  0.064]]
    FlexMatTensor_ref = [[5.814, 3.126,  0.000], [3.126, 5.814,  0.000], [0.000, 0.000,  15.569]]
    Bulk_ref = 0.056
    Ex_ref = 0.172
    Ey_ref = 0.172
    Poissonyx_ref = -0.538
    Poissonxy_ref = -0.538
    G_ref = 0.032
    rho_ref = 0.333

    assert(rho_ref == round(solver.rho, 3))
    assert(Bulk_ref == round(solver.Bulk, 3))
    assert(Ex_ref == round(solver.Ex, 3))
    assert(Ey_ref == round(solver.Ey, 3))
    assert(Poissonyx_ref == round(solver.Poissonyx, 3))
    assert(Poissonxy_ref == round(solver.Poissonxy, 3))

    for i in range(3):
        for j in range(3):
            assert(CMatTensor_ref[i][j] == round(solver.CMatTensor[i][j], 3))

    for i in range(3):
        for j in range(3):
            assert(FlexMatTensor_ref[i][j] == round(solver.FlexMatTensor[i][j], 3))
