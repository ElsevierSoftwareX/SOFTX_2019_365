# DiscreteLatticeMech

#### Introduction

DiscreteLattichMech is a discrete element based mechanics Python package for the computation of the effective static properties of two-dimensional, metamaterial lattice structures. The software makes use of the asymptotic expansion form of the inner kinematic and static variables of the lattice structure, exploiting its spatial periodicity. As such, it makes use of the smallest repetitive material unit, substantially reducing the cost of full-scale computations. For the identification of the basic cell’s parameters, a dedicated Graphical User Interface (GUI) is provided. The code computes the complete, Cauchy mechanics, stiffness and compliance matrix, providing access to all elastic material moduli. In particular, the normal, shear and bulk moduli, as well as the Poisson’s ratio values of the architectured material structures are elaborated. Its formulation favors the analysis of a wide range of lattice designs, establishing a fundamental link between micro- and macro-scale material properties.

#### Project Layout

- `DiscreteLatticeMech/Core`: python library
- `DiscreteLatticeMech/GUI`: GUI tool
- `DiscreteLatticeMech/SampleInputs`: sample input configuration files
- `tests`: test that checks
- `examples`: set of python script examples
- `videos:`: a set of videos demonstrating the usage of the GUI tool

#### Requirement

Python 3.5 or higher is needed by both the core module and the GUI tool.

The package requirements for the core module are the following:
- `numpy`
- `jsonschema`
- `matplotlib`
- `pytest`

The additional package requirements for the GUI tool are the following:
- `wxpython`

Please note that the GUI tool has been tested on Windows platforms only.

#### Installation

Within your Python environment and the root folder of the package,
type the following command in your terminal to install it:

- `pip3 install .`

Otherwise, you can install the PyPi distribution:

- `pip3 install DiscreteLatticeMech`

The GUI tool is part of the package distribution. However, it's addition dependencies must be installed
by running the following command:

- `pip3 install wxpython`

#### Testing

Just type `pytest` to check the installation by automatically running the script in the `tests` folder.

#### Examples

To run the examples, just type `python3 examples/example1.py` and `python3 examples/example2.py`, from the root folder.

The first example reads the input configuration file (`InputData_SquareEx.json`), available in the `examples` folder and creates a new folder with the results of the run.

The second example sets the input data in a Python dictionary and calls the solver, generating another folder
with the same results.

The contents of `InputData_SquareEx.json` are shown below:
```
{
    "NumberElements": 2,
    "e_1": [1,0],
    "e_2": [0,1],
    "Y_1": [1, 0],
    "Y_2": [0, 1],
    "NumberNodes": 1,
    "Ob": [1,1],
    "Eb": [1,1],
    "Delta1": [1,0],
    "Delta2": [0,1],
    "Ka": [21,21],
    "Kb": [0.21,0.21],
    "Lb": [10,10],
    "tb": [1,1],
    "L1": 10,
    "L2": 10
}
```

where,
- `"NumberElements"`: number of elements
- `"e_1", "e_2"`: direction vectors of each element
- `"Y_1", "Y_2"`: define the global periodicity vectors
- `"NumberNodes"`: number of inner nodes
- `"Ob", "Eb", "Delta1", "Delta2"`: list of origin and end points along with delta
- `"Ka", "Kb"`: list of element axial and bending stiffness
- `"Lb", "tb"`: list of element lengths and volumes
- `"L1", "L2"`: norm of the periodicity vectors


A typical usage of the Python module, similarly to `example1.py`, is depicted below:

```
from DiscreteLatticeMech import Solver, Writer

if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Usage: {} <input filename (json)>".format(sys.argv[0]))
        sys.exit(1)
    else:
        filepath = sys.argv[1]

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except IOError as error:
        print("could not open input file {}".format(filepath))
        sys.exit(1)

    # create a DiscreteLatticeMech solver object
    solver = Solver()

    # initialize and call the solver and get the solution
    solver.solve(data)

    # create a write object
    writer = Writer()

    # write the results
    writer.WriteTensorsToFile(solver.InputData, solver.CMatTensor, solver.FlexMatTensor)
    writer.WriteEffectivePropertiesToFile(solver.Bulk, solver.Ex, solver.Ey, solver.Poissonyx, solver.Poissonxy, solver.G, solver.rho)

    # create some plots
    writer.PlotEffectiveProperties(solver.Bulk, solver.Ex, solver.Ey, solver.Poissonyx, solver.Poissonxy, solver.G)

```

The users can specify a configuration file as runtime argument to the `example1.py` script,
for instance `python3 examples/example1.py examples/InputData_SquareEx.json`
This command will automatically create a folder `Results_<data>_<time>`, where <date> and <time>
the current date and time on the system, with the following files:

- `InputData.json`: copy of the input configuration InputData
- `CMatrix.txt`, `FlexMatrix.txt`: computed matrices
- `EffectProperties.txt`: computed effective properties
- `NSB_Moduli.png`, `NormalToShear.png`, `PoissonRation.png`: plots of the computed effective properties

#### Using the GUI tool:
