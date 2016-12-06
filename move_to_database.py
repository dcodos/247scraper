import sqlite3
import os
import csv

BASE = "output"


def get_recruits(files):
    recruits = []
    for file in files:
        if "info" in file:
            with open(BASE + "/" + file) as f:
                reader = csv.reader(f)
                for row in reader:
                    recruits.append(row)
    return recruits


def get_interests(files):
    interests = []
    for file in files:
        if "interest" in file:
            with open(BASE + "/" + file) as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[2] == "Yes":
                        row[2] = True
                    else:
                        row[2] = False
                    if len(row[4]) > 0:
                        date_items = row[4].split("/")
                        month = date_items[0]
                        day = date_items[1]
                        year = date_items[2]
                        date_string = str(year) + "-"
                        if int(month) < 10:
                            date_string += "0"
                        date_string += str(month) + "-"
                        if int(day) < 10:
                            date_string += "0"
                        date_string += str(day)
                        row[4] = date_string
                    interests.append(row)
    return interests


if __name__ == "__main__":
    conn = sqlite3.connect("recruit_db.sqlite")
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS recruits')
    cursor.execute('DROP TABLE IF EXISTS interests')
    cursor.execute('CREATE TABLE recruits (id INTEGER, name TEXT, city TEXT, state TEXT, hs TEXT, position TEXT, height TEXT, weight INTEGER, stars INTEGER, rating DECIMAL)')
    cursor.execute('CREATE TABLE interests (id INTEGER PRIMARY KEY, recruit_id INTEGER, school TEXT, offer BOOLEAN, status TEXT, status_date DATE, FOREIGN KEY(recruit_id) REFERENCES recruits(id))')
    conn.commit()

    all_files = os.listdir(BASE)

    all_recruits = get_recruits(all_files)
    for recruit in all_recruits:
        cursor.execute('INSERT INTO recruits (id, name, city, state, hs, position, height, weight, stars, rating) VALUES (?,?,?,?,?,?,?,?,?,?)', recruit)

    all_interests = get_interests(all_files)
    for interest in all_interests:
        cursor.execute('INSERT INTO interests (recruit_id, school, offer, status, status_date) VALUES (?,?,?,?,?)', interest)

    conn.commit()
    conn.close()
