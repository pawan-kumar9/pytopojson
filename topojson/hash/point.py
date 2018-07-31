
import struct


def to_bin(value):
    if type(value) == str:
        b = ''.join(map(bin, bytearray(value))).replace('0b', '')[:64]
        return b if len(b) == 64 else b.zfill(64)
    else:
        return float_to_bin(value)


def float_to_bin(value):
    """ Convert float to 64-bit binary string. """
    [d] = struct.unpack(">Q", struct.pack(">d", value))
    return '{:064b}'.format(d)


def bin_to_uint(value):
    return int(value, 2)


def hash(point):
    bins = [to_bin(point.keys()[0]), to_bin(point.values()[0])]
    uints = [bin_to_uint(bins[0][:32]), bin_to_uint(bins[0][32:]),
             bin_to_uint(bins[1][:32]), bin_to_uint(bins[1][32:])]
    h = uints[0] ^ uints[1]
    h = h << 5 ^ h >> 7 ^ uints[2] ^ uints[3]
    return h & 0x7fffffff


def equal(p_1, p_2):
    return p_1.keys()[0] == p_2.keys()[0] and p_1.values()[0] == p_2.values()[0]