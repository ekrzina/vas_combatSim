# main game file of project; sets up game then starts combat loop

from setupGame import setupGame
from combat import startCombat

if __name__ == "__main__":
    actors = setupGame()
    startCombat(actors)