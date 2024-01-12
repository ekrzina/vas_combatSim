osoba(agnes).
osoba(bridget).

:- dynamic pluta/1.
:- discontiguous pluta/1.

pluta(kruh).
pluta(jabuke).
pluta(kamencic).
pluta(cider).
pluta(olovo).

pluta(maramica).
pluta(patka).

pluta(maramica).


tezikao(agnes,patka).
odDrva(drvo).

odDrva(X) :- teziKao(X,Y), pluta(Y).
vjestica(X) :- odDrva(X), osoba(X).

gori(X) :- odDrva(X).

likes(john, curry).
likes(sandy, mushrooms).

has_weakness(cat, water).

has_weakness(parrot, water).
has_weakness(moose, fire).
