import numpy as np

class Packet:
    def __init__(self):
        self.size = 1500 * 8; # bits

    def get_size(self):
        return self.size

class Header:
    def __init__(self):
        # a and g total size is 1542
        # n, ac, ax total size = 1548
        self.packet = Packet();

        self.MAC_header = 34 * 8; # bits

        self.SNAP_LLC = 8 * 8; # bits

    def get_size(self):
        return self.packet.get_size() + self.MAC_header + self.SNAP_LLC;

    def add_MAC_bytes(self, extra):
        # Add 40 for n, ac and ax.

        # Set bytes to bits.
        extra_bits = extra*8
        self.MAC_header = self.MAC_header + extra_bits;

    def add_SNAP_bytes(self, extra):
        # Add 8 for ac, ax and an.
        # Set bytes to bits.
        extra_bits = extra*8
        self.SNAP_LLC = self.SNAP_LLC + extra_bits;

    def set_n_ac_ax(self):
        self.add_MAC_bytes(40);

        self.add_SNAP_bytes(8);

class ACK:
    def __init__(self):
        self.header_info = 40*8; # bits

class DataRate:
    def __init__(self, modulation, NBits, CRate, NChan, SDur, Data_Rate):
        self.modulation = modulation

        self.NBits = NBits;

        self.CRate = CRate;

        self.NChan = NChan;

        self.SDur = SDur;

        self.data_rate = Data_Rate; # Mbps

    
class a:
    def __init__(self):
        self.name = "802.11a";

        self.header = Header();

        self.SIFS = 16E-6; # seconds

        self.slot = 9E-6; # seconds

        self.DIFS = (2*self.slot) + self.SIFS

        self.max_dr = 54E6; # bps

        self.symbol_tx_time = 4E-6; # seconds

        self.ofdm_tail=0;

        # if use_ofdm:
        #     self.ofdm_tail = 6;

        self.rts_size = 20*8; # bits

        self.cts_size = 14*8; # bits

        self.ack_size = 14*8; # bits

        self.preamble = 20E-6; # mu s

        # Used Packet Size instead.
        # self.data_size = 1500; # Bytes.

        self.data_rates = [DataRate("BPSK", 1, 1/2, 48, 4E-6, 6E6), DataRate("64-QAM", 6, 3/4, 48, 4E-6, 54E6)];

    def set_OFDM(self):
        self.ofdm_tail = 6; # bits

    def get_ofdm_symbols(self):
        # header_bytes = self.header.get_size();

        # header_bits = header_bytes * 8;
        
        header_bits= self.header.get_size();
        
        ofdm_bits = header_bits + self.ofdm_tail;

        ofdm_symbols = np.ceil(ofdm_bits / self.bits_per_ofdm_symbol());

        return ofdm_symbols;
    
    def bits_per_ofdm_symbol(self, verbose=False):
        bps = self.data_rates[1].NBits * self.data_rates[1].CRate * self.data_rates[1].NChan; # b/symbol
        
        if verbose:
            print(f"Bits per ofdm Symbol: {bps}")
            
        return bps

    def frame_transmit_time(self):
        return self.get_ofdm_symbols() * self.symbol_tx_time;

    def rts_tx_time(self):
        return self.symbols_to_tx_time(self.bits_to_symbols((self.rts_size)+6))

    def cts_tx_time(self):
        return self.symbols_to_tx_time(self.bits_to_symbols((self.cts_size)+6))

    def ack_tx_time(self):
        return self.symbols_to_tx_time(self.bits_to_symbols(self.ack_size))

    def data_rate(self):
        return (1/self.SDur) * (self.bits_per_ofdm_symbol())

    def bits_to_symbols(self, bit_count):
        return np.ceil(bit_count / self.bits_per_ofdm_symbol())

    def bytes_to_symbols(self, byte_count):
        return self.bits_to_symbols(byte_count*8)

    def symbols_to_tx_time(self, symbol_count):
        return symbol_count * self.symbol_tx_time;

    def tx_data_time(self, verbose = False):
        tx_time = self.symbols_to_tx_time(self.bits_to_symbols((self.header.get_size()*8)+6));

        if verbose:
            print(f"Time to Transmit Data: {tx_time}")
        
        return tx_time

    def time_to_send(self):
        return self.DIFS + self.preamble + self.rts_tx_time() + self.SIFS + self.preamble + self.cts_tx_time() + self.SIFS +self.preamble + self.tx_data_time(verbose=True) + self.SIFS + self.preamble + self.ack_tx_time();

    def get_throughput(self, bits):
        return bits / self.time_to_send()

    def time_to_transfer(self, bits):
        return bits / self.get_throughput(1500*8)

menu1 = ["802.11a", "802.11g", "802.11n", "802.11ac_w1", "802.11ac_w2", "802.11ax"]

menu2 = ["Minimum", "Maximum"]

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

    dr = int(x)-1

    data_rate = menu2[dr]

    print(f"You have chosen the {data_rate} data rate.")

    print("Which protocol would you like to use?")

    for i, prot in enumerate(menu3):
        print(f"{i+1}. {prot}")

    x = input("Number of Protocol: ")

    x = int(x)-1

    protocol = menu3[x]

    print(f"You have chosen the {protocol} protocol.")

    routine = None;

    if standard == menu1[0]:
        routine = a();

    elif standard == menu1[1]:
        routine = g();

    elif standard == menu1[2]:
        routine = n();

    elif standard == menu1[3]:
        routine = ac_w1();

    elif standard == menu1[4]:
        routine = ac_w2();

    elif standard == menu1[5]:
        routine = ax();
    
    else:
        print(f"Options not found.")
    
    print(f"Time needed to transfer 15 x 10 9 bytes of data for {routine.name} @ {routine.data_rates[dr]} using {protocol}:")

    print(f"{routine.time_to_transfer(15e6)}")


if __name__ == "__main__":
    print(a().get_throughput(1500*8))
    main()