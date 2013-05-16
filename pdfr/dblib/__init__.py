#!/usr/bin/env python

import dblite

def getSqliteAdapter(app):
    return dblite.Adapter(app)
