from engine import engine

# Drivers
from betmgm import betmgm
from betrivers import betrivers
from draftkings import draftkings
from hardrock import hardrock
from fanduel import fanduel

def main():
    drivers = {
        'betmgm' : betmgm(),
        'betrivers' : betrivers()
    }
    e = engine(drivers)
    e.run()

if __name__ == '__main__':
    main()