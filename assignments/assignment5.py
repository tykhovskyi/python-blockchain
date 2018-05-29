# 1) Write a normal function that accepts another function 
#    as an argument. Output the result of that other function 
#    in your “normal” function.

def addTwo(number):
    return number + 2

def calculate(operation, number):
    return operation(number)

print(calculate(addTwo, 5))

# 2) Call your “normal” function by passing a lambda function – 
#    which performs any operation of your choice – as an argument.

print(calculate(lambda n: n -2, 5))

# 3) Tweak your normal function by allowing an infinite amount 
#    of arguments on which your lambda function will be executed.

def calculate_ext(operation, *args):
    for arg in args:
        print(operation(arg))

calculate_ext(addTwo, 2, 5, 10)

# 4) Format the output of your “normal” function such that numbers 
#    look nice and are centered in a 20 character column.

def calculate_ext1(operation, *args):
    for arg in args:
        print('Result: {:^20.2f}'.format(operation(arg)))

calculate_ext1(lambda n: n * 2, 3, 12, 44, 123)
