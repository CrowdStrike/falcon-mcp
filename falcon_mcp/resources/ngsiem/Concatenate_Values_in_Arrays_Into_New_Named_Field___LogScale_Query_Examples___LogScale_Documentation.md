# Concatenate Values in Arrays Into New Named Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-concatarray-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Concatenate Values in Arrays Into New Named Field

Concatenate values in flat arrays into new named field 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    concatArray("email", as=servers)

### Introduction

The [`concatArray()`](https://library.humio.com/data-analysis/functions-concatarray.html) method concatenates (joins) two or more arrays and returns a new array, containing the joined arrays. The [`concatArray()`](https://library.humio.com/data-analysis/functions-concatarray.html) method does not change the existing arrays. For more information, see [Array Syntax](https://library.humio.com/data-analysis/syntax-array.html). 

In this example, the [`concatArray()`](https://library.humio.com/data-analysis/functions-concatarray.html) function concatenates the values of all fields with the same name into a value in a new defined field. 

Example incoming data might look like this: 
    
    
    email[0] := "dopey"
    email[1] := "sleepy"
    email[2] := "doc"
    email[3] := "happy"
    email[4] := "sneezy"

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         concatArray("email", as=servers)

Concatenates the values of fields email[0], email[1] and so on and returns the results in a field named servers. 

  3. Event Result set.




### Summary and Results

The query is used to concatenate (join) two or more arrays into a new array. Concatenation is useful in programming and computing because it allows you to store and combine multiple pieces of data when needed. 

Sample output from the incoming example data: 

email[0]| email[1]| email[2]| email[3]| email[4]| servers  
---|---|---|---|---|---  
dopey| sleepy| doc| happy| sneezy| dopeysleepydochappysneezy
