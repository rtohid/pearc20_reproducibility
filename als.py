import pandas as pd
import numpy as np
import time
import argparse
import sys

if not len(sys.argv) == 7:
    print(
        "This program requires the following 6 arguments seperated by a space "
    )
    print("row_stop col_stop regularization num_factors iterations alpha")
    exit(-57)

parser = argparse.ArgumentParser(description='Parameters')
parser.add_argument('integers',
                    type=int,
                    nargs=4,
                    help='row_stop, col_stop, num_factors, iterations')

parser.add_argument('doubles',
                    type=float,
                    nargs=2,
                    help='regularization, alpha')

args = parser.parse_args()
print("Command Line: ", args.integers[0], args.integers[1], args.integers[2],
      args.integers[3], args.doubles[0], args.doubles[1])

row_stop = args.integers[0]
col_stop = args.integers[1]
regularization = args.doubles[0]
num_factors = args.integers[2]
iterations = args.integers[3]
alpha = args.doubles[1]

treading = time.time()

print("Reading Data ....")
df = pd.read_csv('/home/jovyan/MovieLens_20m.csv', sep=',', header=None)
df = df.values
print("Slicing ....")
ratings = df[0:row_stop, 0:col_stop]
trslice = time.time()
print("Reading and Slicing done in ", trslice - treading, " s ")

print("Starting ALS ....")

tals = time.time()


def myALS(ratings, regularization, num_factors, iterations, alpha=40):
    num_users = np.shape(ratings)[0]
    num_items = np.shape(ratings)[1]

    conf = alpha * ratings
    np.random.seed(0)
    X = np.random.rand(num_users, num_factors)
    Y = np.random.rand(num_items, num_factors)

    I_f = np.identity(num_factors)
    I_i = np.identity(num_items)
    I_u = np.identity(num_users)

    for k in range(iterations):
        YtY = np.dot(Y.T, Y)
        XtX = np.dot(X.T, X)
        for u in range(num_users):
            conf_u = conf[u, :]
            c_u = np.diag(conf_u)
            p_u = conf_u.copy()
            p_u[p_u != 0] = 1
            #p_u[conf_u!=0]=1
            A = YtY + np.dot(np.dot(Y.T, c_u), Y) + regularization * I_f
            b = np.dot(np.dot(Y.T, c_u + I_i), p_u.T)
            X[u, :] = np.dot(np.linalg.inv(A), b)
        for i in range(num_items):
            conf_i = conf[:, i]
            c_i = np.diag(conf_i)
            p_i = conf_i.copy()
            p_i[p_i != 0] = 1
            #p_i[conf_i!=0]=1
            A = XtX + np.dot(np.dot(X.T, c_i), X) + regularization * I_f
            b = np.dot(np.dot(X.T, c_i + I_u), p_i.T)
            Y[i, :] = np.dot(np.linalg.inv(A), b)

    return X, Y


X, Y = myALS(ratings, regularization, num_factors, iterations, alpha=40)
tfinal = time.time()

print(" X = ", X)
print(" Y = ", Y)
print(" in time =", tfinal - tals)
