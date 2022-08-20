import pickle
filename = "variables.pickle"

with open(filename, 'rb') as f:
    All = pickle.load(f)
    if All.get("hsvs") != None:
        print(All["hsvs"]["Blue"])
    #if All.get("canny") != None:
    #    print(All["canny"])
    #if All.get("armPositions") != None:
    #    print(All["armPositions"])