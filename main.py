from klasterizacia import klasterizacia
from SVM_2 import SVM_2
from regression_analysis import regression_analysis
from method_loctya import method_loctya
from random_forest import random_forest
from IAD import *

def main_func():

    regression_analysis()
    method_loctya()
    klasterizacia()
    SVM_2()
    random_forest()
main_func()