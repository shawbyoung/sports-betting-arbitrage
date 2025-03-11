from promotion import promotion

# Drivers
from betmgm import betmgm
from betrivers import betrivers
from draftkings import draftkings
from hardrock import hardrock
from fanduel import fanduel

def main():
    drivers = {
        'betmgm' : betmgm(),
        'draftkings' : draftkings(),
        'betrivers' : betrivers()
    }
    p = promotion(drivers)
    p.run()

if __name__ == '__main__':
    main()