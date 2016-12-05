import os

BASE = "output"


def get_num_players(files):
    total = 0
    for file in files:
        if "info" in file:
            with open(BASE + "/" + file) as f:
                for i, l in enumerate(f):
                    pass
            total += i + 1
    return total


def get_num_interests(files):
    total = 0
    for file in files:
        if "interest" in file:
            with open(BASE + "/" + file) as f:
                for i, l in enumerate(f):
                    pass
            total += i + 1
    return total


if __name__ == "__main__":
    all_files = os.listdir(BASE)
    num_players = get_num_players(all_files)
    num_interests = get_num_interests(all_files)

    print("Total number of recruits: " + str(num_players))
    print("Total number of interests: " + str(num_interests))
    print("Average interests per recruit: " + str(num_interests / num_players))