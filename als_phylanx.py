import pandas as pd
import numpy as np
import time
import argparse
import sys


from phylanx import Phylanx, PhylanxSession

PhylanxSession.init(1)

if not len(sys.argv) == 7 :
    print("This program requires the following 6 arguments seperated by a space ")
    print("row_stop col_stop num_factors iterations regularization alpha")
    exit(-57)

parser = argparse.ArgumentParser(description='Parameters')
parser.add_argument('integers', type=int, nargs=4,
                    help='row_stop, col_stop, num_factors, iterations')

parser.add_argument('doubles', type=float, nargs=2,
                    help='regularization, alpha')

args = parser.parse_args()
print("Command Line: " ,args.integers[0], args.integers[1], args.integers[2], args.integers[3],
      args.doubles[0], args.doubles[1])

row_stop = args.integers[0]
col_stop  = args.integers[1]
regularization   = args.doubles[0]
num_factors  = args.integers[2]
iterations = args.integers[3]
alpha=args.doubles[1]

treading=time.time()

print("Reading Data ....")
df = pd.read_csv('/home/jovyan/MovieLens_20m.csv', sep=',',header=None)
df = df.values
print("Slicing ....")
ratings = df[0:row_stop,0:col_stop]
trslice=time.time()
print("Reading and Slicing done in ", trslice - treading, " s ")

print("Starting ALS ....")


@Phylanx
def ALS(ratings, regularization, num_factors, iterations, alpha, X_in, Y_in):
    X = X_in
    Y = Y_in
    num_users = np.shape(ratings)[0]
    num_items = np.shape(ratings)[1]

    conf = alpha * ratings
    conf_u = np.zeros((num_items,1))
    conf_i = np.zeros((num_items,1))

    c_u = np.zeros((num_items, num_items))
    c_i = np.zeros((num_users, num_users))
    p_u = np.zeros((num_items,1))
    p_i = np.zeros((num_users,1))

    I_f = np.identity(num_factors)
    I_i = np.identity(num_items)
    I_u = np.identity(num_users)

    i = 0
    u = 0
    k = 0

    XtX = np.zeros((num_factors, num_factors))
    YtY = np.zeros((num_factors, num_factors))
    A = np.zeros([num_factors, num_factors])
    b = np.zeros([num_factors])
    while k < iterations:
        #if enable_output:
        #    print("iteration ", k)
        #    print("X: ", X)
        #    print("Y: ", Y)
        YtY = np.dot(np.transpose(Y), Y) + regularization * I_f
        XtX = np.dot(np.transpose(X), X) + regularization * I_f
        while u < num_users:
            conf_u = conf[u, :]
            c_u = np.diag(conf_u)
            p_u = conf_u != 0
            A = YtY + np.dot(np.dot(np.transpose(Y), c_u), Y)
            b = np.dot(np.dot(np.transpose(Y), c_u + I_i), np.transpose(p_u))
            X[u, :] = np.dot(inverse(A), b)
            u = u + 1
        while i < num_items:
            conf_i = conf[:, i]
            c_i = np.diag(conf_i)
            p_i = conf_i != 0
            A = XtX + np.dot(np.dot(np.transpose(X), c_i), X)
            b = np.dot(np.dot(np.transpose(X), c_i + I_u), np.transpose(p_i))
            Y[i, :] = np.dot(inverse(A), b)
            i = i + 1
        u = 0
        i = 0
        k = k + 1
    result = np.vstack((X, Y))
    return result

np.random.seed(0)
X=np.random.rand(np.shape(ratings)[0], num_factors)
Y=np.random.rand(np.shape(ratings)[1], num_factors)

tals=time.time()
result=ALS(ratings, regularization, num_factors, iterations, alpha, X, Y)
tfinal= time.time()

print (" X = " , result[0:np.shape(ratings)[0],:])
print (" Y = ", result[0:np.shape(ratings)[1],:])
print (" in time =",tfinal-tals)