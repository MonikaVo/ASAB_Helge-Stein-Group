import sys
from pathlib import Path

def test_paths_prior():
    print('prior', sys.path)
    # Remove the paths from system path to ensure the correct starting conditions
    while str(Path("...","src","ASAB")) in sys.path: # edited prior to publication
        sys.path.remove(str(Path("...","src","ASAB"))) # edited prior to publication
    while str(Path("...","QmixSDK","lib","python")) in sys.path:
        sys.path.remove(str(Path("...","QmixSDK","lib","python"))) # edited prior to publication
    while str(Path("...","QmixSDK")) in sys.path:
        sys.path.remove(str(Path("...","QmixSDK"))) # edited prior to publication

    # ensure, that the paths are not yet in the system path
    # ASAB folder
    assert str(Path("...","src","ASAB")) not in sys.path, f"The ASAB path already was in the PYTHONPATH." # edited prior to publication
    # QmixSDK_python folder
    assert str(Path("...","QmixSDK","lib","python")) not in sys.path, f"The QmixSDK_python path already was in the PYTHONPATH." # edited prior to publication
    # QmixSDK folder
    assert str(Path("...","QmixSDK")) not in sys.path, f"The QmixSDK path already was in the PYTHONPATH." # edited prior to publication

def test_excepthook_prior():
    # set the exceptionhook to its standard value to ensure the correct starting conditions
    sys.excepthook = sys.__excepthook__

    # ensure, that the excepthook was different in the beginning
    assert sys.excepthook.__doc__ == "Handle an exception by displaying it with a traceback on sys.stderr.", f"The docstring is {exceptHook_initial.__doc__} instead of ' Handle an exception by displaying it with a traceback on sys.stderr. '."

# This test seems superfluous -> TODO: check
def test_paths_after():
    import ASAB

    # ensure, that the paths are now in the system path
    print(sys.path[8])
    print(str(Path("...","src","ASAB").resolve())) # edited prior to publication
    # ASAB folder
    assert str(Path("...","src","ASAB")) in sys.path, f"The ASAB path is not in the PYTHONPATH." # edited prior to publication
    # QmixSDK_python folder
    assert str(Path("...","QmixSDK","lib","python")) in sys.path, f"The QmixSDK_python path is not in the PYTHONPATH." # edited prior to publication
    # QmixSDK folder
    assert str(Path("...","QmixSDK")) in sys.path, f"The QmixSDK path is not in the PYTHONPATH." # edited prior to publication

def test_exceptHook_after():
    import ASAB

    # ensure, that the excepthook is changed
    assert sys.excepthook.__doc__ == " This is a modified excepthook, which stops all pumps prior to exiting. ", f"The docstring is {sys.excepthook.__doc__} instead of ' This is a modified excepthook, which stops all pumps prior to exiting. '."
