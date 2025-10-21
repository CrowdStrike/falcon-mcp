# Calculate e Raised to Power | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathexp-calculate-exp.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate `e` Raised to Power

Calculate `e^x` using the [`math:exp()`](https://library.humio.com/data-analysis/functions-math-exp.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 1.0
    | math:exp(x, as=result)

### Introduction

The [`math:exp()`](https://library.humio.com/data-analysis/functions-math-exp.html) function can be used to calculate `e^x` (e raised to the power of x), where `e` is Euler's number (approximately `2.718281828`). Unlike [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) which calculates `e^x - 1` with high precision for values near zero, this function calculates the full exponential value. 

In this example, the [`math:exp()`](https://library.humio.com/data-analysis/functions-math-exp.html) function is used to calculate `e^x` for a given value, demonstrating exponential growth calculation. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 1.0

Assigns the double-precision floating-point value `1.0` to a field named x. This value will demonstrate the calculation of `e^x`, which equals Euler's number itself. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:exp(x, as=result)

Calculates `e^x` for the value in field x and returns the result in a new field named result. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-exp.html#query-functions-math-exp-as) parameter is not specified, the result is returned in a field named _exp as default. 

  4. Event Result set.




### Summary and Results

The query is used to calculate exponential values, which is fundamental in calculating compound growth, decay processes, and various scientific calculations. 

This query is useful, for example, to calculate compound interest, population growth, or radioactive decay where the rate of change is proportional to the current value. 

Sample output from the incoming example data: 

result  
---  
2.718281828459045  
  
The result shows that `e^x` equals Euler's number. While [`math:exp()`](https://library.humio.com/data-analysis/functions-math-exp.html) is suitable for most exponential calculations, for very small values of x where you need to calculate `e^x - 1`, consider using [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) instead for better numerical precision. For an example, see [Calculate `e` Raised to Power Minus One](examples-mathexpm1-calculate-exp-minus-one.html "Calculate e Raised to Power Minus One")

Note that this [`math:exp()`](https://library.humio.com/data-analysis/functions-math-exp.html) function calculates the full exponential value, making it ideal for general exponential calculations where x is not close to zero. For calculations involving very small values where you need to subtract 1 from the result, [`math:expm1()`](https://library.humio.com/data-analysis/functions-math-expm1.html) provides better numerical precision.
