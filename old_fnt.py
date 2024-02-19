def get_rq_name_values(file):
    # Gets the first vars and values for file to work properly.
    with open(file,'rb+') as of:
        data = of.read()
        of.seek(0x38)
        size_val = of.read(1)
        of.seek(0x44)
        padd_val = of.read(1)
        f_offset = data.find(b'mc_10')
        of.seek(f_offset+5)
        if b'_' in of.read(0x01):
            of.seek(f_offset)
            name = of.read(0x08)
            bits = 9
        else:
            of.seek(f_offset)
            name = of.read(0x05)
            bits = 6

        of.seek(f_offset + bits)
        ff = of.read(0x06)

        print(ff) # Can be any var found (for font stuff)

file = 'mc_10_cn.bjson'
get_rq_name_values(file)
