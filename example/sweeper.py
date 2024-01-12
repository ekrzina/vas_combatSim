from pyswip import Prolog

# Create Prolog instance and consult the knowledge base
prolog = Prolog()
prolog.consult(r'C:\\Users\\elena\\Desktop\\pos\\vas\\projekt\\vas_combatSim\\example\\kb.pl')

# Query and print all instances of pluta(X)
query_result = list(prolog.query('pluta(X)'))
for result in query_result:
    print(result['X'])
    

with open('C:\\Users\\elena\\Desktop\\pos\\vas\\projekt\\vas_combatSim\\example\\kb.pl', 'a') as file:
    file.write('pluta(maramica).\n')