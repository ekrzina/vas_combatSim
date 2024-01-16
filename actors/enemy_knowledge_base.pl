% enemy_knowledge_base.pl

:- dynamic is_weak_to/2.
:- discontiguous is_weak_to/2.



is_weak_to(wizard, melee).
is_weak_to(ranger, ice).
