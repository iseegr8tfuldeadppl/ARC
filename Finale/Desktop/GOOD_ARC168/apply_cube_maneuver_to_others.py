import pickle

filename = "variables.pickle"
All = None
with open(filename, 'rb') as f:
    All = pickle.load(f)
    if All.get("armPositions") != None:
        #print(All["armPositions"])
        armPositions = All["armPositions"]
        All["armPositions"]["Circles"] = All["armPositions"]["Squares"].copy()
        All["armPositions"]["Rectangles"] = All["armPositions"]["Squares"].copy()
        All["armPositions"]["Triangles"] = All["armPositions"]["Squares"].copy()
    f.close()

with open(filename, 'wb') as f:
    pickle.dump(All, f)
    print("Successfully saved")