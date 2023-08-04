# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 19:48:59 2023

@author: Administrator
"""

script_1 = __import__("Client_Data")
script_2 = __import__("AP_Data")
script_3 = __import__("Radio_Data")


def main():
    print("Run script 1...")
    script_1.main()
    print("Run script 2...")
    script_2.main()
    print("Run script 3...")
    script_3.main()

if __name__ == "__main__":
    main()