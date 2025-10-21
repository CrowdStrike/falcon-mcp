# Format Values From Two Array Elements Using : | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-objectarrayeval.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Format Values From Two Array Elements Using :

Format Values from Two Array Elements using : as a separator 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    objectArray:eval("in[]", asArray="out[]", function={out := format("%s:%s", field=[in.key, in.value])})

### Introduction

The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function is a structured array query function that follows normal array syntax. The array syntax is similar to the one used by JSON, where `[` and `]` are used for indexing and `.` for selecting members in objects. For more information, see [Array Syntax](https://library.humio.com/data-analysis/syntax-array.html). The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function operates on arrays of objects using a function that supports a special pattern to access sub-selections of array entries. 

The special pattern that allows the function to operate on arrays of objects, and arrays of arrays, and other arrays of structured data is: "in" (the input array) followed by: 
    
    
    .subselection

or 
    
    
    [number]

or any combination of the above. For example: 
    
    
    in.key,
    in.others[0].foo
    in[0][1]

Semantically, given the input array `in`, an array index `i`, and an access `in.subselection` this will be translated to the field name `in[i]._`subselection`_`. Similarly, `in[2]` is translated to `in[i][2]`. 

In this example, the [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function is used to format the array entries `in[].key ` and `in[].value` separating the concatenated values with a `:` in the output field out[]. The output must be a single field in this example as [`format()`](https://library.humio.com/data-analysis/functions-format.html) is only capable of creating a single value. 

Example incoming data might look like this: 

JSON
    
    
    in[0].key = x
    in[0].value = y
    in[1].key = a
    in[1].value = b

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         objectArray:eval("in[]", asArray="out[]", function={out := format("%s:%s", field=[in.key, in.value])})

Iterates (executes a loop) over the array from start to end (or to the first empty index in the array), applies the given function, and returns the concatenated results in a new output array name field out[]. 

Notice that a [_`var`_](https://library.humio.com/data-analysis/functions-objectarray-eval.html#query-functions-objectarray-eval-var) parameter can be used to give a different name to the input array variable inside the function argument. This is particularly useful whenever the input array name is very long. Example: 

logscale
         
         objectArray:eval("someVeryLongName[]", asArray="out[]",
         var=x, function={out := format("%s:%s", field=[x.key,
         x.value])})

  3. Event Result set.




### Summary and Results

The query is used to format arrays of objects. 

Sample output from the incoming example data: 
    
    
    out[0] = x:y
    out[1] = a:b
