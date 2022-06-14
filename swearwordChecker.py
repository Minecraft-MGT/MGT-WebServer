import os
from pathlib import Path

swearword_list = []
#Loading swearword list from file to list
swearword_list_path = Path.joinpath(Path(__file__).parent.absolute(), os.getenv("DATABASE_PATH", "./swearwords"))
if os.path.isfile(swearword_list_path):
    with open(swearword_list_path, "r") as file:
        for line in file.read().split("\n"):
            swearword_list.append(line.lower())

def contains_swearwords(text:str):
    text = text.lower()
    for csw in swearword_list:
        if csw in text:
            print(f"{text} containing {csw}")
            return True
    return False

if __name__ == "__main__":
    while True:
        print(contains_swearwords(input("TestString: ")))