% ally_knowledge_base.pl

:- dynamic has_weakness/2.
:- discontiguous has_weakness/2.

:- dynamic has_strength/2.
:- discontiguous has_strength/2.

:- dynamic is_immune/2.
:- discontiguous is_immune/2.

is_immune(ice-crab, ice).
has_strength(ice-crab, melee).
has_weakness(lava-crab, ice).
has_weakness(doom-shroom, fire).
has_strength(lava-crab, melee).
is_immune(little-devil, poison).
has_weakness(red-dragon, ranged).
has_strength(undine, ice).
has_weakness(undine, thunder).
is_immune(red-dragon, fire).
has_strength(rock-crab, melee).
has_strength(red-dragon, thunder).
