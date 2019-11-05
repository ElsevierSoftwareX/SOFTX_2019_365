# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 13:24:31 2019

@author: nicka
"""
import json
from DiscreteLatticeMech import WriteEffectivePropertiesToFile, WriteTensorsToFile, PlotEffectiveProperties, Solver


if __name__ == "__main__":

    solver = Solver()

    #filepath = 'Inputs/InputData_CarreReentrant.json'
    #with open(filepath, 'r') as f:
    #    data = json.load(f)

    data = {
        "NumberElements": 10,
        "e_1": [1, 0],
        "e_2": [0.5, 0.866],
        "e_3": [-0.5, 0.866],
        "e_4": [0.866, -0.5],
        "e_5": [-0.866, -0.5],
        "e_6": [-0.5, -0.866],
        "e_7": [-0.5, 0.866],
        "e_8": [0.866, -0.5],
        "e_9": [0.866, 0.5],
        "e_10": [0, 1],
        "Y_1": [1, 0],
        "Y_2": [0, 1],
        "NumberNodes": 8,
        "Ob": [1, 3, 2, 8, 7, 7, 6, 4, 3, 5],
        "Eb": [2, 2, 8, 5, 5, 1, 1, 6, 4, 4],
        "Delta1": [0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
        "Delta2": [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
        "Ka": [21, 21, 21, 21, 21, 21, 21, 21, 21, 21],
        "Kb": [0.21, 0.21, 0.21, 0.21, 0.21, 0.21, 0.21, 0.21, 0.21, 0.21],
        "Lb": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
        "L1": 17.3205,
        "L2": 17.3205
    }

    print(json.dumps(data, indent=4, sort_keys=False))

    solver.solve(data)

    # Write to file
    WriteTensorsToFile(solver.CMatTensor, solver.FlexMatTensor)
    WriteEffectivePropertiesToFile(solver.Bulk, solver.Ex, solver.Ey, solver.Poissonyx, solver.Poissonxy, solver.G)
    PlotEffectiveProperties(solver.Bulk, solver.Ex, solver.Ey, solver.Poissonyx, solver.Poissonxy, solver.G)
