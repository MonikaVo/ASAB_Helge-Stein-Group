from experiment import calcComp, chemicals
# import calcComp
# import chemicals
# import testCalcComp

#create dict chemList including objects of class chemicals
#only necessary, if "Chemicals_database.csv" changed
#chemList = chemicals.getChemicalsList("Chemicals_database.csv")           #https://coderslegacy.com/import-class-from-python-file/, https://www.geeksforgeeks.org/python-read-csv-using-pandas-read_csv/

#load chemList
chemList = chemicals.loadChemicalsList(r"chemList")

#just for testing
amount = 1.0
mixratio = [0.5, 0.5]
components = ["H2O", "EtOH"]

print(chemList["EtOH"].molarMass)
print(chemList["EtOH"].density)
#vol = calcComp.calcComp(chemList, mixratio, components, amount)