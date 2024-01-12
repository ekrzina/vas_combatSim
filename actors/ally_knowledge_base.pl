% ally_knowledge_base.pl

:- dynamic has_weakness/2.
:- discontiguous has_weakness/2.

:- dynamic has_strength/2.
:- discontiguous has_strength/2.

:- dynamic is_immune/2.
:- discontiguous is_immune/2.


has_strength(rock-crab, melee).
has_strength(ice-crab, melee).
is_immune(doom-shroom, poison).
