# Concatenate Values From Deeply Nested Array Elements | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-objectarrayeval-concat-nested-3.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Concatenate Values From Deeply Nested Array Elements

Concatenate deeply nested objects and arrays using [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function with itself 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    objectArray:eval(
            "in[]",
            asArray="out[]",
            function={
    objectArray:eval("in.others[]", asArray="tmp[]", function={tmp := "in.others.d"})
    | out := concatArray(tmp)
              }
              )

### Introduction

The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function is a structured array query function that follows normal array syntax. The array syntax is similar to the one used by JSON, where `[` and `]` are used for indexing and `.` for selecting members in objects. For more information, see [Array Syntax](https://library.humio.com/data-analysis/syntax-array.html). The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function operates on arrays of objects using a function that supports a special pattern to access sub-selections of array entries. 

The special pattern that allows the function to operate on arrays of objects, and arrays of arrays, and other arrays of structured data is: "in" (the input array) followed by: 

logscale Syntax
    
    
    .subselection

or 

logscale Syntax
    
    
    [number]

or any combination of the above. For example: 

logscale Syntax
    
    
    in.key,
    in.others[0].foo
    in[0][1]

Semantically, given the input array `in`, an array index `i`, and an access `in.subselection` this will be translated to the field name `in[i]._`subselection`_`. Similarly, `in[2]` is translated to `in[i][2]`. 

The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function can be combined with other array functions (or itself), in order to support processing nested arrays. 

In this example, the [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function is used with itself to concatenate a deeply nested arrays of objects values in the array in[] and return the concatenated values in the output field out[]. 

Example incoming data might look like this: 

in[0].others[0].d: 1  
---  
in[0].others[1].d: 2  
in[0].others[2].d: 3  
in[1].others[0].d: 4  
in[1].others[1].d: 5  
in[1].others[2].d: 6  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         objectArray:eval(
                 "in[]",
                 asArray="out[]",
                 function={

Iterates over the array from start to end (or to the first empty index in the array, applies the given function, and returns the concatenated results in a new output array name field out[]. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         objectArray:eval("in.others[]", asArray="tmp[]", function={tmp := "in.others.d"})
         | out := concatArray(tmp)
                   }
                   )

The nested [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) performs the concatenation of the values within the nested array by calling the [`concatArray()`](https://library.humio.com/data-analysis/functions-concatarray.html) function. 

Notice that in the nested call to [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html), the given input array name is the nested array in.others[]. This works because it is translated to the field in[i].others[] by the parent [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) current array index `i`. 

To return the concatenated array, the [_`asArray`_](https://library.humio.com/data-analysis/functions-objectarray-eval.html#query-functions-objectarray-eval-asarray) parameter is set to the tmp[] field, and then when we assign the value of the concatenated value. 

  4. Event Result set.




### Summary and Results

The query is used to concatenate deeply nested arrays of objects. The use of this function in this way is often useful when incoming ingested data has been defined in a nested structure, but needs to be displayed or summarized. For example, importing the properties or configuration values may result in a list of potential values for a given property. Concatenating the values together makes them easier to use as a summary value for display in a table or graph. 

Sample output from the incoming example data: 
    
    
    out[0]: 123
    out[1]: 456
