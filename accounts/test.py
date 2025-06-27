
def hidec(func):
    def decorator(name):
        func()
        print(name)
    return decorator

@hidec
def sayhi():
    print('hi', end=' ')

sayhi('Jamal')
