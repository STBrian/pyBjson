# pyBjson
pyBjson is the first modding Python module able to convert BJSON files fully and successfully to JSON and vice versa.

# What is a BJSON?
A BJSON file is the binary form of a JSON file, that is used in MC3DS Edition.

# Structure of a BJSON
## JSON Structure
This is where the JSON structure is defined.
Each JSON element is represented by 12 bytes.
The first 4 bytes (uint 32-bits) represents the length in objects that the structure has.
Next, all objects are listed in the same order that they were in the original JSON.
The known data types used are the next ones.

### Base structure
```
uint32      4 bytes     4 bytes
Data type   Value 1     Value 2
```
### Specific structures
#### null
```
uint32  uint32  uint32
0       0       0
```
#### Boolean
```
uint32  uint32              uint32
1       (0|1)=(false|true)  0
```
#### Integer
```
uint32  int32   uint32
2       Value   0
```
#### Float
```
uint32  float32 uint32
3       Value   0
```
#### Array
```
uint32  uint32  uint32
4       Lenght  Objects in previous arrays
```
Objects in previous arrays are the amount of previous array objects at the time the current array was closed.
#### String
```
uint32  uint32  uint32
5       Hash    String start position
```
String start position is where the string starts in the strings file section.
#### Object
```
uint32  uint32  uint32
6       Lenght  Objects in previous objects
```
Objects in previous objects is the same as Arrays but applied to Objects
## Strings
In this section are all the string values used in the JSON structure, it doesn't include header strings.
Strings are ended with null character.
The first 4 bytes (uint 32-bits) in the section represents the length in bytes of the section.
## Arrays indexes
In this section are all of the Arrays indexes used in the JSON structure. They appear in the same order as the Array was closed.
Elements in this section are represented by one uint 32-bits, that represent the absolute index of the element in the whole JSON structure.
The first 4 bytes (uint 32-bits) in the section represents the length in elements that this section has.
## Key strings
In this section are stored all the keys strings used in the JSON structure.

For example, if you have the following JSON:
```
{
    "my_number": 2
}
```
"my_number" will be stored in this section.
The main purpose of this section is to be able to search for keys efficiently in the JSON structure.
Each element has a similar structure of the strings data type.
#### Key structure
```
uint32  uint32  uint32
Index   Hash    String start position
```
Where index is the absolute element index in the whole JSON structure. Hash self-explanatory. String start position where the string starts in the last section of the file, the keys strings section.
The elements are grouped as their object was closed as the array indexes value, but with the addition that they are sorted by their hash.
The first 4 bytes (uint 32-bits) represents the length in elements of the section.
## Keys strings
This section works the same as the normal strings section, the only thing different is that this section stores the key strings insted of value strings.
Each string is ended by null character.
The first 4 bytes (uint 32-bits) represents the length in bytes of the section.
# Notes
- To generate hashes a 32-bits JOAAT algorithm is used with the lowered string.
- If an object or array is empty, then it's 3rd value must be 0.
