import struct


class Bitmap:
    """
    This class is used to generate Bitmap and transform the bitmap into bytes array
    """
    def cal_element_index(self, num):
        return int(num / 32)

    def cal_bit_index(self, num):
        return num % 32

    def __init__(self):
        self.size = self.cal_element_index(1024)
        self.array = [0 for i in range(self.size)]

    def set(self, row, col):
        element = self.array[row]
        self.array[row] = element | (1 << (32-col-1))

    def clean(self, row, col):
        row = row - 1
        element = self.array[row]
        self.array[row] = element & (~(1 << (32-col-1)))

    def check_one(self, row, col):
        row = row - 1
        if self.array[row] & (1 << (32-col-1)):
            return True
        return False

    def to_bit_map_array(self):
        result = []
        for element in self.array:
            result.append(struct.pack('!I', element))
        return b''.join(result)



