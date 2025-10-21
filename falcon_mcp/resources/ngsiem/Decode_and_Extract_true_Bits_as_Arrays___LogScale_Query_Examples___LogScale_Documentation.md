# Decode and Extract true Bits as Arrays | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-bitfield-extractflagsasarray.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Decode and Extract `true` Bits as Arrays

Decode and extract `true` bits as arrays using the [`bitfield:extractFlagsAsArray()`](https://library.humio.com/data-analysis/functions-bitfield-extractflagsasarray.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

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

### Introduction

The [`bitfield:extractFlagsAsArray()`](https://library.humio.com/data-analysis/functions-bitfield-extractflagsasarray.html) function can be used to decode an integer to its bit-representation and extract the `true` bits at specified indices with specified names to an array. The array will contain the names of the set bits, listed in ascending order, from lowest bit to highest bit. The bits are indexed from 0 and will include up to 64 bits. If the value in the input field is larger, the lowest 64 bits will be used. 

In this example, the [`bitfield:extractFlagsAsArray()`](https://library.humio.com/data-analysis/functions-bitfield-extractflagsasarray.html) function is used to decode the field MemoryDescriptionFlags and extract its `true` bits. 

Example incoming data might look like this: 

Raw Events

MemoryDescriptionFlags,1234  
---  
// corresponds to 10011010010  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

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

Decodes the field MemoryDescriptionFlags and extracts the `true` bits at specified indices with specified names to an array named flagsArray[]. The array will contain the names of the set bits, listed in ascending order, from lowest bit to highest bit. 

  3. Event Result set.




### Summary and Results

The query is used to decode an integer to its bit-representation and extract the `true` bits at specified indices with specified names to an array. 

Sample output from the incoming example data: 

flagsArray[0]| flagsArray[1]| flagsArray[2]| flagsArray[3]| flagsArray[4]  
---|---|---|---|---  
CURRENT_STACK| CODE| MAPPED| REFLECIVE_PE| PRIVATE_MEMORY
