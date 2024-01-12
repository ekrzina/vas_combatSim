import os
from pyswip import Prolog

prolog = Prolog()

script_dir = os.path.dirname(os.path.realpath(__file__))
file_name = "kb.pl"
file_path = os.path.join(script_dir, file_name).replace('\\', '/')
prolog.consult(file_path)

with open(file_path, 'a') as file:
    file.write('has_weakness(moose, fire).\n')

# Example query
prolog.consult(file_path)
weakness_result = list(prolog.query(f'has_weakness(X, water).'))
print(weakness_result)