name = 'Yurii'
age = 32


def print_name_and_age():
    print('Name: ' + name + ', Age: ' + age)


def print_data(arg1, arg2):
    print('arg1: "' + str(arg1) + '", arg2: "' + str(arg2) + '"')


def get_decades(number):
    return number // 10


print_name_and_age()
# print_data(False, 5.1)
print(get_decades(age))
