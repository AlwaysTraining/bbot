#!/usr/bin/env python

# Author: Derrick H. Karimi
# Emerging Technology Center, Carnegie Mellon University, Copyright 2013
# Unclassified

import botlog
from Data import *

def default_region_ratio(app, context):
    r = Regions()
    r.desert.number = 1
    return r

class MetaData(dict):

    def __init__(self, data):
        self.data = data
        self.get_region_ratio_func = default_region_ratio







        
        
 



