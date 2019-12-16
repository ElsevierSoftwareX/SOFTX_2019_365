# -*- coding: utf-8 -*-
import os
import sys
import json

try:
    from DiscreteLatticeMech import Solver, Writer
except ImportError:
    file_location = os.path.dirname(os.path.abspath(__file__))
    package_location = file_location + '/../'
    sys.path.append(package_location)
    from DiscreteLatticeMech import Solver, Writer

if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Usage: {} <input filename (json)>".format(sys.argv[0]))
        filepath = file_location + '/InputData_SquareEx.json'
    else:
        filepath = sys.argv[1]

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except IOError as error:
        print("could not open input file {}".format(filepath))
        sys.exit(1)

    solver = Solver()
    solver.solve(data)

    writer = Writer()
    writer.WriteTensorsToFile(solver.InputData, solver.CMatTensor, solver.FlexMatTensor)
    writer.WriteEffectivePropertiesToFile(solver.Bulk, solver.Ex, solver.Ey, solver.Poissonyx, solver.Poissonxy, solver.G, solver.rho)
    writer.PlotEffectiveProperties(solver.Bulk, solver.Ex, solver.Ey, solver.Poissonyx, solver.Poissonxy, solver.G)
