from mercurial.ui import ui as UI

def log(msg, ui: UI):  # pragma: no cover
    if ui is not None:
        ui.write("HGCACHE: {msg}\n".format(msg=msg).encode())
    else:
        print("HGCACHE: {msg}".format(msg=msg))
