# Calculate Arc Tangent of Value | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-matharctan-calculate-arctangent.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Arc Tangent of Value

Calculate the arc tangent using the [`math:arctan()`](https://library.humio.com/data-analysis/functions-math-arctan.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 1.0
    | math:arctan(x, as=angle)

### Introduction

The [`math:arctan()`](https://library.humio.com/data-analysis/functions-math-arctan.html) function can be used to calculate the inverse tangent (arc tangent) of a value, returning the angle in radians. Unlike [`math:arctan2()`](https://library.humio.com/data-analysis/functions-math-arctan2.html) which uses two coordinates to determine the full angle, this function takes a single value and returns an angle in the range `-π/2` to `π/2` radians (from -90 to 90 degrees). 

In this example, the [`math:arctan()`](https://library.humio.com/data-analysis/functions-math-arctan.html) function is used to calculate the arc tangent of 1.0, which represents a slope of 1 (45-degree angle). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 1.0

Assigns the value `1.0` to field x. This value represents a slope of 1 (rise over run), which should result in an angle of `π/4` radians (45 degrees). 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:arctan(x, as=angle)

Calculates the arc tangent of the value in field x and returns the result in radians in a field named angle. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-arctan.html#query-functions-math-arctan-as) parameter is not specified, the result is returned in a field named _arctan as default. 

  4. Event Result set.




### Summary and Results

The query is used to calculate angles from slope values, which is useful in various mathematical and geometric calculations where you need to find an angle from a ratio. 

This query is useful, for example, to calculate angles from slopes, determine inclination from gradients, or analyze ratios in trigonometric calculations. 

Sample output from the incoming example data: 

angle  
---  
0.7853981633974483  
  
The result shows that the arc tangent of `1.0` is approximately `0.7854` radians (π/4 radians or 45 degrees). This means a slope of 1 corresponds to a 45-degree angle. 

Note that the [`math:arctan()`](https://library.humio.com/data-analysis/functions-math-arctan.html) function only returns values between `-π/2` and `π/2` radians (-90 to 90 degrees). For full angle determination in all directions (0 to 360 degrees), use [`math:arctan2()`](https://library.humio.com/data-analysis/functions-math-arctan2.html) instead. 

The [`math:arctan()`](https://library.humio.com/data-analysis/functions-math-arctan.html) function is often used with [`math:rad2deg()`](https://library.humio.com/data-analysis/functions-math-rad2deg.html) when angles need to be displayed in degrees. For applications requiring angles in all directions, consider using [`math:arctan2()`](https://library.humio.com/data-analysis/functions-math-arctan2.html) instead.
