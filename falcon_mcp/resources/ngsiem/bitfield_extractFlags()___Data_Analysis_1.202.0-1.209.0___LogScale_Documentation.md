# bitfield:extractFlags() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-bitfield-extractflags.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`bitfield:extractFlags()`](functions-bitfield-extractflags.html "bitfield:extractFlags\(\)")

Decodes an integer to its bit-representation and extracts the bits at specified indices to specified field names as a boolean. 

The bits are indexed from 0 and can accept up to 64 bits. If the value in the input field is larger, the lowest 64 bits will be used. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-bitfield-extractflags.html#query-functions-bitfield-extractflags-field)|  string| required |  |  The name of the field that should be decoded.   
[_`onlyTrue`_](functions-bitfield-extractflags.html#query-functions-bitfield-extractflags-onlytrue)|  boolean| optional[a] | `false`|  If set to `true`, fields will only be added if their value in the bitfield is `true`; any flags that are `false` will not be added.   
[_`output`_](functions-bitfield-extractflags.html#query-functions-bitfield-extractflags-output)|  array of arrays of strings| required |  |  A list of pairs of indices in the bit-representation and the field name it should be written to.   
[a] Optional parameters use their default value unless explicitly set.  
  
### [`bitfield:extractFlags()`](functions-bitfield-extractflags.html "bitfield:extractFlags\(\)") Examples

Click + next to an example below to get the full details.

#### Decode and Extract Bit Flags 

**Extract`true`bits using the [`bitfield:extractFlags()`](functions-bitfield-extractflags.html "bitfield:extractFlags\(\)") function **

##### Query

logscale
    
    
    bitfield:extractFlags(field="MemoryDescriptionFlags", onlyTrue=true, output=[
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

In this example, the [`bitfield:extractFlags()`](functions-bitfield-extractflags.html "bitfield:extractFlags\(\)") function is used to decode the field MemoryDescriptionFlags and extract its `true` bits. 

Example incoming data might look like this: 

Raw Events

MemoryDescriptionFlags,1234  
---  
// corresponds to 10011010010  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bitfield:extractFlags(field="MemoryDescriptionFlags", onlyTrue=true, output=[
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

Decodes the field MemoryDescriptionFlags and extracts the `true` bits at specified indices with specified names. The fields will be named with the names of the set bits. 

  3. Event Result set.




##### Summary and Results

The query is used to decode an integer to its bit-representation and extract the `true` bits at specified indices with specified names. 

Sample output from the incoming example data: 

CODE| CURRENT_STACK| FREE_MEMORY| INVALID_ADDRESS| JIT_DOTNET| JIT_FLASH| KNOWN_FUNCTION| MAPPED| MODULE| MZ| PRIMARY_MODULE| PRIVATE_MEMORY| REFLECIVE_PE  
---|---|---|---|---|---|---|---|---|---|---|---|---  
true| true| false| false| false| false| false| true| false| false| false| true| true  
  
#### Generate Temporary Event With Bit Flags For Troubleshooting

**Generate temporary events with the[`createEvents()`](functions-createevents.html "createEvents\(\)") function as part of the query to generate sample data for testing or troubleshooting **

##### Query

logscale
    
    
    createEvents(["flags=4"])
    | kvParse()
    | bitfield:extractFlags(
    field=flags,
    output=[
    [1, ErrorFlag],
    [2, WarningFlag]
    ])

##### Introduction

In this example, the bit field is named `flags` and has the value `4` corresponding to the bit string `00000100`. The goal is to extract two flags based on their bit value. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         createEvents(["flags=4"])

Creates a temporary event that includes a new field named flag to be used for testing purposes. Bit flags are one or more (up to 32) Boolean values stored in a single number variable. 

  3. logscale
         
         | kvParse()

Parses the raw text looking for the key/value pairs and creates the corresponding fields in the event. In this case a single field named flags with the value `8`. 

  4. logscale
         
         | bitfield:extractFlags(
         field=flags,
         output=[
         [1, ErrorFlag],
         [2, WarningFlag]
         ])

When specifying the values for the bit field, values start from bit 0 (`2^0` or decimal 1). The invidual bit values are defined using an array of arrays. Each array index should specify the bit number (not literal value) and the field to be created. Each field will then be set to `true` if the bit was enabled in the compared field. 

In the above example, `ErrorFlag` located at bit 1 (2^1, decimal 2), and `WarningFlag` located at index `2` (decimal 4). 

  5. Event Result set.




##### Summary and Results

The query is used to extract and match values to bit flags. Creating events based on bit flags are useful when testing and troubleshooting on values, as it is faster to compare values stored as bitmasks compared to a series of booleans. Furthermore, events based on bit flags uses considerably less memory. 

Sample output from the incoming example data: 

ErrorFlag| WarningFlag  
---|---  
false| true
