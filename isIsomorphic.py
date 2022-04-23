import numpy as np
from itertools import permutations


def is_isomorphic(A, B):
    A = np.array(A)
    B = np.array(B)
    if len(A) != len(A[0]) or len(B) != len(B[0]) or A.size != B.size or np.sum(A) != np.sum(B):
        return False
    n = len(A)
    eye_mat = np.eye(n)
    permuts = permutations(range(n))
    for permut in permuts:
        eye = np.array([eye_mat[i] for i in permut])
        if (eye.transpose() @ A @ eye == B).all():
            return True


# a = [[0, 1, 0],
#      [1, 0, 1],
#      [0, 1, 0]]
#
# b = [[0, 0, 1],
#      [0, 0, 1],
#      [1, 1, 0]]
#
# с = [[0, 1, 0],
#      [1, 1, 1],
#      [0, 1, 0]]
#
# print(is_isomorphic(b, a))
