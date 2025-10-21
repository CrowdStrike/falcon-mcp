# Calculate Natural Logarithm of Value Plus One | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathlog1p-calculate-logarithm.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Natural Logarithm of Value Plus One

Calculate the natural logarithm of `(1 + x)` using the [`math:log1p()`](https://library.humio.com/data-analysis/functions-math-log1p.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 0.0001
    | math:log1p(x, as=log1p_result)

### Introduction

The [`math:log1p()`](https://library.humio.com/data-analysis/functions-math-log1p.html) function can be used to calculate the natural logarithm of the sum of a field value and 1. For small values of x, the result of `log1p(x)` is much closer to the true result of `ln(1 + x)` than the floating-point evaluation of `log(1.0 + x)`. 

In this example, the [`math:log1p()`](https://library.humio.com/data-analysis/functions-math-log1p.html) function is used to demonstrate accurate calculation of `ln(1 + x)`, particularly for small values where standard floating-point arithmetic might lose precision. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 0.0001

Assigns a small value `0.0001` to a field named x. This demonstrates the function's precision advantage with small values. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:log1p(x, as=log1p_result)

Calculates `ln(1 + x)` for the value in field x and returns the result in a new field named log1p_result. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-log1p.html#query-functions-math-log1p-as) parameter is not specified, the result is returned in a field named _log1p as default. 

  4. Event Result set.




### Summary and Results

The query is used to calculate `ln(1 + x)` with high precision, particularly beneficial for small values where standard floating-point calculations might be inaccurate. 

This query is useful, for example, when working with small incremental changes, calculating precise logarithmic values near 1, or in financial calculations involving rates close to zero. 

Sample output from the incoming example data: 

log1p_result  
---  
0.00009999999833333334  
  
The result demonstrates the precise calculation of `ln(1 + 0.0001)`. Note that for very small values, the result is close to, but not exactly equal to, the input value. This is because [`math:log1p()`](https://library.humio.com/data-analysis/functions-math-log1p.html) provides better numerical accuracy than calculating `ln(1.0 + x)` directly, especially important when working with small values where floating-point precision matters.
