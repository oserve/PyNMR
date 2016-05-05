"""
Definitions for application defaults
"""
import pickle
from os.path import exists
from os import remove

configFileName = "pymolNMR.cfg"
defaults = {}

standardDefaults = {'radius': 0.03, 'cutOff': 0.3,
					'colors':
						{
							'Satisfied': [1, 1, 1, 1, 1, 1],
							'tooFar': [ 1, 0, 0, 1, 0, 0],
							'tooClose': [ 0, 0, 1, 0, 0, 1]
						},
		'gradient': 'blue_white_red', 'method': 'sum6',
		'UnSatisfactionMarker': '_US_', 'SatisfactionMarker': '_S_',
		'rangeCutOff': 5,
		'urlPDB': 'ftp://ftp.wwpdb.org/pub/pdb/data/structures/all/nmr_restraints/',
		'gradientColorList' : [
            "blue_green", "blue_magenta", "blue_red", "blue_white_green",
            "blue_white_magenta", "blue_white_red", "blue_white_yellow",
            "blue_yellow", "cbmr", "cyan_magenta", "cyan_red",
            "cyan_white_magenta", "cyan_white_red", "cyan_white_yellow",
            "cyan_yellow", "gcbmry", "green_blue", "green_magenta",
            "green_red", "green_white_blue", "green_white_magenta",
            "green_white_red", "green_white_yellow", "green_yellow",
            "green_yellow_red", "magenta_blue", "magenta_cyan",
            "magenta_green", "magenta_white_blue", "magenta_white_cyan",
            "magenta_white_green", "magenta_white_yellow", "magenta_yellow",
            "rainbow", "rainbow2", "rainbow2_rev", "rainbow_cycle",
            "rainbow_cycle_rev", "rainbow_rev", "red_blue", "red_cyan",
            "red_green", "red_white_blue", "red_white_cyan", "red_white_green",
            "red_white_yellow", "red_yellow", "red_yellow_green", "rmbc",
            "yellow_blue", "yellow_cyan", "yellow_cyan_white", "yellow_green",
            "yellow_magenta", "yellow_red", "yellow_white_blue",
            "yellow_white_green", "yellow_white_magenta", "yellow_white_red",
            "yrmbcg"
            ]
        }


def registerDefaults(newDefaults):
    """
    """
    defaults.update(newDefaults)


def defaultForParameter(parameter):
    """
    """
    return defaults[parameter]


def setToStandardDefaults():
    """
    """
    defaults.update(standardDefaults)
    if exists(configFileName):
        remove(configFileName)


def saveDefaults():
    """
    """
    configFile = open(configFileName, 'w')
    pickle.dump(defaults, configFile)
    configFile.close()


def loadDefaults():
    """
    """
    if exists(configFileName):
        configFile = open(configFileName, 'r')
        defaults.update(pickle.load(configFile))
        configFile.close()
    else:
        setToStandardDefaults()
