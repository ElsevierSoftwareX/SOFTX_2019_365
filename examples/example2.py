# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 13:24:31 2019

@author: nicka
"""
from DiscreteLatticeMech import Solver, Writer


if __name__ == "__main__":

    data = {
        'Delta1': [1, 0],
        'Delta2': [0, 1],
        'Eb': [1, 1],
        'Ka': [21, 21],
        'Kb': [0.21, 0.21],
        'L1': 10,
        'L2': 10,
        'Lb': [10, 10],
        'NumberElements': 2,
        'NumberNodes': 1,
        'Ob': [1, 1],
        'Y_1': [1, 0],
        'Y_2': [0, 1],
        'e_1': [1, 0],
        'e_2': [0, 1],
        'tb': [1, 1]}

    solver = Solver()
    solver.solve(data)

    writer = Writer()
    writer.WriteTensorsToFile(solver.CMatTensor, solver.FlexMatTensor)
    writer.WriteEffectivePropertiesToFile(solver.Bulk, solver.Ex, solver.Ey, solver.Poissonyx, solver.Poissonxy, solver.G, solver.rho)
    writer.PlotEffectiveProperties(solver.Bulk, solver.Ex, solver.Ey, solver.Poissonyx, solver.Poissonxy, solver.G)
