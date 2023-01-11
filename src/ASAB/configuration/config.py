from pathlib import Path

# reference to the directory, where the clone of the github repository is saved,
# but not yet in the folder, which is the clone of the repository
ASAB_folder = Path(__file__).resolve().parents[4]

# store the paths as strings in the config file as otherwise functions like
# sys.path.append() cannot handle the paths
configASAB =    {
                    "ASAB": str(ASAB_folder.joinpath("ASAB","src","ASAB")),
                    "QmixSDK_python": str(ASAB_folder.joinpath("QmixSDK", "lib", "python")),
                    "QmixSDK": str(ASAB_folder.joinpath("QmixSDK"))
                }
