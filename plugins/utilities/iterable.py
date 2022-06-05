from builtins import next

# for when you need to loop a big array but just want the first N items
def limit(j: int, arr):
    i = 0
    iterable = iter(arr)

    while True:
        try:
            yield next(iterable)
        except StopIteration:
            break

        i = i + 1
        if i == j:
            break
