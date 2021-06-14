import chemicals


def calcComp(chemicals, mixratio, components, amount):
    # chemicals is a dict, key is the name of the chemical, the resulting object has functions .density and .molarMass
    # mixratio is a list, containing the ratio of each component. it doesn't have to add up to one
    # components is a list, containing the names of the chemicals
    # amount is the total amount of solution needed
    # output: vol is a list, containing the volume of each component

    # create a normalized mixratio list, called mixratio_norm
    mixratio_norm = []
    for r in mixratio:
        mixratio_norm = mixratio_norm + [r/sum(mixratio)]     #https://www.codespeedy.com/how-to-add-all-numbers-in-a-list-in-python/

    # List including molar masses
    M = []
    for c in components:
        M = M + [chemicals[c].molarMass]   #get the molar mass of each component

    # List including densities
    rho = []
    for c in components:
        rho = rho + [chemicals[c].density]     #get the density of each component      https://www.w3schools.com/python/python_classes.asp

    #if len(components) == 1:
    #    return amount
    #if len(components) == 2:
    #    n_1 = amount / (M[0]/rho[0] + (1-mixratio)/(mixratio) * (M[1]/rho[1]))      #calculate the amount of substance 1
    #    n_2 = (1-mixratio)/(mixratio) * n_1         #calculate the amount of substance 2
    #    v_1 = n_1 * M[0] / rho[0]       #Volume of substance 1
    #    v_2 = n_2 * M[1] / rho[1]       #Volume of substance 2
    #    vol = [v_1, v_2]        #lists volume of each component
    #    return vol         #https://realpython.com/python-return-statement/
    #if len(components) > 1:

    # Calculate volume fraction-denominator
    volcalc = 0
    for i in range(len(components)):
        volcalc = volcalc + mixratio_norm[i] * M[i] / rho[i]

    # list which will contain volumes of all components
    vol = []
    for i in range(len(components)):
        vol = vol + [mixratio_norm[i] * M[i] / rho[i] / volcalc * amount]
    return vol


    #missing: DeadVolume

