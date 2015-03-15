import sys

# This decryps using pre-generated RC4 key bitstream

key = open('xorkey').read()

enc = open(sys.argv[1]).read()

for i, c in enumerate(enc):
    sys.stdout.write(chr(ord(c)^ord(key[i])))
