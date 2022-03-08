menu1 = ["802.11a", "802.11g", "802.11n", "802.11ac_w1", "802.11ac_w2", "802.11ax"]

menu2 = ["Maximum", "Minimum"]

menu3 = ["UDP", "TCP"]

def main():
    print("Which Standard would you like to use?")

    for i, std in enumerate(menu1):
        print(f"{i+1}. {std}")

    x = input("Number of standard: ")

    x = int(x)-1

    standard = menu1[x]

    print(f"You have chosen the {standard} standard.")

    print("Which data rate would you like to use?")

    for i, dr in enumerate(menu2):
        print(f"{i+1}. {dr}")

    x = input("Number of Data Rate: ")

    x = int(x)-1

    data_rate = menu2[x]

    print(f"You have chosen the {data_rate} data rate.")

    print("Which protocol would you like to use?")

    for i, prot in enumerate(menu3):
        print(f"{i+1}. {prot}")

    x = input("Number of Protocol: ")

    x = int(x)-1

    protocol = menu3[x]

    print(f"You have chosen the {protocol} protocol.")


if __name__ == "__main__":
    main()