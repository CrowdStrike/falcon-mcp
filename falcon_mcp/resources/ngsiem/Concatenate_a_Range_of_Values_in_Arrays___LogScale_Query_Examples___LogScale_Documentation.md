# Concatenate a Range of Values in Arrays | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-concatarray-3.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Concatenate a Range of Values in Arrays

Concatenate values in flat arrays 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    concatArray(server, from=1, to=3)

### Introduction

The [`concatArray()`](https://library.humio.com/data-analysis/functions-concatarray.html) method concatenates (joins) two or more arrays and returns a new array, containing the joined arrays. The [`concatArray()`](https://library.humio.com/data-analysis/functions-concatarray.html) method does not change the existing arrays. For more information, see [Array Syntax](https://library.humio.com/data-analysis/syntax-array.html). 

In this example, the [`concatArray()`](https://library.humio.com/data-analysis/functions-concatarray.html) function concatenates the values of all fields with the same name and index between 1 to 3 into a value in a new field. 

Example incoming data might look like this: 
    
    
    server[0] := "dopey"
    server[1] := "sleepy"
    server[2] := "doc"
    server[3] := "happy"
    server[4] := "sneezy"

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         concatArray(server, from=1, to=3)

Concatenates the values of fields server[1], server[2], and server[3], and returns the results in a new array with a field named _concatArray. 

  3. Event Result set.




### Summary and Results

The query is used to concatenate (join) two or more arrays into a new array. Concatenation is useful in programming and computing because it allows you to store and combine multiple pieces of data when needed. 

Sample output from the incoming example data: 

server[0]| server[1]| server[2]| server[3]| server[4]| _concatArray  
---|---|---|---|---|---  
dopey| sleepy| doc| happy| sneezy| sleepydochappy
