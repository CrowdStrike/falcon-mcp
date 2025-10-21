# Concatenate Values in Arrays With a Defined Prefix and Suffix | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-concatarray-prefix-suffix.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Concatenate Values in Arrays With a Defined Prefix and Suffix

Concatenate values in flat arrays using prefix, suffix and separator 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    concatArray(server, prefix="[", separator=",", suffix="]")

### Introduction

The [`concatArray()`](https://library.humio.com/data-analysis/functions-concatarray.html) method concatenates (joins) two or more arrays and returns a new array, containing the joined arrays. The [`concatArray()`](https://library.humio.com/data-analysis/functions-concatarray.html) method does not change the existing arrays. For more information, see [Array Syntax](https://library.humio.com/data-analysis/syntax-array.html). 

In this example, the [`concatArray()`](https://library.humio.com/data-analysis/functions-concatarray.html) function concatenates the values of all fields with the same name and an array suffix into a value in a new field, adding a prefix and a suffix to the generated output result. 

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
         
         concatArray(server, prefix="[", separator=",", suffix="]")

Concatenates the values of fields server[0], server[1] and so on and returns the results as a string named _concatArray enclosed in square brackets, and separated by a comma, which is similar to the written array format. 

  3. Event Result set.




### Summary and Results

This can be useful to summarize or format a list of items for use in another part of the query. 

Sample output from the incoming example data: 

server[0]| server[1]| server[2]| server[3]| server[4]| _concatArray  
---|---|---|---|---|---  
dopey| sleepy| doc| happy| sneezy| [dopey,sleepy,doc,happy,dopey]
