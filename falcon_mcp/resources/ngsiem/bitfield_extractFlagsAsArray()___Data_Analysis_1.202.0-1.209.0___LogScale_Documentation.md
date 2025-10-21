# bitfield:extractFlagsAsArray() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-bitfield-extractflagsasarray.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`bitfield:extractFlagsAsArray()`](functions-bitfield-extractflagsasarray.html "bitfield:extractFlagsAsArray\(\)")

Decodes an integer to its bit-representation and extracts the `true` bits at specified indices with specified names to an array. The array will contain the names of the set bits, in order from lowest bit to highest bit. 

The bits are indexed from 0 and will include up to 64 bits. If the value in the input field is larger, the lowest 64 bits will be used. 

If the specified field does not exist, nothing happens. If an array with the name given as the output array already exists, it is overwritten. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`asArray`_](functions-bitfield-extractflagsasarray.html#query-functions-bitfield-extractflagsasarray-asarray)|  string| optional[a] | `_flags[]`|  The name of the output array. Must follow valid [Array Syntax](syntax-array.html "Array Syntax").   
[_`field`_](functions-bitfield-extractflagsasarray.html#query-functions-bitfield-extractflagsasarray-field)|  string| required |  |  The name of the field to be decoded.   
[_`flagNames`_](functions-bitfield-extractflagsasarray.html#query-functions-bitfield-extractflagsasarray-flagnames)|  array of arrays of strings| required |  |  A list of pairs of indices in the bit-representation and the names of the flags that these correspond to.   
[a] Optional parameters use their default value unless explicitly set.  
  
**Validation** : 

In the [_`flagNames`_](functions-bitfield-extractflagsasarray.html#query-functions-bitfield-extractflagsasarray-flagnames) parameter, the indices have to be non-negative numbers below 64. The indices and the names of the flags have to be unique. 

### [`bitfield:extractFlagsAsArray()`](functions-bitfield-extractflagsasarray.html "bitfield:extractFlagsAsArray\(\)") Examples

Click + next to an example below to get the full details.

#### Decode and Extract `true` Bits as Arrays

**Decode and extract`true` bits as arrays using the [`bitfield:extractFlagsAsArray()`](functions-bitfield-extractflagsasarray.html "bitfield:extractFlagsAsArray\(\)") function **

##### Query

logscale
    
    
    bitfield:extractFlagsAsArray(field="MemoryDescriptionFlags", flagNames=[
    [0,INVALID_ADDRESS],
    [1,CURRENT_STACK],
    [2,JIT_DOTNET],
    [3,MZ],
    [4,CODE],
    [5,MODULE],
    [6,MAPPED],
    [7,REFLECIVE_PE],
    [8,JIT_FLASH],
    [9,PRIMARY_MODULE],
    [10,PRIVATE_MEMORY],
    [11,KNOWN_FUNCTION],
    [12,FREE_MEMORY]], asArray="flagsArray[]")

##### Introduction

In this example, the [`bitfield:extractFlagsAsArray()`](functions-bitfield-extractflagsasarray.html "bitfield:extractFlagsAsArray\(\)") function is used to decode the field MemoryDescriptionFlags and extract its `true` bits. 

Example incoming data might look like this: 

Raw Events

MemoryDescriptionFlags,1234  
---  
// corresponds to 10011010010  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bitfield:extractFlagsAsArray(field="MemoryDescriptionFlags", flagNames=[
         [0,INVALID_ADDRESS],
         [1,CURRENT_STACK],
         [2,JIT_DOTNET],
         [3,MZ],
         [4,CODE],
         [5,MODULE],
         [6,MAPPED],
         [7,REFLECIVE_PE],
         [8,JIT_FLASH],
         [9,PRIMARY_MODULE],
         [10,PRIVATE_MEMORY],
         [11,KNOWN_FUNCTION],
         [12,FREE_MEMORY]], asArray="flagsArray[]")

Decodes the field MemoryDescriptionFlags and extracts the `true` bits at specified indices with specified names to an array named flagsArray[]. The array will contain the names of the set bits, listed in ascending order, from lowest bit to highest bit. 

  3. Event Result set.




##### Summary and Results

The query is used to decode an integer to its bit-representation and extract the `true` bits at specified indices with specified names to an array. 

Sample output from the incoming example data: 

flagsArray[0]| flagsArray[1]| flagsArray[2]| flagsArray[3]| flagsArray[4]  
---|---|---|---|---  
CURRENT_STACK| CODE| MAPPED| REFLECIVE_PE| PRIVATE_MEMORY
