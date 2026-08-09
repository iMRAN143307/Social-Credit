import csv
import random

with open("/Users/imran/Desktop/Scred/new.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows([[random.choice(["U001", "U002"]), random.choice(["Jane", "John"]), random.choice(["heresy", "accepting"])]])
