import numpy

import numpy as np

arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
## arr = np.random.randint(0, 255, (8*8*8))    # random numpy array of shape (4,5)
# arr = np.random.randint(0, 255, (100))    # random numpy array of shape (4,5)
# newarr = arr.reshape(8, 8, 8)

#print(newarr)

# z, y, x
# print(" -z, y , x- ")
# print("bottom", newarr[0, 0, 0])
# print("next level", newarr[1, 0, 0])
# print("bottom, down one", newarr[0, 1, 0])
# print("bottom right one", newarr[0, 0, 1])

# Look for vertical columns in Z that match with 3 or more
# Look for rows in y that match with 3 or more
# Look for rows in x that match with 3 or more

#for z in range(0, 8):

# attempt 1D first

debug_print = False

def compress(in_name, out_name):
    dist = [0] * 257

    i = 7
    remainder = 0
    with open(in_name, "rb") as f, open(out_name, "wb") as out_file:
        byte = f.read(1)

        while byte:
            # Do stuff with byte.
            dist[ord(byte)] += 1
            eight_bit = ord(byte) >> 7
            remainder = remainder | eight_bit << i
            if debug_print: print("Byte", byte, "ord", ord(byte), " -- Eight_bit ", eight_bit, " -- Remainder ", remainder)
            i -= 1

            # Strip first bit
            seven_bit = ord(byte) & 127
            out_file.write(seven_bit.to_bytes(1, 'big'))
            if debug_print: print('7-bit byte', seven_bit)

            if i == 0:
                i = 7
                if debug_print: print('remainder', remainder, " ----- ", remainder.to_bytes(1, 'big'), ord(remainder.to_bytes(1, 'big')))

                out_file.write(remainder.to_bytes(1, 'big'))
                remainder = 0
                #d -= 1
            #if d == 0:
                #break

            byte = f.read(1)

        if i > 0:
            if debug_print: print("Ended Early!", 'remainder', remainder, " ----- ", remainder.to_bytes(1, 'big'), ord(remainder.to_bytes(1, 'big')))
            out_file.write(remainder.to_bytes(1, 'big'))

    print(dist)


def decompress(in_name, out_name):
    dist = [0] * 257
    value = 4

    i = 7
    d = 2
    remainder = 0
    eight_bytes = []
    with open(in_name, "rb") as f, open(out_name, "wb") as out_file:
        byte = f.read(1)

        while byte:
            eight_bytes.append(byte)
            i -= 1

            if i == -1:
                i = 7
                # Re-Build the original bytes

                # loop over bytes taking ith bit from the 8th byte
                for b in range(0, 7):
                    if debug_print: print(eight_bytes[b], " -- ", ord(eight_bytes[7]) , " -- ", (ord(eight_bytes[7]) << b) & 128, " -- ", ord(eight_bytes[b]) | (ord(eight_bytes[7]) << b) & 128)

                    remainder = (ord(eight_bytes[7]) << b) & 128
                    eight_bytes[b] = ord(eight_bytes[b]) | remainder
                    out_file.write(eight_bytes[b].to_bytes(1, 'big'))

                eight_bytes = []

            byte = f.read(1)

        # Ended early
        if i >= 0 and i < 7:
            if debug_print: print("Ended Early")
            if debug_print: print(eight_bytes)

            # loop over bytes taking ith bit from the 8th byte
            end_byte = len(eight_bytes) - 1
            for b in range(0, end_byte):
                if debug_print: print(eight_bytes[b], " -- ", ord(eight_bytes[end_byte]), " -- ", (ord(eight_bytes[end_byte]) << b) & 128, " -- ", ord(eight_bytes[b]) | (ord(eight_bytes[end_byte]) << b) & 128)

                remainder = (ord(eight_bytes[end_byte]) << b) & 128
                eight_bytes[b] = ord(eight_bytes[b]) | remainder
                out_file.write(eight_bytes[b].to_bytes(1, 'big'))

# structure is

# all bytes are stripped of their first bit
# Meaning a byte of 11010101
# becomes a byte of 01010101
# and the "1" from the front is used to create a new byte after the first 7 "7-bit" bytes
# Issue#1 the new 7-bit byte would interrupt any patterns that might exist
# fix#1 perhaps these 7 bit byte sequences are put at the end of the file and seperatly attempted to be compressed

# A converted but uncompressed file would look like this, where every first bit of a byte is a zero [0]
# Original:  11111111 11010101 01110101 00011011 01110100 10000110 11100101 ########
# Converted: 01111111 01010101 01110101 00011011 01110100 00000110 01100101 01100011

# File size of converted but uncompressed size is (BYTES / 7) * 8
# 7 / 7 * 8 = 8
# 14 / 7 = 2 * 8 = 16
# File with 31,772,640 bytes
# becomes:  36,311,589 bytes
# Essentially 4,538,948 more bytes

# This means we have to come up with a compression ratio of at least 13% to save any space at all
# Using an example EXE binary, (r5apex.exe [Apex Legends exe])
# It ends up at 28,791,033 bytes compressed, a 10% compression

#compress('file1.exe', 'outfile1.exe')
#decompress('outfile1.exe', 'revert1.exe')

compress('file.exe', 'outfile.exe')
decompress('outfile.exe', 'revert.exe')