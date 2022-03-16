import numpy as np

class Packet:
    '''Step 1: Packet Size.'''
    def __init__(self):
        self.size = 1500 # Bytes

    def get_size(self):
        return self.size

class Header:
    def __init__(self):
        # a and g total size is 1542
        # n, ac, ax total size = 1548
        self.packet = Packet()

        self.MAC_header = 0 # bytes

        self.SNAP_LLC = 0 # bytes

    def get_size(self):
        return self.packet.get_size() + self.MAC_header + self.SNAP_LLC # Bytes

    def add_MAC_bytes(self, extra):
        # Add 40 for n, ac and ax.
        self.MAC_header = self.MAC_header + extra

    def add_SNAP_bytes(self, extra):
        # Add 8 for ac, ax and an.
        self.SNAP_LLC = self.SNAP_LLC + extra

    def set_n_ac_ax(self):
        self.add_MAC_bytes(40)

        self.add_SNAP_bytes(8)

class Ack:
    def __init__(self):
        self.header_info = 40

        self.MAC_header = 0

        self.SNAP_LLC = 0

    def add_MAC_bytes(self, extra):
        # Add 34 for a/g.
        # Add 40 for n, ac and ax.
        self.MAC_header = self.MAC_header + extra

    def add_SNAP_bytes(self, extra):
        # Add 8 for a, g, ac, ax and an.
        self.SNAP_LLC = self.SNAP_LLC + extra

    def get_size(self):
        return self.header_info + self.MAC_header + self.SNAP_LLC # Bytes

class DataRating:
    def __init__(self, modulation, NBits, CRate, NChan, SDur, Data_Rate, Nss=None):
        self.modulation = modulation

        self.NBits = NBits

        self.CRate = CRate

        self.NChan = NChan

        self.SDur = SDur # mu s

        self.data_rate = Data_Rate # Mbps

        if Nss:
            self.Nss = Nss
        else:
            self.Nss = 1

    def get_bits_per_symbol(self):
        return self.NBits * self.CRate * self.NChan * self.Nss # bits/symbol!

    def get_data_rate(self):
        return self.get_bits_per_symbol() / self.SDur # Mbps

    def __str__(self):
        return f"{self.get_data_rate()} Mb/s"

    
