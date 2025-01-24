# pyBjson
Un archivo BJSON es en escencia la forma binaria de un JSON usado en MC3DS Edition

# Estructura
## Estructura JSON
La primera parte del archivo es donde se define la estructura JSON, donde cada elemento se representa por un conjunto de 3 números enteros de 32 bits.

Antes inicia con un entero de 32 bits que representa la longitud de objetos que posee la estructura. Seguido de eso ya vienen los objetos en orden de la estructura original del archivo JSON.

Los tipos de datos que puede contener son los siguientes, includia su estructura.

### Estructura base
```
int32       int32       int32
Data type   Value 1     Value 2
```
### Estructuras especificas
#### Nulo - null
```
int32   int32   int32
0       0       0
```
#### Booleano - boolean
```
int32   int32               int32
1       (0|1)=(false|true)  0
```
#### Entero - integer
```
int32   int32   int32
2       Value   0
```
#### Flotante - float
```
int32   flt32   int32
3       Value   0
```
#### Array
```
int32   int32   int32
4       Lenght  Objects in previous arrays
```
Objects in previous arrays se refiere a la cantidad de objetos que hay en arrays anteriores al momento en el que se cierra un array
#### Cadena de texto - string
```
int32   int32   int32
5       Hash    String start position
```
String start position representa la posición en la que la cadena de texto inicia dentro de la siguiente sección del archivo, que es una sección que contiene todos los textos usados en la estructura, terminados con el caracter nulo
#### Objecto - object
```
int32   int32   int32
6       Lenght  Objects in previous objects
```
Objects in previous objects se refiere a la cantidad de objetos que hay en objetos anteriores al momento en el que se cierra un objeto
## Cadenas de texto
En esta sección se agrupan todas las cadenas de texto usadas en el archivo BJSON que se guardan como valores, eso significa que no incluye el texto de las cabeceras, las cuales se encuentran en otra sección.

Las cadenas de texto están terminadas por el caractér nulo.

La sección inicia con un entero de 32 bits que representa la cantidad de caracteres totales en la sección. Seguido se encuentran las cadenas de texto.
## Índices de arrays
En esta sección se encuentran todos los índices de los elementos que se encuentran en un array, se encuentran agrupados según el orden en el que se hayan cerrados los arrays, lo que significa que primero van a estar los índices del primer array que haya estado y se haya cerrado primero en el archivo JSON.

Los elementos de esta sección están representados por un solo entero de 32 bits que representa el índice del elemento en la estructura, este índice se obtiene según el orden en el que haya aparecido en el JSON y es absoluto respecto a todos los demás elementos del JSON, significa que no habrán índices repetidos en esta sección nunca

La sección inicia, como en las demás, con un entero de 32 bits que representa la cantidad de índices que hay en total, en la sección.
## Key values
En esta sección se encuentran definidas todos los key values o cabeceras.

Es decir, si tienes en un JSON:
```
{
    "my_number": 2
}
```
"my_number" estará definido en esta sección.

El propósito de esta sección es la búsqueda rápida de información mediante el uso de keys.

Cada key tiene una estructura parecida a la de una cadena de texto:
#### Key structure
```
int32   int32   int32
Index   Hash    String start position
```
Donde el índice sigue las mismas reglas de la sección anterior, hash es el protagonista de esta sección, y String start position funciona igual que en la sección de estructura, con diferencia que ahora el texto se busca en la siguiente sección.

La búsqueda de valores mediate keys se realiza usando el hash de la cadena de texto, ya que es más rápido comparar dos enteros que dos cadenas de texto. Por eso es importante el hash aquí.

Además, los keys se agrupan de igual forma que en la sección anterior, con una adición, y es que dentro de cada grupo los keys se tienen que ordenar de menor a mayor según su valor de hash. Lo cual está relacionado con algoritmos de búsqueda más eficientes.

La sección inicia con un entero de 32 bits que representa la cantidad de keys que contiene la sección
## Cadenas de texto para keys
Esta sección tiene las mismas reglas que la sección de Cadenas de texto, solo que aquí se almacenan las cadenas de texto que se usan en las keys.

Inicia con un entero de 32 bits que indica la cantidad de caracteres que contiene la sección

Cada cadena está terminada por el caractér nulo

# Notas
- Para generar los hash de cada cadena se utiliza un algoritmo JOAAT de 32 bits. Antes de generar el hash, la cadena se debe convertir a todo minúsculas.
- Si un objeto o array está vacía, el valor de la sumatoria se omite y en su lugar se coloca como 0.
