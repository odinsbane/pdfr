#!/usr/bin/env python


def loadParameters(app):
    lines = []
    with app.open_resource('pdfr.conf') as f:
        lines = f.readlines()
    params = {}
    for item in lines:
        if item[0]=='#':
            pass
        else:
            split_dex = item.find(' ')
            key = item[:split_dex]
            value = item[ split_dex+1: ].strip()
            if key =='USERNAME':
                value = value.split(',')
            if key =='DATABASE':
                if not value[0] == '/':
                    value = '/'.join([app.root_path,value])
            params[key] = value
    return params
    