class a:
    def __init__(self, protocol=None, data_speed=None):
        self.name = "802.11a"

        self.header = Header()
        
        self.header.add_MAC_bytes(34) # bytes

        self.header.add_SNAP_bytes(8)   # Bytes

        # self.SIFS = 16 # mu s
        self.set_sifs(16) # mu s

        self.slot = 9 # mu s

        self.symbol_tx_time = 4 # mu s

        self.ofdm_tail = 6 # bits!

        self.rts_size = 20 # bytes

        self.cts_size = 14 # bytes

        self.mac_ack_size = 14 # Bytes

        # Step 2: Ack size.
        self.tcp_ack = Ack()
        self.tcp_ack.add_MAC_bytes(34)
        self.tcp_ack.add_SNAP_bytes(8)

        self.preamble = 20 # mu s

        self.data_ratings = [DataRating("BPSK", 1, 1/2, 48, 4, 6), DataRating("64-QAM", 6, 3/4, 48, 4, 54)]

        if not protocol:
            # Default to UDP.
            self.protocol = 'UDP' 

        if not data_speed:
            # default to Max
            self.data_rating = self.data_ratings[1]


    def setup(self, protocol, data_speed):
        if protocol == 'UDP':
            self.protocol = 'UDP'
        
        else:
            self.protocol = 'TCP'

        if data_speed == 'Minimum':
            self.data_rating = self.data_ratings[0]

        else:
            self.data_rating = self.data_ratings[1]

    def set_sifs(self, sif):
        self.SIFS = sif

    def get_DIFS(self):
        return (2*self.slot) + self.SIFS

    def set_OFDM(self):
        self.ofdm_tail = 6

    def get_bits_per_frame(self):
        ''' Step 4: Get bits per OFDM Frame.'''
        header_bits = self.header.get_size() * 8

        ofdm_bits_pf = header_bits + self.ofdm_tail            # bits per OFDM frame.

        return ofdm_bits_pf

    def get_ofdm_symbols(self):
        ''' Step 5: Symbols per frame.'''
        # (bits/frame) / (bits/symbol) = symbol/frame
        ofdm_symbols = self.get_bits_per_frame() / self.bits_per_ofdm_symbol() 
        
        # Round up to nearest integer.
        return  np.ceil(ofdm_symbols)                   
    
    def bits_per_ofdm_symbol(self, verbose=False):
        '''Step 3: Data bits per OFDM symbol.'''
        # bps = self.data_rating.NBits * self.data_rating.CRate * self.data_rating.NChan # bits/symbol!
        bps = self.data_rating.get_bits_per_symbol()
        
        bps = np.floor(bps) # Round down to nearest integer.

        # Print to see workings.
        if verbose:
            print(f"Bits per ofdm Symbol: {bps}")
            
        return bps

    def frame_transmit_time(self):
        '''Step 6: frame transmit time'''
        return self.get_ofdm_symbols() * self.symbol_tx_time # mu s

    def rts_tx_time(self):
        '''Step 7.1: RTS transmit time.'''
        return self.symbols_to_tx_time(self.bits_to_symbols((self.rts_size*8)+6))

    def cts_tx_time(self):
        '''Step 7.2: CTS transmit time.'''
        return self.symbols_to_tx_time(self.bits_to_symbols((self.cts_size*8)+6))

    def ack_tx_time(self):
        '''Step 8.1: MAC ACK transmit time.'''
        return self.symbols_to_tx_time(self.bytes_to_symbols(self.mac_ack_size))

    def tcp_ack_tx_time(self, verbose=False):
        byt = self.tcp_ack.get_size()

        symbols = self.bytes_to_symbols(byt)

        time = self.symbols_to_tx_time(symbols)

        if verbose:
            print(f"tcp ack\nbytes: {byt}\nsymbols:{symbols}\ntime:{time}")

        return time # mu s

    # def data_rate(self):
    #     return (1/self.SDur) * (self.bits_per_ofdm_symbol())

    def bits_to_symbols(self, bit_count):
        return np.ceil(bit_count / self.bits_per_ofdm_symbol())

    def bytes_to_symbols(self, byte_count):
        return self.bits_to_symbols(byte_count*8)

    def symbols_to_tx_time(self, symbol_count):
        return symbol_count * self.symbol_tx_time # symbols * mu s = mu s

    def tx_data_time(self, verbose = False):
        # tx_time = self.symbols_to_tx_time(self.bits_to_symbols((1500*8)+6))
        bits = (self.header.get_size()*8)+6

        symbols = self.bits_to_symbols(bits)
        
        tx_time = self.symbols_to_tx_time(symbols)

        if verbose:
            print(f"bits:{bits}\nsymbols:{symbols}\nTime to Transmit 1 Data Packet: {tx_time}")
        
        return tx_time

    def time_to_send(self):
        '''Step 9: Sum all tx times.'''
        sum = 0
        
        sum = sum + self.get_DIFS()
        sum = sum + self.preamble 
        sum = sum + self.rts_tx_time() 
        sum = sum + self.SIFS 
        sum = sum + self.preamble 
        sum = sum + self.cts_tx_time() 
        sum = sum + self.SIFS
        sum = sum + self.preamble 
        sum = sum + self.tx_data_time(verbose=False) 
        sum = sum + self.SIFS
        sum = sum + self.preamble 
        sum = sum + self.ack_tx_time()

        if self.protocol == 'TCP':
            sum = sum + self.SIFS
            sum = sum + self.tcp_ack_tx_time()
            # print(f"tcp ack tx time: {self.tcp_ack_tx_time()}")


        return sum # mu s

    def get_throughput(self, bytes_in):
        '''Step 10: Throughput.'''
        bits = bytes_in*8

        seconds = self.time_to_send() /1e6 #... seconds

        return bits / seconds # bits/second

    def time_to_transfer(self, bytes_in):
        bits = bytes_in*8 # bits

        throughput = self.get_throughput(Packet().get_size()) # bits/second

        return bits / throughput # bits / (bits/second) = seconds
    
    # End of class a.

