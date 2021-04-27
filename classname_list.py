import pickle

names = {"dummy value"}

with open("classnames.txt", "wb") as f:
    pickle.dump(names, f)
