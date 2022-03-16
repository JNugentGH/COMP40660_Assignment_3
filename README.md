# COMP40660_Assignment_3
Name: John Nugent
Student Number: 17410624

# Compiling
The python script is written for python3.

Numpy is necessary in order for the np.ceil and np.floor functions to operate.
Run the command:
pip3 install numpy

### Install pip3
https://www.activestate.com/resources/quick-reads/how-to-install-and-use-pip3/

# Running
On windows with a version of python3 installed opening the terminal in the folder holding the program and typing:

python3 John_Nugent_17410624_Assignment_3.py

Will run the code in the terminal.
# How to use program
Once the program is running 3 menus will need to be navigated.
The first the option for which WLAN standard you wish to use.
Entering 1-6 followed by enter will take you to the next menu.

Second the whether you want the minimum or maximum data rate.
Enter 1-2 followed by enter will select the corresponding option and move onto the next menu.

Third, whether you want to use UDP or TCP protocols.
Entering 1-2 on the keyboard followed by enter will complete your options and setup.

The program will then execute the computation for the Actual MAC throughput of the standard along with the time in seconds to transmit 15 GB for the options you have chosen.

In the cases of 802.11n, 802.11ac_w1, 802.11ac_w2 and 802.11ax, there will be normal and best case results.
The mimimum option will return the same results for both cases except for 802.11ax, which has different minimum best case results.