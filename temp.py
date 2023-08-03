import random

class SRAM:
    def __init__(self, size):
        self.memory = [0] * size

    def read(self, address):
        return self.memory[address]

    def write(self, address, value):
        self.memory[address] = value

class Seq_Buff:
    def __init__(self, size):
        self.memory = [0] * size

    def read(self, address):
        return self.memory[address]

    def write(self, address, value):
        self.memory[address] = value

def main():
    sram = SRAM(1024)
    sram.name = "Welcome_Buff"

    seq_buff = Seq_Buff(1024)
    seq_buff.name = "Seq_Buff"

    for i in range(1024):
        address = random.randint(0, 1023)
        value = chr(random.randint(0, 255))
        sram.write(address, value)
        seq_buff.write(address, value)

    for i in range(1024):
        address = random.randint(0, 1023)
        value = sram.read(address)
        print("address:", address, "value:", value)
        hashed_key = hash64(value)
        value = seq_buff.read(hashed_key)
        print("address:", address, "value:", value)

if __name__ == "__main__":
    main()
