import pickle

names = {"dummy value"}

with open("classnames.bin", "wb") as f:
    pickle.dump(names, f)
