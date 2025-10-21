# Concatenate Values From Two Nested Array Elements | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-objectarrayeval-nested-to-flat.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Concatenate Values From Two Nested Array Elements

Concatenate values from two nested array elements returning output in flat array 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    objectArray:eval("arr[]", var=x, function={_mapped := concat([x.a, x.b])}, asArray="_mapped[]")

### Introduction

The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function is a structured array query function that follows normal array syntax. The array syntax is similar to the one used by JSON, where `[` and `]` are used for indexing and `.` for selecting members in objects. For more information, see [Array Syntax](https://library.humio.com/data-analysis/syntax-array.html). The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function operates on arrays of objects. 

In this example, the [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function is used with the variable x to concatenate the values `a` and `b` from each array element. The [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) function is used to return the concatenated output into a new array. 

Example incoming data might look like this: 

JSON
    
    
    arr[0]: machine
    arr[0].a: a0
    arr[0].b: b0
    arr[1].a: a1
    arr[1].b: b1
    arr[1].c: c1
    arr[2].a: a2
    arr[4].b: b2
    other: abc

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         objectArray:eval("arr[]", var=x, function={_mapped := concat([x.a, x.b])}, asArray="_mapped[]")

Concatenates the values `a` and `b` from each array element and returns the results in a new array named _mapped. In this example, [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) iterates over each element of the array and assigns each element to the variable `x` which is then used as an alias. The new field _mapped is created by concatenating the value using the alias `x` to extract each object value from each element of the array. Notice that the output in this example is a flat array. 

For example, this array element: 

arr[0].a: a0  
---  
arr[0].b: b0  
  
is translated to: 
         
         _mapped[0]: a0b0

  3. Event Result set.




### Summary and Results

The query is used to concatenate values of two array elements. 

Sample output from the incoming example data, the original values have not been removed: 
    
    
    _mapped[0]: a0b0
    _mapped[1]: a1b1
    _mapped[2]: a2
    _mapped[3]: b2
    
    arr[0]: machine
    
    arr[0].a: a0
    arr[0].b: b0
    
    arr[1].a: a1
    arr[1].b: b1
    
    arr[1].c: c1
    
    arr[2].a: a2
    
    arr[4].b: b2
    
    other: abc
