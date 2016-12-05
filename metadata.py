import os

def get_num_players():
    files = os.listdir("output")
    total = 0
    for file in files:
        if "info" in file:
            with open("output/" + file) as f:
                for i, l in enumerate(f):
                    pass
            total += i + 1
    return total


if __name__ == "__main__":
    num_players = get_num_players()
    # interest_metadata = get_interests_metadata()

    print("Total number of players: " + str(num_players))