#!/usr/bin/env python2


def log(msg="", ui=None):
    if ui is not None:
        ui.write("HGCACHE: {msg}\n".format(msg=msg))
    else:
        print "HGCACHE: {msg}".format(msg=msg)
