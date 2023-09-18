import os

missing = []

with open("data/download_history.txt", "r") as f:
    data = f.read()
    # lines = [line.strip for line in lines]

    for fname in os.listdir("data/workflows"):
        fname = "/".join(fname.split("_")[:2])
        fname = "repo_" + fname

        if fname not in data:
            missing.append(fname)
