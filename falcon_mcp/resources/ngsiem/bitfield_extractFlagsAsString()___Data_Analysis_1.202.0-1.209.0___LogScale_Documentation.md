# bitfield:extractFlagsAsString() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-bitfield-extractflagsasstring.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`bitfield:extractFlagsAsString()`](functions-bitfield-extractflagsasstring.html "bitfield:extractFlagsAsString\(\)")

Decodes an integer to its bit-representation and extracts the `true` bits at specified indices with specified names to a string. The flags are listed in ascending order, from lowest bit to highest bit. If no flags are `true`, the output field will contain an empty string. 

The bits are indexed from 0 and will include up to 64 bits. If the value in the input field is larger, the lowest 64 bits will be used. 

If the specified field does not exist, nothing happens. If a field with the name given for the output field already exists, it is overwritten. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-bitfield-extractflagsasstring.html#query-functions-bitfield-extractflagsasstring-as)|  string| optional[a] | `_flags`|  The name of the output field.   
[_`field`_](functions-bitfield-extractflagsasstring.html#query-functions-bitfield-extractflagsasstring-field)|  string| required |  |  The name of the field to be decoded.   
[_`flagNames`_](functions-bitfield-extractflagsasstring.html#query-functions-bitfield-extractflagsasstring-flagnames)|  array of arrays of strings| required |  |  A list of pairs of indices in the bit-representation and the names of the flags that these correspond to.   
[_`separator`_](functions-bitfield-extractflagsasstring.html#query-functions-bitfield-extractflagsasstring-separator)|  string| optional[[a]](functions-bitfield-extractflagsasstring.html#ftn.table-functions-bitfield-extractflagsasstring-optparamfn) | `(space)`|  The separator to use between names of `true` flags.   
[a] Optional parameters use their default value unless explicitly set.  
  
**Validation** : 

In the [_`flagNames`_](functions-bitfield-extractflagsasstring.html#query-functions-bitfield-extractflagsasstring-flagnames) parameter, the indices have to be non-negative numbers below 64. The indices and the names of the flags have to be unique. 

### [`bitfield:extractFlagsAsString()`](functions-bitfield-extractflagsasstring.html "bitfield:extractFlagsAsString\(\)") Examples

Click + next to an example below to get the full details.

#### Decode and Extract `true` Bits as Strings - Example 1

**Decode and extract`true` bits as strings using the [`bitfield:extractFlagsAsString()`](functions-bitfield-extractflagsasstring.html "bitfield:extractFlagsAsString\(\)") function **

##### Query

logscale
    
    
    bitfield:extractFlagsAsString(field="MemoryDescriptionFlags", flagNames=[
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
    [12,FREE_MEMORY]])

##### Introduction

In this example, the [`bitfield:extractFlagsAsString()`](functions-bitfield-extractflagsasstring.html "bitfield:extractFlagsAsString\(\)") function is used to decode the field MemoryDescriptionFlags and extract its `true` bits. 

Example incoming data might look like this: 

Raw Events

MemoryDescriptionFlags,1234  
---  
// corresponds to 10011010010  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bitfield:extractFlagsAsString(field="MemoryDescriptionFlags", flagNames=[
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
         [12,FREE_MEMORY]])

Decodes the field MemoryDescriptionFlags and extracts the `true` bits at specified indices with specified names to a string in a field named _flags. The string will contain the names of the set bits, listed in ascending order, from lowest bit to highest bit. 

  3. Event Result set.




##### Summary and Results

The query is used to decode an integer to its bit-representation and extract the `true` bits at specified indices with specified names to a string. 

Sample output from the incoming example data: 

_flags  
---  
CURRENT_STACK CODE MAPPED REFLECIVE_PE PRIVATE_MEMORY  
  
#### Decode and Extract `true` Bits as Strings - Example 2

**Decode and Extract`true` bits as strings using the [`bitfield:extractFlagsAsString()`](functions-bitfield-extractflagsasstring.html "bitfield:extractFlagsAsString\(\)") function with a comma separator **

##### Query

logscale
    
    
    bitfield:extractFlagsAsString(field="MemoryDescriptionFlags", flagNames=[
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
    [12,FREE_MEMORY]], as="trueFlags", separator=", ")

##### Introduction

In this example, the [`bitfield:extractFlagsAsString()`](functions-bitfield-extractflagsasstring.html "bitfield:extractFlagsAsString\(\)") function is used to decode the field MemoryDescriptionFlags, separating the `true` bits with a comma. 

Example incoming data might look like this: 

Raw Events

MemoryDescriptionFlags,1234  
---  
// corresponds to 10011010010  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bitfield:extractFlagsAsString(field="MemoryDescriptionFlags", flagNames=[
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
         [12,FREE_MEMORY]], as="trueFlags", separator=", ")

Decodes the field MemoryDescriptionFlags and extracts the `true` bits at specified indices with specified names to a comma-separated string in a field named trueFlags. The string will contain the names of the set bits, listed in ascending order, from lowest bit to highest bit. 

  3. Event Result set.




##### Summary and Results

The query is used to decode an integer to its bit-representation and extract the `true` bits at specified indices with specified names to a string. 

Sample output from the incoming example data: 

trueFlags  
---  
CURRENT_STACK, CODE MAPPED, REFLECIVE_PE, PRIVATE_MEMORY
