# Concatenate Multiple Values From Nested Array Elements | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-objectarrayeval-nested-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Concatenate Multiple Values From Nested Array Elements

Concatenate multiple values from nested array elements using [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function with [`concat()`](https://library.humio.com/data-analysis/functions-concat.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    objectArray:eval("foo[]", var=x, function={_mapped := concat([x.key.value, "x.key.others[0]", "x.key.others[1]"])}, asArray="_mapped[]")

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

The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function can be combined with other array functions (or itself), in order to support processing nested arrays. When used with nested arrays, multiple values can be accessed and processed. 

In this example, the [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function is used with the [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) function to concatenate multiple deeply nested arrays of objects values in the array `foo[] ` and return the concatenated values in the output field _mapped[]

Example incoming data might look like this: 

JSON
    
    
    "foo[0].key.value": y
    "foo[0].key.others[0]": 1
    "foo[0].key.others[1]": 2
    "foo[1].nothing": 355

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         objectArray:eval("foo[]", var=x, function={_mapped := concat([x.key.value, "x.key.others[0]", "x.key.others[1]"])}, asArray="_mapped[]")

Notice that a [_`var`_](https://library.humio.com/data-analysis/functions-objectarray-eval.html#query-functions-objectarray-eval-var) parameter can be used to give a different name to the input array variable inside the function argument. This is particularly useful whenever the input array name is very long. 

  3. Event Result set.




### Summary and Results

The query is used to concatenate multiple deeply nested arrays of objects values. 

Sample output from the incoming example data: 
    
    
    _mapped[0]: y12
    "foo[0].key.value": y
    "foo[0].key.others[0]": 1
    "foo[0].key.others[1]": 2
