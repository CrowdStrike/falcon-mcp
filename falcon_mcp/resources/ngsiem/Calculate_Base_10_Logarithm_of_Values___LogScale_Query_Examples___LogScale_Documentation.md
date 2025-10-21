# Calculate Base 10 Logarithm of Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathlog10-calculate-logarithm.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Base 10 Logarithm of Values

Calculate the base 10 logarithm of a double field using the [`math:log10()`](https://library.humio.com/data-analysis/functions-math-log10.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 100.0
            | math:log10(x, as=log10_result)

### Introduction

The [`math:log10()`](https://library.humio.com/data-analysis/functions-math-log10.html) function can be used to calculate the base 10 logarithm of a double field (a field containing a double-precision floating-point number). This function determines the exponent needed to raise 10 to obtain the given number. 

In this example, the [`math:log10()`](https://library.humio.com/data-analysis/functions-math-log10.html) function is used to calculate the base 10 logarithm of a double-precision value, showing how many times you need to multiply 10 by itself to get that value. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 100.0

Assigns the double-precision floating-point value `100.0` to a field named x. This value will be used to calculate its base 10 logarithm. Note the decimal point indicating a floating-point number. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:log10(x, as=log10_result)

Calculates the base 10 logarithm of the double-precision value in field x and returns the result in a new field named log10_result as a double-precision number. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-log10.html#query-functions-math-log10-as) parameter is not specified, the result is returned in a field named _log10 as default. 

  4. Event Result set.




### Summary and Results

The query is used to calculate the base 10 logarithm of a double-precision value, which is useful in analyzing exponential growth or decay in decimal systems. 

This query is useful, for example, to analyze orders of magnitude in scientific notation, convert between linear and logarithmic scales, or measure exponential relationships in scientific applications where precise floating-point calculations are required. 

Sample output from the incoming example data: 

log10_result  
---  
2.000000  
  
The result shows that the base 10 logarithm of `100.0 = 2.000000`, meaning that `10² = 100`. This indicates that you need to multiply 10 by itself 2 times to get 100. 

Some other examples with double-precision values: 

  * base 10 logarithm of 10.0 = 1.000000 (`10¹ = 10`) 

  * base 10 logarithm of 1000.0 = 3.000000 (`10³ = 1000`) 

  * base 10 logarithm of 1.0 = 0.000000 (`10⁰ = 1`) 

  * base 10 logarithm of 0.1 = -1.000000 (`10⁻¹ = 0.1`)
