def sequence_number():
    number = 1
    while True:
        for _ in range(number):
            yield number
        number += 1

n = int(input("Введите количество элементов: "))
sequence = sequence_number()
print("".join(str(next(sequence)) for _ in range(n)))
