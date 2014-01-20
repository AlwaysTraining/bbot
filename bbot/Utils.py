#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import imp
import os,sys
import logging
import Strategy

bbot_TOOL_VERSION="0.1"
ENVIRON_PREFIX="bbot_"


def load_modules(
    modulePaths    # list of paths to python modules
    ):
    """
    Dynamically load each module path in the list modulePaths
    return a dictionary where keys are the items in modulePaths and the
    values are the corresponding loaded module object
    """

    # create empty dictionary for return from function
    modules = {}

    # iterate each path in the list of modulePaths
    for modulePath in modulePaths:

        # expand all environment variables in path with built in function
        expandedModulePath = os.path.expandvars(modulePath)

        if not os.path.exists(expandedModulePath):
            raise Exception("Module path " + str(expandedModulePath) + 
                    " was not found") 

        # split path into base path (module path) and file extension
        mod_name,file_ext = os.path.splitext(os.path.split(modulePath)[-1])

        # set loadFunction to None
        loadFunc = None

        # if file extenstion indicates python source file
        if file_ext.lower() == '.py':
            # set the loadFunction to imp.load_source
            loadFunc = imp.load_source
        # otherwise if the file extension indicates a compiled object
        elif file_ext.lower() == '.pyc':
            # set the loadFunction to imp.load_compiled
            loadFunc = imp.load_compiled

        # if loadFunction is None
        if loadFunc is None:
            # raise an exception for the unexpected path name
            raise Exception("Unable to load module: " + str(expandedModulePath))

        # set the returned python module resulting from invoking 
        #   loadFunction into returning dictionary
        logging.debug("Loading: " + expandedModulePath)
        mod = loadFunc(mod_name, expandedModulePath)
        logging.debug("Loaded: " + expandedModulePath)
        modules[modulePath] = mod

    # return the dictinoary mapping modulePaths to loaded module objects
    return modules

def create_instance(
    modulePath,
    srcMgrTypeName,
    **kwargs
    ):
    """
    string modulePath       the path to a python module (one .py file or a
                              package directory that contains an __init__.py
                              file.  This path may contain environment
                              variables
    string srcMgrTypeN me   the name of the python class that inherits
                              from SourceManager and implements a
                              specific source manager
    **kwargs                keyworded argument list providing arguments to
                              the type's constructor
    """

    # use load_modules utility function to get dictionary mapping 
    #   modulePath to a loaded module 
    # get the loadedModule value from the modulePath key
    py_mod = load_modules([modulePath])[modulePath]

    # get the type specified by the srcMgrTypeName from the loaded module
    if not hasattr(py_mod, srcMgrTypeName):
        raise Exception("Type " + str(srcMgrTypeName) +
                " was not found in " + str(py_mod))
    type_ = getattr(py_mod, srcMgrTypeName)

    # call the tanstances constructor, unwrap the key word argument
    #   dictionary and pass parameters to the constructor
    instance = type_(**kwargs)

    return instance
