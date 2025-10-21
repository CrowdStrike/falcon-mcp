# Create Single Array from Object Arrays | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-objectarrayeval-output.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Single Array from Object Arrays

Transform one or more objects from object arrays into a single array 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    "a[0].foo" := "a"
    | "a[0].bar" := "b"
    | "a[1].foo" := "c"
    | "a[1].bar" := "d"
    | objectArray:eval(array="a[]", asArray="output[]", var="x", function={output := x.bar})

### Introduction

The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function is a structured array query function that follows normal array syntax. The array syntax is similar to the one used by JSON, where `[` and `]` are used for indexing and `.` for selecting members in objects. For more information, see [Array Syntax](https://library.humio.com/data-analysis/syntax-array.html). The [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function operates on arrays of objects. 

In this example, the [`objectArray:eval()`](https://library.humio.com/data-analysis/functions-objectarray-eval.html) function is used to extract one object from each element of an array of objects into a new array. 

Example incoming data might look like this: 

a[0].foo: a  
---  
a[0].bar: b  
a[1].foo: c  
a[1].bar: d  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         "a[0].foo" := "a"
         | "a[0].bar" := "b"
         | "a[1].foo" := "c"
         | "a[1].bar" := "d"

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | objectArray:eval(array="a[]", asArray="output[]", var="x", function={output := x.bar})

Iterates (creates a loop) over the array `a[]` and adds the value of the object `.bar` to a new array `output[]`. This is achieved by executing an anonymous function, which sets the value of `output` to the iterated value of `x.bar` from `a[]`. 

The [_`asArray`_](https://library.humio.com/data-analysis/functions-objectarray-eval.html#query-functions-objectarray-eval-asarray) parameter is set to the output[] field, creating an array where each element contains the value of x.bar from the corresponding iteration. 

  4. Event Result set.




### Summary and Results

The query is used to create an array from compound arrays. This can be useful when you need to collect specific values from nested arrays for further processing, filtering, or analysis. 

Sample output from the incoming example data: 

a[0].foo| a[0].bar| a[1].foo| a[1].bar| output[0]| output[1]  
---|---|---|---|---|---  
a| b| c| d| b| d
