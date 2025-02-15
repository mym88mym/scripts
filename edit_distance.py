''' this is string doc'''
import sys


def minEditDist(sm, sn):
    ''' this is function docstring'''
    m, n = len(sm)+1, len(sn)+1
    # create a matrix (m*n)
    matrix = [[0]*n for i in range(m)]
    matrix[0][0] = 0
    for i in range(1, m):
        matrix[i][0] = matrix[i-1][0] + 1

    for j in range(1, n):
        matrix[0][j] = matrix[0][j-1]+1

    #   for i in range(m):
    #       print matrix[i]
    #   print "********************"
    cost = 0
    for i in range(1, m):
        for j in range(1, n):
            if sm[i-1] == sn[j-1]:
                cost = 0
            else:
                cost = 1
            matrix[i][j] = min(
                    matrix[i-1][j]+1,
                    matrix[i][j-1]+1,
                    matrix[i-1][j-1]+cost)

#   for i in range(m):
#      print matrix[i]
    return matrix[m-1][n-1]

string1 = sys.argv[1]
string2 = sys.argv[2]
mindist = minEditDist(string1, string2)
print mindist
