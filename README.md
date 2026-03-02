# vas_combatSim

Welcome to VAS Combat Sim, a multi-agent system that uses only agents to play a turn-based RPG game. 

SPADE message agents form two groups:
- the "party" group
- the "monster" group

Each agent type has their own unique movesets and weaknesses defined in a randomized `JSON` file, and fights the opposing group. Both allies and enemies have **knowledge bases** that the groups use to target weaknesses once they are learnt.
