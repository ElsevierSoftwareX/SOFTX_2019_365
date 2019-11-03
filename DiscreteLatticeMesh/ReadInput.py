# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 16:37:36 2019

@author: nicka
"""
import json
import jsonschema
from jsonschema import validate

def ReadInpDataJSON(FileName):

    # Create the schema, as a nested Python dict,
    # specifying the data elements, their names and their types.
    schema = {
        "type": "object",
        "properties": {
            "NumberElements": {"type": "number"},
            "NumberNodes": {"type": "number"},
            "Y_1": {"type": "array", "minItems": 2, "maxItems": 2, "items": [{"type": "number"}]},
            "Y_2": {"type": "array", "minItems": 2, "maxItems": 2, "items": [{"type": "number"}]},
            "Ob": {"type": "array", "minItems": None, "maxItems": None, "items": [{"type": "number"}]},
            "Eb": {"type": "array", "minItems": None, "maxItems": None, "items": [{"type": "number"}]},
            "Delta1": {"type": "array", "minItems": None, "maxItems": None, "items": [{"type": "number"}]},
            "Delta2": {"type": "array", "minItems": None, "maxItems": None, "items": [{"type": "number"}]},
            "Ka": {"type": "array", "minItems": None, "maxItems": None, "items": [{"type": "number"}]},
            "Kb": {"type": "array", "minItems": None, "maxItems": None, "items": [{"type": "number"}]},
            "Lb": {"type": "array", "minItems": None, "maxItems": None, "items": [{"type": "number"}]},
            "L1": {"type": "number"},
            "L2": {"type": "number"}
        }
    }

    with open(FileName, 'r') as f:
        data = json.load(f)

    print(json.dumps(data, indent=4, sort_keys=False))

    NumElements = data["NumberElements"]

    for i in range(1, NumElements+1):
        key = 'e_' + str(i)
        d = {key : {"type": "array", "minItems" : 2, "maxItems": 2, "items": [{ "type" : "number"}]}}
        schema.update(d)

    for key in ["Ob", "Eb", "Delta1", "Delta2", "Ka", "Kb", "Lb"]:
        schema["properties"][key]["minItems"] = NumElements
        schema["properties"][key]["maxItems"] = NumElements

    print(schema)

    print(json.dumps(schema, indent=4, sort_keys=True))

    validate(data, schema)

    DirectionVectors = []
    PeriodicityVectors = [[0.0] * 2 for _ in range(2)]
    OriginBeams = []
    EndBeams = []
    DeltaPerVect1 = []
    DeltaPerVect2 = []
    AxialStiffness = []
    BendingStiffness = []
    ElemLengths = []

    for i in range(1, NumElements+1):
        key = 'e_' + str(i)
        DirectVector = data[key]
        DirectionVectors.append([0.0] * 2)
        DirectionVectors[i-1][0] = DirectVector[0]
        DirectionVectors[i-1][1] = DirectVector[1]
        print(DirectVector)

    PeriodVect = data["Y_1"]
    PeriodicityVectors[0][0] = PeriodVect[0]
    PeriodicityVectors[0][1] = PeriodVect[1]
    PeriodVect = data["Y_2"]
    PeriodicityVectors[1][0] = PeriodVect[0]
    PeriodicityVectors[1][1] = PeriodVect[1]

    # Store the number of nodes
    NumberOfNodes = data["NumberNodes"]

    # Store the origin beams
    OrigBeam = data["Ob"]
    for i in range(NumElements):
        OriginBeams.append(int(OrigBeam[i]))

    # Store the end beams
    EndBeam = data["Eb"]
    for i in range(NumElements):
        EndBeams.append(int(EndBeam[i]))

    # Store the end beams
    Delta = data["Delta1"]
    for i in range(NumElements):
        DeltaPerVect1.append(int(Delta[i]))

    Delta = data["Delta2"]
    for i in range(NumElements):
        DeltaPerVect2.append(int(Delta[i]))

    Stiff = data["Ka"]
    for i in range(NumElements):
        AxialStiffness.append(float(Stiff[i]))

    Stiff = data["Kb"]
    for i in range(NumElements):
        BendingStiffness.append(float(Stiff[i]))

    Length = data["Lb"]
    for i in range(NumElements):
        ElemLengths.append(float(Length[i]))

    L1 = data["L1"]
    L2 = data["L2"]

    return [DirectionVectors, PeriodicityVectors, NumberOfNodes, OriginBeams, EndBeams, DeltaPerVect1, DeltaPerVect2,
            AxialStiffness, BendingStiffness, ElemLengths, L1, L2]
