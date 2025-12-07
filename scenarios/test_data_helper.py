import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  
from data.utils.data_helper import save, load
import numpy as np

do_save = False
if do_save ==True:
    A = np.linspace(1,10,10)
    save(A=A)
    print("A saved")

if do_save == False:
    B = load("A")
    print(B)