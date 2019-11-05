# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 13:24:31 2019

@author: nicka
"""
from DiscreteLatticeMech import WriteEffectivePropertiesToFile, WriteTensorsToFile, PlotEffectiveProperties, Solver

if __name__ == "__main__":

    solver = Solver()

    # filepath = 'Inputs/InputData_CarreReentrant.txt'
    filepath = 'Inputs/InputData_CarreReentrant.json'

    solver.solve(filepath)

    # Write to file
    WriteTensorsToFile(solver.CMatTensor, solver.FlexMatTensor)
    WriteEffectivePropertiesToFile(solver.Bulk, solver.Ex, solver.Ey, solver.Poissonyx, solver.Poissonxy, solver.G)
    PlotEffectiveProperties(solver.Bulk, solver.Ex, solver.Ey, solver.Poissonyx, solver.Poissonxy, solver.G)
