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

def convert_file(in_name, out_name):
    dist = [0] * 257

    i = 7
    remainder = 0
    moved_bytes = []
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
                moved_bytes.append(remainder.to_bytes(1, 'big'))
                #out_file.write(remainder.to_bytes(1, 'big'))
                remainder = 0
                #d -= 1
            #if d == 0:
                #break

            byte = f.read(1)

        # Write the remainder bytes at the end of the file
        for b in moved_bytes:
            out_file.write(b)

        if i > 0:
            if debug_print: print("Ended Early!", 'remainder', remainder, " ----- ", remainder.to_bytes(1, 'big'), ord(remainder.to_bytes(1, 'big')))
            out_file.write(remainder.to_bytes(1, 'big'))

    print(dist)



def compress(in_name, out_name):
    counter = 1 # Set to 1 because this means that 2 bytes have been found that match
    compressions = 0
    bytes_compressed = 0
    with open(in_name, "rb") as f, open(out_name, "wb") as out_file:
        compare_byte = f.read(1)
        byte = f.read(1)
        while byte:
            if compare_byte == byte:
                counter += 1
            else:
                # If we no longer find a byte that matches, and the counter is at 2 more
                # Store the number of bytes we can compress, and how many times total we compressed
                if counter > 1:
                    compressions += 1
                    bytes_compressed += counter
                    a = 255
                    out_file.write(a.to_bytes(1, 'big'))  # TODO: this would be the compression_bit
                    out_file.write(compare_byte)
                else:
                    # The bytes did not match, and we did not have at least "2" matching bytes
                    # So, write the byte, and move on
                    out_file.write(compare_byte)

                counter = 1

            compare_byte = byte
            byte = f.read(1)



    print("compressions", compressions)
    print("bytes_compressed", bytes_compressed)


def compress_pattern(in_name, out_name, items=2):
    #print("Attempting compression with pattern of " + str(items) + " items")
    #print(in_name, out_name)
    compressions = 0
    bytes_compressed = 0
    working_bytes = []
    with open(in_name, "rb") as f, open(out_name, "wb") as out_file:
        for i in range(0, items):
            working_bytes.append(f.read(1))

        pattern = working_bytes.copy()

        counter = 0 # for pattern
        file_empty = False
        while not file_empty:
            if working_bytes == pattern:
                counter += 1
                # Update the pattern to the current working_bytes
                # pattern = working_bytes.copy() # they are the same, we don't need to do this

                working_bytes = []
                for i in range(0, items):
                    byte = f.read(1)
                    if not byte:
                        file_empty = True
                        break
                    working_bytes.append(byte)
            else:
                # If we no longer find a byte that matches, and the counter is at 2 more
                # Store the number of bytes we can compress, and how many times total we compressed
                if counter > 1:
                    compressions += 1
                    bytes_compressed += (counter * items) - 1
                    a = 255
                    out_file.write(a.to_bytes(1, 'big'))  # TODO: this would be the compression_bit information

                    # Testing 2 byte pattern
                    for b in pattern:
                        out_file.write(b)

                    #print(pattern)
                    # Reset pattern to new pattern found in working_bytes
                    # Load new N bytes from file to compare against
                    pattern = working_bytes.copy()
                    working_bytes = []
                    for i in range(0, items):
                        byte = f.read(1)
                        if not byte:
                            file_empty = True
                            break
                        working_bytes.append(byte)

                else:
                    # The bytes did not match, and we did not have at least "2" matching bytes
                    # So, write the byte, and move on
                    #out_file.write(compare_byte)
                    #for b in pattern:
                    #    out_file.write(b)

                    # if the 15 bytes pattern doesn't match the next 15 bytes
                    # Write the first byte from the pattern via pop(0)
                    b = pattern.pop(0)
                    out_file.write(b)

                    # Shift the first byte from the working_bytes to the end of pattern with append
                    b = working_bytes.pop(0)
                    pattern.append(b)

                    # Read a new byte and append it to the end of working_bytes
                    byte = f.read(1)
                    if not byte:
                        file_empty = True
                    working_bytes.append(byte)

                counter = 1


        if counter > 1:
            compressions += 1
            bytes_compressed += (counter * items) - 1
            a = 255
            out_file.write(a.to_bytes(1, 'big'))  # TODO: this would be the compression_bit
            # out_file.write(compare_byte)

            # Testing n byte pattern
            for b in pattern:
                out_file.write(b)

        else:
            # The bytes did not match, and we did not have at least "n" matching bytes
            # So, write the bytes, and move on

            for b in pattern:
                out_file.write(b)

        # need to write any remaining bytes captured
        for b in working_bytes:
            out_file.write(b)

    if compressions > 0:
        print("Attempting compression with pattern of " + str(items) + " items")
        print(in_name, out_name)

        print("compressions", compressions)
        print("bytes_compressed", bytes_compressed)


