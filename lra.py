import time
import numpy as np
from phylanx import Phylanx
from phylanx import PhylanxSession

num_threads = 2
PhylanxSession.init(num_threads)


def lra(x, y, alpha, num_iterations, enable_output=False):
    weights = np.zeros(np.shape(x)[1])
    transx = np.transpose(x)
    pred = np.zeros(np.shape(x)[0])
    error = np.zeros(np.shape(x)[0])
    gradient = np.zeros(np.shape(x)[1])
    step = 0
    while step < num_iterations:
        if (enable_output):
            print("step: ", step, ", ", weights)
        pred = 1.0 / (1.0 + np.exp(-np.dot(x, weights)))
        error = pred - y
        gradient = np.dot(transx, error)
        weights = weights - (alpha * gradient)
        step += 1
    return weights


file_name = "/home/jovyan/10kx10k.csv"
print("reading file, it may take a little while ...")
data = np.genfromtxt(file_name, skip_header=1, delimiter=",")
print("done reading.")
alpha = 1e-5
num_iterations = (10, 10)
phy_lra = Phylanx(lra)
print('num_threads', num_threads)
for n in num_iterations:
    phy_lra_start = time.time()
    phy_lra(data[:, :-1], data[:, -1], alpha, n)
    phy_lra_stop = time.time()
    print('phy_lra', phy_lra_stop - phy_lra_start)
