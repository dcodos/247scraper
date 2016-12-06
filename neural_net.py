import sqlite3
import tensorflow as tf
import numpy as np
from geopy import geocoders
from tensorflow.examples.tutorials.mnist import input_data
import random
mnist = input_data.read_data_sets("/tmp/data/", one_hot = True)

schools = []
n_nodes_hl1 = 500
n_nodes_hl2 = 500
n_nodes_hl3 = 500
n_classes = 303
batch_size = 100

x = tf.placeholder('float', [None, 3])
y = tf.placeholder('float')

conn = sqlite3.connect("recruit_db.sqlite")
cursor = conn.cursor()

def neural_network_model(data):
    hidden_1_layer = {'weights':tf.Variable(tf.random_normal([3, n_nodes_hl1])),
                      'biases':tf.Variable(tf.random_normal([n_nodes_hl1]))}

    hidden_2_layer = {'weights':tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                      'biases':tf.Variable(tf.random_normal([n_nodes_hl2]))}

    hidden_3_layer = {'weights':tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
                      'biases':tf.Variable(tf.random_normal([n_nodes_hl3]))}

    output_layer = {'weights':tf.Variable(tf.random_normal([n_nodes_hl3, n_classes])),
                    'biases':tf.Variable(tf.random_normal([n_classes])),}

    l1 = tf.add(tf.matmul(data,hidden_1_layer['weights']), hidden_1_layer['biases'])
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.matmul(l1,hidden_2_layer['weights']), hidden_2_layer['biases'])
    l2 = tf.nn.relu(l2)

    l3 = tf.add(tf.matmul(l2,hidden_3_layer['weights']), hidden_3_layer['biases'])
    l3 = tf.nn.relu(l3)

    output = tf.matmul(l3,output_layer['weights']) + output_layer['biases']

    return output


def train_neural_network(x):
    prediction = neural_network_model(x)
    cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(prediction,y) )
    optimizer = tf.train.AdamOptimizer().minimize(cost)

    hm_epochs = 10
    with tf.Session() as sess:
        sess.run(tf.initialize_all_variables())

        for epoch in range(hm_epochs):
            epoch_loss = 0
            i = 0
            while i < len(train_x):
                start = i
                end = i + batch_size
                batch_x = np.array(train_x[start:end])
                batch_y = np.array(train_y[start:end])
                _, c = sess.run([optimizer, cost], feed_dict={x: batch_x, y: batch_y})
                epoch_loss += c
                i += batch_size

            print('Epoch', epoch, 'completed out of',hm_epochs,'loss:',epoch_loss)

        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))

        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        print('Accuracy:',accuracy.eval({x:test_x, y:test_y}))

def get_unique_classes():
    school_list = []
    cursor.execute("SELECT DISTINCT i.school FROM recruits r INNER JOIN interests i ON r.id = i.recruit_id WHERE i.status = 'Committed' OR i.status = 'Enrolled' OR i.status = 'Signed'")

    school_res = cursor.fetchall()
    for row in school_res:
        school_list.append(row[0])

    return school_list

def get_data():
    featureset = []
    gn = geocoders.GeoNames(username="dcodos")

    cursor.execute("SELECT r.rating, r.city, r.state, i.school FROM recruits r INNER JOIN interests i ON r.id = i.recruit_id WHERE i.status = 'Committed' OR i.status = 'Enrolled' OR i.status = 'Signed' LIMIT 1000")

    res = cursor.fetchall()
    for i, row in enumerate(res):
        print(i)
        rating = row[0]
        city = row[1]
        state = row[2]
        school = row[3]
        location = gn.geocode(city + ", " + state)
        lat = location.latitude
        long = location.longitude
        features = np.zeros(3)
        features[0] = rating
        features[1] = lat
        features[2] = long
        features = list(features)

        classification = np.zeros(n_classes)
        classification[schools.index(school)] = 1
        classification = list(classification)

        featureset.append([features, classification])

    return featureset


def split_data(featureset, test_percentage):
    testing_size = int(test_percentage*len(featureset))
    train_x = list(featureset[:,0][:-testing_size])
    train_y = list(featureset[:,1][:-testing_size])
    test_x = list(featureset[:,0][-testing_size:])
    test_y = list(featureset[:,1][-testing_size:])
    return train_x, train_y, test_x, test_y

if __name__ == "__main__":
    print("Getting classes")
    schools = get_unique_classes()
    n_classes = len(schools)
    print("Getting data")
    features = get_data()
    random.shuffle(features)
    features = np.array(features)

    train_x, train_y, test_x, test_y = split_data(features, 0.1)

    train_neural_network(x)