class g(a):
    def __init__(self, protocol=None, data_speed=None):
        a.__init__(self, protocol, data_speed)

        self.name = "802.11g"

        self.set_sifs(10)

    def time_to_send(self):
        return a.time_to_send(self) + 6 # mu s
        
    # End of class g.

class n(a):
    def __init__(self, protocol=None, data_speed=None):
        a.__init__(self, protocol, data_speed)

        self.name = "802.11n"

        self.set_sifs(16) # mu s

        self.header = Header()

        self.header.add_MAC_bytes(40) # Bytes

        self.header.add_SNAP_bytes(8) # Bytes

        self.symbol_tx_time = 3.6 # mu s

        self.preamble = 46 # mu s

        self.tcp_ack = Ack()
        self.tcp_ack.add_MAC_bytes(40)
        self.tcp_ack.add_SNAP_bytes(8)

        self.data_ratings = [DataRating("BPSK", 1, 1/2, 52, 3.6, 7.2), DataRating("64-QAM", 6, 5/6, 52, 3.6, 72.2)]

class n_best(n):
    def __init__(self, protocol=None, data_speed=None):
        n.__init__(self, protocol, data_speed)

        self.data_ratings = [DataRating("BPSK", 1, 1/2, 52, 3.6, 7.2), DataRating("40 MHz", 6, 5/6, 108, 3.6, 150, 4)]


class ac_w1(n):
    def __init__(self, protocol=None, data_speed=None):
        n.__init__(self, protocol=protocol, data_speed=data_speed)

        self.name = "802.11ac_w1"

        self.preamble = 56.8

        self.data_ratings = [DataRating("BPSK", 1, 1/2, 52, 3.6, 7.2), DataRating("256-QAM", 8, 5/6, 52, 3.6, 96.3)]

class ac_w1_best(ac_w1):
    def __init__(self, protocol=None, data_speed=None):
        ac_w1.__init__(self, protocol, data_speed)

        self.data_ratings = [DataRating("BPSK", 1, 1/2, 52, 3.6, 7.2), DataRating("80MHz", 8, 5/6, 234, 3.6, 433.3, 3)]

class ac_w2(n):
    def __init__(self, protocol=None, data_speed=None):
        n.__init__(self, protocol=protocol, data_speed=data_speed)

        self.name = "802.11ac_w2"

        self.preamble = 92.8

        self.data_ratings = [DataRating("BPSK", 1, 1/2, 52, 3.6, 7.2), DataRating("256-QAM", 8, 5/6, 52, 3.6, 96.3, 1)]

class ac_w2_best(ac_w2):
    def __init__(self, protocol=None, data_speed=None):
        ac_w2.__init__(self, protocol, data_speed)

        self.data_ratings = [DataRating("BPSK", 1, 1/2, 52, 3.6, 7.2), DataRating("160MHz", 8, 5/6, 468, 3.6, 866.7, 8)]

class ax(ac_w2):
    def __init__(self, protocol=None, data_speed=None):
        ac_w2.__init__(self, protocol, data_speed)

        self.name = "802.11ax"

        self.data_ratings = [DataRating("BPSK", 1, 1/2, 234, 13.6, 8.6), DataRating("1024-QAM", 10, 5/6, 234, 13.6, 143.4, 1)]

class ax_best(ax):
    def __init__(self, protocol=None, data_speed=None):
        ax.__init__(self, protocol, data_speed)

        self.data_ratings = [DataRating("BPSK", 1, 1/2, 1960, 13.6, 576.5, 8), DataRating("1024-QAM", 10, 5/6, 1960, 13.6, 9607.8, 8)]

