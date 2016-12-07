import sqlite3
import numpy as np
import csv
import sys

conn = sqlite3.connect("recruit_db.sqlite")
cursor = conn.cursor()
csv.field_size_limit(sys.maxsize)

places = {}

def load_places():
    with open("US.txt") as f:
        reader = csv.reader(f, delimiter='\t')
        total = 0
        for row in reader:
            names = []
            state = row[10]
            main_name = row[1]
            ascii_name = row[2]
            alt_names = row[3]
            names.append(main_name)
            names.append(ascii_name)
            names += alt_names.split(",")
            lat = row[4]
            long = row[5]
            for name in names:
                name_state = name + "|" + state
                places[name_state] = [lat, long]

def geocode(city, state):
    name_state = city + "|" + state
    if name_state in places:
        lat_long = places[name_state]
        return lat_long
    else:
        print("NONE", city, state)
        return [0,0]


def get_data():
    load_places()
    schools = get_unique_classes()
    n_classes = len(schools)
    featureset = []

    print("Querying")
    cursor.execute("SELECT r.rating, r.city, r.state, i.school FROM recruits r INNER JOIN interests i ON r.id = i.recruit_id WHERE i.status = 'Committed' OR i.status = 'Enrolled' OR i.status = 'Signed' LIMIT 1000")
    none = 0
    res = cursor.fetchall()
    for i, row in enumerate(res):
        print(i)
        rating = row[0]
        city = row[1]
        state = row[2]
        school = row[3]

        location = geocode(city, state)
        if location == [0,0]:
            none += 1
        lat = location[0]
        long = location[1]
        features = np.zeros(3)
        features[0] = rating
        features[1] = lat
        features[2] = long
        features = list(features)

        classification = np.zeros(n_classes)
        classification[schools.index(school)] = 1
        classification = list(classification)

        featureset.append([features, classification])
    print(none)
    return featureset


def get_unique_classes():
    school_list = []
    cursor.execute("SELECT DISTINCT i.school FROM recruits r INNER JOIN interests i ON r.id = i.recruit_id WHERE i.status = 'Committed' OR i.status = 'Enrolled' OR i.status = 'Signed'")

    school_res = cursor.fetchall()
    for row in school_res:
        school_list.append(row[0])

    return school_list

get_data()