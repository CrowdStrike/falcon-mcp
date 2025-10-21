# Calculate Floor Value of a Number | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathfloor-calculate-floor.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Floor Value of a Number

Calculate the largest integer less than or equal to a number using the [`math:floor()`](https://library.humio.com/data-analysis/functions-math-floor.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 3.7
    | math:floor(x, as=floor_result)

### Introduction

The [`math:floor()`](https://library.humio.com/data-analysis/functions-math-floor.html) function can be used to calculate the largest integer less than or equal to a given number (a field containing a double-precision floating-point number). This function effectively rounds a number down to the nearest integer. 

In this example, the [`math:floor()`](https://library.humio.com/data-analysis/functions-math-floor.html) function is used to calculate the floor value of a decimal number, demonstrating how it always rounds down to the nearest integer regardless of the decimal portion. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 3.7

Assigns the double-precision floating-point value `3.7` to a field named x. This value will be used to demonstrate the floor function. Note the decimal point indicating a floating-point number. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:floor(x, as=floor_result)

Calculates the floor value of the double-precision value in field x and returns the result in a new field named floor_result as a double-precision number. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-floor.html#query-functions-math-floor-as) parameter is not specified, the result is returned in a field named _floor as default. 

  4. Event Result set.




### Summary and Results

The query is used to find the largest integer less than or equal to a given number, which is useful when you need to round numbers down consistently. 

This query is useful, for example, to calculate whole units from decimal measurements, determine complete time periods, or round down financial calculations where partial units are not allowed. 

Sample output from the incoming example data: 

floor_result  
---  
3.000000  
  
The result shows that the floor value of `3.7` is `3.000000`, as `3` is the largest integer less than or equal to `3.7`. 

Some other examples demonstrating floor values: 

  * `math:floor(3.0) = 3.000000` (integer input returns the same integer) 

  * `math:floor(3.1) = 3.000000` (rounds down regardless of decimal value) 

  * `math:floor(-3.7) = -4.000000` (negative numbers round down to next lower integer) 

  * `math:floor(0.8) = 0.000000` (decimal numbers between 0 and 1 round down to 0) 




Note that the [`math:floor()`](https://library.humio.com/data-analysis/functions-math-floor.html) function always rounds down, unlike rounding functions that might round up or down based on the decimal portion. This makes it particularly useful when you need consistent downward rounding behavior.
