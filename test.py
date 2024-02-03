from pathlib import Path
from main import extract_chunk

filepath = Path("es_MX-pocket.blang")
with open(filepath, "rb") as f:
    data_bytes = f.read()

to_print = []
to_loop = int.from_bytes(extract_chunk(data_bytes, 0), "little", signed=False)
for i in range(to_loop):
    idx = i * 2 + 1
    #for j in range(2):
        #to_print.append(int.from_bytes(extract_chunk(data_bytes, idx + j), "little", signed=False))
    to_print.append(int.from_bytes(extract_chunk(data_bytes, idx), "little", signed=False))

#print(to_print)
differences = []
for i in range(1, len(to_print)):
    try:
        differences.append(to_print[i] - to_print[i - 1])
    except:
        print("missing one more quantity")

print(differences)