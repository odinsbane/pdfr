#!/usr/bin/env python

PARAMETER_FILE = "/Users/msmith/Documents/development/flask/pdfr/pdfr.conf"

def loadParameters():
    lines = open(PARAMETER_FILE,'r').readlines()
    params = {}
    for item in lines:
        if item[0]=='#':
            pass
        else:
            pair = item.strip().split(' ')
            value = pair[1]
            if pair[0] =='USERNAME':
                value = pair[1].split(',')
            params[pair[0]] = value
    return params
    
parameters = loadParameters()
