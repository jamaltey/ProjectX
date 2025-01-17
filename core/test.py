A = [5, 4, 6, 7, 6, 8, 7, 7, 6, 9]
c = 0
for i in range(9):
    if A[i-1] <= A[i]:
            c = c + A[i]
print(c)
