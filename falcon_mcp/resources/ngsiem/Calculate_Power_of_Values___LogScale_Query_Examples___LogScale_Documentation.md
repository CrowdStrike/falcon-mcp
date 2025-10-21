# Calculate Power of Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathpow-calculate-power.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Power of Values

Calculate values raised to a power using the [`math:pow()`](https://library.humio.com/data-analysis/functions-math-pow.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 2
    exp := 3
    | math:pow(field=x, exponent=exp, as=result)

### Introduction

The [`math:pow()`](https://library.humio.com/data-analysis/functions-math-pow.html) function can be used to calculate a number raised to a specified power (exponent). It takes two parameters: [_`field`_](https://library.humio.com/data-analysis/functions-math-pow.html#query-functions-math-pow-field) (the input value to be raised to a power) and [_`exponent`_](https://library.humio.com/data-analysis/functions-math-pow.html#query-functions-math-pow-exponent) (the power to raise it to), and returns the result of raising the field value to that power. It supports both integer and decimal values for both the input field and exponent. 

In this example, the [`math:pow()`](https://library.humio.com/data-analysis/functions-math-pow.html) function is used to calculate values raised to different powers (xexp), demonstrating both integer and decimal exponents. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 2
         exp := 3

Assigns the value `2` to field x (the value to be raised to a power) and `3` to field exp (the exponent). This will calculate `x3`, which equals `8`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:pow(field=x, exponent=exp, as=result)

Raises the value in the field x to the power specified by the [_`exponent`_](https://library.humio.com/data-analysis/functions-math-pow.html#query-functions-math-pow-exponent) parameter and returns the result in a field named result. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-pow.html#query-functions-math-pow-as) parameter is not specified, the result is returned in a field named _pow as default. 

  4. Event Result set.




### Summary and Results

The query calculates the power of a number by raising it to a specified exponent. The [`math:pow()`](https://library.humio.com/data-analysis/functions-math-pow.html) function supports both integer and decimal values, making it versatile for various mathematical calculations. For example, you can calculate squares (x2), cubes (x3), or roots (using fractional exponents like `0.5` for square root). 

This query is useful for exponential calculations, geometric computations, scientific notation conversions, and any scenario requiring power operations. The function handles positive and negative numbers, as well as decimal exponents. 

Sample output from the incoming example data: 

result  
---  
8.000000  
  
The result shows that `2` raised to the power of `3` (`2³`) equals `8`, demonstrating the basic power operation. The function can also handle more complex calculations like `2.5⁴` or `3⁻²`.