menu1 = ["802.11a", "802.11g", "802.11n", "802.11ac_w1", "802.11ac_w2", "802.11ax"]

menu2 = ["Minimum", "Maximum"]

menu3 = ["UDP", "TCP"]

def main():
    print("Which Standard would you like to use?")

    for i, std in enumerate(menu1):
        print(f"{i+1}. {std}")
    
    valid = False
    all_numbers = True

    while not valid:
        x = input("Number of standard: ")
        all_numbers = True

        for i in range(len(x)):
            if not (ord(x[i]) >= 48 and ord(x[i])<=57):
                all_numbers=False
            
        if all_numbers:
            if (int(x) > 0) and (int(x) <= len(menu1)):
                valid = True

    x = int(x)-1

    standard = menu1[x]

    print(f"You have chosen the {standard} standard.")

    print("Which data rate would you like to use?")

    for i, dr in enumerate(menu2):
        print(f"{i+1}. {dr}")

    valid = False
    all_numbers = True

    while not valid:
        x = input("Number of Data Rate: ")
        all_numbers = True

        for i in range(len(x)):
            if not (ord(x[i]) >= 48 and ord(x[i])<=57):
                all_numbers=False
            
        if all_numbers:
            if (int(x) > 0) and (int(x) <= len(menu2)):
                valid = True
                
    dr = int(x)-1

    data_rating = menu2[dr]

    print(f"You have chosen the {data_rating} data rate.")

    print("Which protocol would you like to use?")

    for i, prot in enumerate(menu3):
        print(f"{i+1}. {prot}")

    valid = False
    all_numbers = True

    while not valid:
        x = input("Number of Protocol: ")
        all_numbers = True

        for i in range(len(x)):
            if not (ord(x[i]) >= 48 and ord(x[i])<=57):
                all_numbers=False
            
        if all_numbers:
            if (int(x) > 0) and (int(x) <= len(menu2)):
                valid = True
                
    x = int(x)-1

    protocol = menu3[x]

    print(f"You have chosen the {protocol} protocol.")

    routine = None
    best_routine=None

    if standard == menu1[0]:
        routine = a()

    elif standard == menu1[1]:
        routine = g()

    elif standard == menu1[2]:
        routine = n()
        best_routine = n_best()

    elif standard == menu1[3]:
        routine = ac_w1()
        best_routine = ac_w1_best()

    elif standard == menu1[4]:
        routine = ac_w2()
        best_routine = ac_w2_best()

    elif standard == menu1[5]:
        routine = ax()
        best_routine = ax_best()
    
    else:
        print(f"Options not found.")
    
    routine.setup(protocol, data_rating)

    tf_time = routine.time_to_transfer(15e9)

    throughput = routine.get_throughput(Packet().get_size())

    if not (best_routine == None):
        best_routine.setup(protocol, data_rating)

        best_tf_time = best_routine.time_to_transfer(15e9)

        best_throughput = best_routine.get_throughput(Packet().get_size())

    print(len(f"Time to Transmit in the best Case 15 x 10^9 Bytes: {best_tf_time:.2f} seconds")*'=')

    print(f"Standard: {routine.name}")

    print(f"Protocol: {routine.protocol}")

    print(f"Actual MAC Throughput: {throughput/1e6:.2f} Mb/s")
    
    if not (best_routine == None):
        print(f"Actual MAC Throughput Best Case: {best_throughput/1e6:.2f} Mb/s")

    print(f"Time to Transmit 15 x 10^9 Bytes: {tf_time:.2f} seconds")
    
    if not (best_routine == None):
        print(f"Time to Transmit in the best Case 15 x 10^9 Bytes: {best_tf_time:.2f} seconds")

    print(len(f"Time to Transmit in the best Case 15 x 10^9 Bytes: {best_tf_time:.2f} seconds")*'=')
    


if __name__ == "__main__":
    # print(a().get_throughput(1500), 'bits/second')

    main()