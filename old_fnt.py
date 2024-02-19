import json, os, sys

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
            name = of.read(0x08).decode('utf-8')
            bits = 9
        else:
            of.seek(f_offset)
            name = of.read(0x05).decode('utf-8')
            bits = 6

        padd_val = int.from_bytes(padd_val, byteorder='big')
        size_val = int.from_bytes(size_val, byteorder='big')
        of.seek(f_offset + bits)
        ff = of.read(0x06).decode('utf-8')

        return {
            ln0: [{
                r0: name,
                r1: size_val,
                r2: padd_val,
                r3: ff,
                ln1: []
            }]
        }

file = 'mc_10_cn.bjson'
with open(f'{file.replace('.bjson','_newerest_biggerer.json')}', 'w') as f0:
    json_data = json.dump(get_rq_name_values(file), f0, indent=4)