# Skip over N bytes to look for the next matching pattern
def skip_compress(in_name, out_name, items, skip_bytes):
    compressions = 0
    bytes_compressed = 0
    working_bytes = []
    skip_buffer = []  # Place to store extra bytes to "skip" ahead"
    with open(in_name, "rb") as f, open(out_name, "wb") as out_file:
        for i in range(0, items):
            working_bytes.append(f.read(1))

        pattern = working_bytes.copy()

        counter = 0 # for pattern
        file_empty = False
        while not file_empty:
            if working_bytes == pattern:
                counter += 1
                # Update the pattern to the current working_bytes
                # pattern = working_bytes.copy() # they are the same, we don't need to do this

                # Read in the next N bytes to skip over and store in the skip buffer
                for s in range(0, skip_bytes):
                    skip_buffer.append(f.read(1))

                working_bytes = []
                for i in range(0, items):
                    byte = f.read(1)
                    if not byte:
                        file_empty = True
                        break
                    working_bytes.append(byte)

            else:
                # If we no longer find a byte that matches, and the counter is at 2 more
                # Store the number of bytes we can compress, and how many times total we compressed
                if counter > 1:
                    compressions += 1
                    bytes_compressed += (counter * items) - 1
                    a = 255
                    out_file.write(a.to_bytes(1, 'big'))  # TODO: this would be the compression_bit information

                    # Write pattern that will be interleaved into the skip_buffer that is written afterwards
                    for b in pattern:
                        out_file.write(b)

                    # Write out all the bytes we've been compiling from the skip buffer
                    # Minus the last "N" where n is the number of skip bytes
                    # Leaving skip_buffer at skip_bytes items
                    for i in range(0, len(skip_buffer) - skip_bytes):
                        b = skip_buffer.pop(0)
                        out_file.write(b)

                    # Reset pattern to new pattern found in working_bytes
                    # Load new N bytes from file to compare against
                    # Minus the number of bytes in the skip_buffer
                    pattern = skip_buffer.copy()
                    for i in range(0, len(working_bytes) - skip_bytes):
                        pattern.append(working_bytes.pop(0))

                    # Read in skip bytes (Pattern - Skip - Working)
                    # working_bytes should now contain only "skip_bytes" amount of bytes
                    # This becomes the new skip_buffer
                    skip_buffer = working_bytes.copy()

                    # Load the next N bytes to check of a pattern after skip_buffer
                    working_bytes = []
                    for i in range(0, items):
                        byte = f.read(1)
                        if not byte:
                            file_empty = True
                            break
                        working_bytes.append(byte)



                else:
                    # The bytes did not match, and we did not have at least "2" matching bytes
                    # So, write the byte, and move on
                    #out_file.write(compare_byte)
                    #for b in pattern:
                    #    out_file.write(b)

                    # if the 15 bytes pattern doesn't match the next 15 bytes
                    # Write the first byte from the pattern via pop(0)
                    b = pattern.pop(0)
                    out_file.write(b)

                    # Shift the first byte from the skip_buffer to the end of the pattern with append
                    b = skip_buffer.pop(0)
                    pattern.append(b)

                    # Shift the first byte from the working_bytes to the end of skip_buffer with append
                    b = working_bytes.pop(0)
                    skip_buffer.append(b)

                    # Read a new byte and append it to the end of working_bytes
                    byte = f.read(1)
                    if not byte:
                        file_empty = True
                    working_bytes.append(byte)

                counter = 1


        if counter > 1:
            compressions += 1
            bytes_compressed += (counter * items) - 1
            a = 255
            out_file.write(a.to_bytes(1, 'big'))  # TODO: this would be the compression_bit
            # out_file.write(compare_byte)

        for b in pattern:
            out_file.write(b)

        # need to write any remaining bytes in skip
        for b in skip_buffer:
            out_file.write(b)

        # need to write any remaining bytes captured
        for b in working_bytes:
            out_file.write(b)

    if compressions > 0:
        print("Compression by skipping " + str(skip_bytes) + " bytes with " + str(items) + " items")
        print(in_name, out_name)

        print("compressions", compressions)
        print("bytes_compressed", bytes_compressed)


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

#convert_file('file1.exe', 'outfile1.exe')
filename = 'img_256' # file
fileext = '.bmp' # .exe
convert_file(filename + fileext, 'working/' + filename + '0' + fileext)
compress('working/' + filename + '0' + fileext, 'working/' + filename + '16' + fileext)

previous_file = 'working/' + filename + '16' + fileext
for i in range(15, 1, -1):
    compress_pattern(previous_file, 'working/' + filename + str(i) + fileext, i)
    previous_file = 'working/' + filename + str(i) + fileext

previous_file = 'working/' + filename + '2' + fileext
for i in range(15, 1, -1):
    for j in range(1, 10):
        skip_compress(previous_file, 'working/' + filename + str(i) + "_" + str(j) + fileext, i, j)
        previous_file = 'working/' + filename + str(i) + "_" + str(j) + fileext

#decompress('outfile.exe', 'revert.exe')