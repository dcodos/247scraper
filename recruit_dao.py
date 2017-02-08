import sqlite3
import numpy as np
import csv
import sys

conn = sqlite3.connect("recruit_db.sqlite")
cursor = conn.cursor()
cursor2 = conn.cursor()
csv.field_size_limit(sys.maxsize)


def get_data():
    schools = get_unique_classes()
    states = get_states()
    n_classes = len(schools)
    featureset = []

    print("Querying")
    cursor.execute("""SELECT a.rating as 'rating', a.city as 'city', a.state as 'state', a.school as 'school', GROUP_CONCAT(i2.school, '|') FROM
  (SELECT r.id, r.rating, r.city, r.state, i.school
   FROM recruits r INNER JOIN interests i ON r.id = i.recruit_id
   WHERE i.status = 'Committed' OR i.status = 'Enrolled' OR i.status = 'Signed') a
INNER JOIN interests i2 ON a.id = i2.recruit_id
GROUP BY 1, 2, 3, 4 ORDER BY 1 DESC""")
    res = cursor.fetchall()
    for i, row in enumerate(res):
        # ints = cursor2.execute("SELECT i.school FROM interests i WHERE i.recruit_id = ?", (row[4],))
        print(i)
        rating = row[0]
        city = row[1]
        state = row[2]
        school = row[3]
        interests = row[4].split("|")
        # features = np.zeros(3)
        # features[0] = rating
        # features[1] = lat
        # features[2] = long

        features = np.zeros(1 + len(states) + len(schools))
        features[0] = rating
        features[states.index(state) + 1] = 1
        for interest in interests:
            features[1 + len(states) + schools.index(interest)] = 1

        features = list(features)

        classification = np.zeros(n_classes)
        classification[schools.index(school)] = 1
        classification = list(classification)

        featureset.append([features, classification])
    return featureset


def get_unique_classes():
    school_list = []
    cursor.execute("SELECT DISTINCT i.school FROM recruits r INNER JOIN interests i ON r.id = i.recruit_id")

    school_res = cursor.fetchall()
    for row in school_res:
        school_list.append(row[0])

    return school_list


def get_states():
    state_list = []
    cursor.execute("SELECT DISTINCT r.state FROM recruits r")

    state_res = cursor.fetchall()
    for row in state_res:
        state_list.append(row[0])

    return state_list
