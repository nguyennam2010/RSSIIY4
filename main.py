script_1 = __import__("call_Positioning_IY")
script_2 = __import__("call_All_Controller4")
script_3 = __import__("EdgeSDK_AP_Coordinate")
script_4 = __import__("EdgeSDK_Client_Number")


def main():
    print("Run script 1...")
    script_1.main()
    print("Run script 2...")
    script_2.main()
    print("Run script 3...")
    script_3.main()
    print("Run script 4...")
    script_4.main()


if __name__ == "__main__":
    main()
