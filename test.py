from collections import deque
check_list={'a':deque('x'*10,maxlen=10)}

name='a'
check_list[name].append('o')
print((check_list[name]).count('o'))

