import os

# base = "data/action"
# for fname in os.listdir(base):
#     if fname.endswith(".yml_action.yml"):
#         old_fpath = os.path.join(base, fname)
#         new_fname = fname[:-11]
#         new_fpath = os.path.join(base, new_fname)

#     print(fname)

# with open(old_fpath, "r") as f:
#     data = f.read()

# os.remove(old_fpath)

# with open(new_fpath, "w") as f:
#     f.write(data)

# data/action/moby_moby_.github_workflows_.windows.yml
# data/action/moby_moby_.github_workflows_.windows.yml

base = "data/workflows"
for fname in os.listdir(base):
    if len(fname.split("_")) >= 4:
        splitted = fname.split("_")
        new_splitted = splitted[:2] + [".github", "workflows"] + splitted[2:]
        new_name = "_".join(new_splitted)

        print(f"OLD: {fname}")
        print(f"NEW: {new_name}")

    # l = len(fname.split("_"))
    # if l != 3:
    #     print(fname)

    # with open(old_fpath, "r") as f:
    #     data = f.read()

    # os.remove(old_fpath)

    # with open(new_fpath, "w") as f:
    #     f.write(data)
