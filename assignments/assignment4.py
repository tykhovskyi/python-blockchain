# 1) Create a list of “person” dictionaries with a name, age and
#    list of hobbies for each person. Fill in any data you want.
persons = [
    {'name': 'Max', 'age': 15, 'hobbies': [
        'Fishing', 'Baseball', 'Paintball']},
    {'name': 'Kate', 'age': 22, 'hobbies': [
        'Photography', 'Sand art', 'Dance', 'Cooking']},
    {'name': 'Juliya', 'age': 19, 'hobbies': [
        'Dance', 'Fashion', 'Photography']},
    {'name': 'John', 'age': 32, 'hobbies': [
        'Lego building', 'Electronics', 'Astronomy']}
]

# 2) Use a list comprehension to convert this list of persons
#    into a list of names (of the persons).
names = [
    person['name']
    for person in persons
]
print(names)

# 3) Use a list comprehension to check whether all persons are older
#    than 20.
isOlder20 = all([
    person['age'] > 20
    for person in persons
])
print(isOlder20)

# 4) Copy the person list such that you can safely edit the name of
#    the first person (without changing the original list).
# presons_copy = persons[:]
persons_copy = [person.copy() for person in persons]
persons_copy[0]['name'] = 'edited_name'
print(persons_copy[0])
print(persons[0])

# 5) Unpack the persons of the original list into different variables
#    and output these variables.
p1, p2, p3, p4 = persons
print(p1)
print(p2)
print(p3)
print(p4)
