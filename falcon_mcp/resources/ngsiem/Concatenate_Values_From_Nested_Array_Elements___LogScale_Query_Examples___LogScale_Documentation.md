# Concatenate Values From Nested Array Elements | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-objectarrayeval-concat-nested-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Concatenate Values From Nested Array Elements

Concatenate deeply nested objects and arrays using [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function with [`concat()`](https://library.humio.com/data-analysis/functions-concat.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    objectArray:eval("in[]", asArray="out[]", function={out := concat(["in.a", "in.b.c", "in.others[1].d"])})

### Introduction

The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html)function is a structured array query function that follows normal array syntax. The array syntax is similar to the one used by JSON, where `[` and `]` are used for indexing and `.` for selecting members in objects. For more information, see [Array Syntax](https://library.humio.com/data-analysis/syntax-array.html). The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function operates on arrays of objects using a function that supports a special pattern to access sub-selections of array entries. 

The special pattern that allows the function to operate on arrays of objects, and arrays of arrays, and other arrays of structured data is: "in" (the input array) followed by: 
    
    
    .subselection

or 
    
    
    [number]

or any combination of the above. For example: 
    
    
    in.key,
    in.others[0].foo
    in[0][1]

Semantically, given the input array `in`, an array index `i`, and an access `in.subselection` this will be translated to the field name `in[i]._`subselection`_`. Similarly, `in[2]` is translated to `in[i][2]`. 

The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function can be combined with other array functions (or itself), in order to support processing nested arrays. When used with nested arrays, multiple values can be accessed and processed. 

In this example, the [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function is used with the [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) function to concatenate deeply nested arrays of objects values in the array `in[] ` and return the concatenated values in the output field out[]. 

Example incoming data might look like this: 

JSON
    
    
    in[0].a: 1
    in[0].b.c: 2
    in[0].others[0].d: 3
    in[0].others[1].d: 4

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         objectArray:eval("in[]", asArray="out[]", function={out := concat(["in.a", "in.b.c", "in.others[1].d"])})

Iterates over the array from start to end (or to the first empty index in the array), applies the given function, and returns the concatenated results in a new output array name field out[]. 

  3. Event Result set.




### Summary and Results

The query is used to concatenate deeply nested arrays of objects. 

Sample output from the incoming example data: 
    
    
    out[0]: 124
