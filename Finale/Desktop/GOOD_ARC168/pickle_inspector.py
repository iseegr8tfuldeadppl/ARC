import pickle
filename = "variables.pickle"

with open(filename, 'rb') as f:
    All = pickle.load(f)
    if All.get("armPositions") != None:
        for i in All["armPositions"]["Squares"]:
            print(i)
    #if All.get("cargoPositions") != None:
    #    print(All["cargoPositions"])
    #if All.get("hsvs") != None:
    #    print(All["hsvs"])
    #if All.get("canny") != None:
    #    print(All["canny"])