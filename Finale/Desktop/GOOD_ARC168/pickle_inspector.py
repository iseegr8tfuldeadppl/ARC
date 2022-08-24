import pickle
filename = "variables.pickle"
filename2 = "variablesbackup2.pickle"
filename3 = "variablesbroo.pickle"
canny = None
hsvs = None
armPositions = None
cargoPositions = None
with open(filename3, 'rb') as f:
    All = pickle.load(f)
    if All.get("armPositions") != None:
        #print(All["armPositions"])
        armPositions = All["armPositions"]
        pass
    if All.get("cargoPositions") != None:
        #print(All["armPositions"])
        #print(All["cargoPositions"])
        cargoPositions = All["cargoPositions"]
        pass

with open(filename2, 'rb') as f:
    All = pickle.load(f)
    if All.get("hsvs") != None:
        hsvs = All["hsvs"]
    if All.get("canny") != None:
        #print(All["canny"])
        canny = All["canny"]
        pass

    with open("okay.pickle", 'wb') as f:
        print("g")
        pickle.dump({"hsvs": hsvs, "canny": canny, "armPositions": armPositions, "cargoPositions": cargoPositions}, f)
        #print("Successfully saved")