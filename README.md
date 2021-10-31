# compress1d
Compress binary files as a 1D array

## Overview
This program is an attempt at creating my own Compression program.

The basic logic will be to look for 1 or more consecutive bytes that are the same.  They will all but 1 be removed and a counter used for how many times we need to put that byte back.

### Example: 
Say a program has the following bytes:  `agh4s6sdsssssdshjhhhh43`

The compressed program would become: `agh4s6(s5)dshj(h4)43`

This isn't the real way the bytes are compressed or stored, but it provides a good interpretation.

## Logic
We need a way to store the compression meta data.  For instance, how do we store that we want to compress sssss into a single s, that will be expanded 5 times?

We can't just say s5 or 5s because those are both valid results in a file.

Instead we have to have something in the file that we know always means "Replicate this value N times"

To do this we need some bits or bytes to work with.

1. Convert every 7 bytes into 8 bytes (Yes, we expand first)
1. The first bit of each byte is stripped off of those first 7 bytes.
1. That first bit is used to create the new 8th byte with its 7 bits.
1. The first bit is then reserved as our "key"
1. If the first bit is a 1, then that whole byte is our encoding logic byte
  - assumes bit 1 is on the LEFT and bit 8 is on the RIGHT
  - bit 1: 0 = normal byte, 1 = Encoding Logic byte
  - bit 2/3/4: How many times do we replicate this byte? (000 = 1, 111 = 8)
  - bit 5/6: What type of series is this? 
    - 00 = addition
    - 01 = power
    - 10 = Fibonacci sequence
    - 11 = reserved
    - Meaning if we set this to 01, and 7/8 is set to 11, then we skip by i^3, where i is the number of bytes written so far
  - bit 7/8: How many places do we skip (00 means don't skip bytes,)
1. The next byte is the 7 bit value that is replicated, if and only if the previous byte has a 1 in the most significant bit

## Compressing

1. The entire file is first converted to the 7 bit byte structure.  This allows us to find consecutive bytes that match, and make sure we have the ability to add in our Logic Byte.
1. Compression is done almost like absorbing the bytes from right <- left
1. Start at beginning of file, look for matching consecutive bytes.
1. When 3 or more are found, this is our Compression Byte:
  - Create a Logic Byte with the appropriate rules (How many consecutive were found, what type of series to use) 
  - Remove all consecutive bytes, write the Logic Byte followed by the Compression Byte, but with a 1 bit-wise or'd to it so the most significant bit is a 1.
1. This is done over and over until the entire file is looked through for all manner of series.
1. Any Bytes found that are not compressible, are written to the file as as the "7-bit" byte format.

A completely random file that is completely incompressible would actually increase in size instead of shrink.

## Expanding

1. Work is done from the end of the file in this case.
1. Each byte is read until we find a byte with the most significant bit set to 1.
1. Once we find this byte, this is the Compression Byte that stores the VALUE we need to replicated
1. We then look backwards 1 more byte to find the Logic Byte, that tells us how to replicate the Compression Byte.
1. We expand the Compression Byte (without a 1 in it's most significant bit)
1. Then we remove the Logic Byte, and repeat looking backwards for the next byte with a 1 in the most significant position.


## Ways to compress

Currently with this 1D solution, the only ways to compress would be

Linear: aaaaaaaaaabbbbbbbcccccccc could be compressed into 10a7b8c (Using symbolic representation of the format)
Linear Steped: abacadakaiahanaaaoakahy could be compressed to (2)11abcdkihnaokhy
Etc

## Changes to stucture

Putting the stripped off significant bit into a new "7-bit" 8th byte may be convinent, but the position of that can create issues for increased compression performandce.

Imagine you have 16 characters `AAAAAAAAAAAAAAAA` this would end up needing to be split into 3 different compressions, because it's unlikely the 7 bits from the top most would match the sequence of A.

To resolve this, the 7-bit bytes could be instead put at the end of the file as a seperate chunk, still compressible, but just not interweaved into the existing possible compressble bytes.

N