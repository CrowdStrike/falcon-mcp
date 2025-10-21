# Calculate e Raised to Power Minus One | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathexpm1-calculate-exp-minus-one.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate `e` Raised to Power Minus One

Calculate `e^x - 1` using the [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) or [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) functions 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] 3["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    x := 0.00001
    | math:expm1(x, as=precise_result)
    | math:exp(x, as=standard_result)

### Introduction

The [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) function can be used to calculate `e^x - 1` with high numerical precision, especially for values of x close to zero. The [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) function provides better numerical accuracy than calculating [`math:exp(x)`](https://library.humio.com/data-analysis/functions-math-exp.html) \- 1 directly, avoiding potential loss of precision due to floating-point arithmetic. 

Note that the [`math:exp(x)`](https://library.humio.com/data-analysis/functions-math-exp.html) function calculates the full exponential value, making it ideal for general exponential calculations where x is not close to zero. For calculations involving very small values where you need to subtract 1 from the result, [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) provides better numerical precision. 

In this example, the [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) function and [`math:exp()`](https://library.humio.com/data-analysis/functions-math-exp.html) function are used to calculate `e^x - 1` for a small value of `x`, demonstrating the superior precision of [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) compared to using [`math:exp()`](https://library.humio.com/data-analysis/functions-math-exp.html) and subtracting `1`. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] 3["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 0.00001

Assigns a very small double-precision floating-point value `0.00001` to a field named x. This small value near zero demonstrates where [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) provides better numerical precision. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] 3["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:expm1(x, as=precise_result)

Calculates `e^x - 1` for the value in field x and returns the result in a new field named precise_result. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-expm1.html#query-functions-math-expm1-as) parameter is not specified, the result is returned in a field named _expm1 as default. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] 3["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:exp(x, as=standard_result)

Calculates `e^x` for the value in field x and returns the result in a new field named standard_result. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-exp.html#query-functions-math-exp-as) parameter is not specified, the result is returned in a field named _exp as default. 

  5. Event Result set.




### Summary and Results

The query is used to calculate exponential values minus one with high precision, which is particularly important in scientific and financial calculations involving very small values. The [`math:exp(x)`](https://library.humio.com/data-analysis/functions-math-exp.html) function is also mentioned in this query to show that it is less precise due to floating-point rounding compared to the [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) function. 

The precise_result field contains the more accurate calculation using [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html), while standard_result shows the result of using [`math:exp()`](https://library.humio.com/data-analysis/functions-math-exp.html) and subtracting `1`. 

This query is useful, for example, to calculate small percentage changes in financial applications, compute precise scientific measurements near baseline values and analyze small deviations in statistical data. 

Sample output from the incoming example data: 

precise_result| standard_result  
---|---  
0.0000100000050000017| 0.0000100000050000166  
  
The results show that [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) provides more precise calculations for small values. For values close to zero, the difference between the two methods becomes significant in applications requiring high precision. 

Note that while the difference between the two methods may appear small, it becomes crucial in applications requiring high precision, especially when dealing with very small values or when performing many successive calculations. 

In short, best practise is to: 

Use [`math:expm1(x)`](https://library.humio.com/data-analysis/functions-math-expm1.html) instead of `[`math:exp(x)`](https://library.humio.com/data-analysis/functions-math-exp.html) - 1` when: 

  * x is close to 0 

  * Precision is important 

  * Working with small values 




Use [`math:exp(x)`](https://library.humio.com/data-analysis/functions-math-exp.html) \- 1 when: 

  * x is larger 

  * Extreme precision is not required 

  * Performance is more important than precision
