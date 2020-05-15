""""This module reads, manipulates, and batch renders .sbs files within Substance Designer.
"""
import os
import random
import subprocess
import tensorflow as tf
from pysbs import context, params, substance, sbsenum, qtclasses
# Substance Automation Toolkit as a dependency

def get_sbsDoc(sbs_path,material):
    # Create path to .sbs file
    sbs_file = material + ".sbs"
    aSBSFileAbsPath = os.path.join(sbs_path,sbs_file)
    # Creation of a SBSDocument object from an existing .sbs file, parsing and writing
    aContext = context.Context()
    sbsDoc = substance.SBSDocument(aContext, aSBSFileAbsPath)
    sbsDoc.parseDoc()
    sbsDoc.writeDoc()
    return sbsDoc

def get_paramDict(image_number, material_id, engine, outputsize, sbsDoc, sbs_render,sbsar, output_path):
    # Retaining the dictionary approach for now, but this should be removed later in the future.
    parameter_label_list = []
    sbsGraphDict = {}

    # Extract variables from sbsDoc and randomize the params.
    graph_list = sbsDoc.getSBSGraphList()

    for graph in graph_list:
        # Input parameters.
        graph_label = graph.getAttribute(aAttributeIdentifier=sbsenum.AttributesEnum.Label)
        param_list = graph.getAllInputsInGroup(aGroup='input_parameter')
        paramDict = {}
        for param in param_list:
            param_label = param.getAttribute(aAttributeIdentifier=sbsenum.AttributesEnum.Label)
            parameter_label_list.append(param_label)
            paramType = param.getType()

            # Randomize values is based on sbsenum.aParamTypes
            if param_label.endswith("_color"): # Randomizing color, this is a temporary solution.
                rgb = []
                for i in range(3):
                    rgb.append(random.uniform(0,1))
                random_default = rgb

            if paramType == sbsenum.ParamTypeEnum.FLOAT1:
                random_default = random.uniform(param.getMinValue(),param.getMaxValue())

            elif paramType == sbsenum.ParamTypeEnum.INTEGER1:
                random_default = random.randint(param.getMinValue(),param.getMaxValue())

            elif paramType == sbsenum.ParamTypeEnum.FLOAT4:
                random_value_list = []
                for i in range(4):
                    rand = random.uniform(0.0,1.0)
                    random_value_list.append(rand)
                random_default = str(random_value_list)

            elif paramType == sbsenum.ParamTypeEnum.BOOLEAN:
                boolList = [
                    param.getMinValue(),
                    param.getMaxValue()
                ]
                random_default = random.choice(boolList)

            elif paramType == sbsenum.ParamTypeEnum.FLOAT3:
                random_value_list = []
                for i in range(3):
                    rand = random.uniform(0.0,1.0)
                    random_value_list.append(rand)
                random_default = str(random_value_list)
            else:
                error = "param type: " + str(paramType) + "needs input"
                raise ValueError(error)

            
            paramDict[param_label] = random_default

        sbsGraphDict[graph_label] = paramDict


    return sbsGraphDict