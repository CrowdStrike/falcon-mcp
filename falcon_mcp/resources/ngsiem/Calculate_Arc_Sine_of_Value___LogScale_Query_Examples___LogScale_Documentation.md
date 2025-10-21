# Calculate Arc Sine of Value | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-matharcsin-calculate-arcsine.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Arc Sine of Value

Calculate the arc sine using the [`math:arcsin()`](https://library.humio.com/data-analysis/functions-math-arcsin.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 0.5
    | math:arcsin(x, as=angle)

### Introduction

The [`math:arcsin()`](https://library.humio.com/data-analysis/functions-math-arcsin.html) function can be used to calculate the inverse sine (arc sine) of a value, returning the angle in radians. The function accepts values between `-1` and `1`, and returns an angle in the range `-π/2` to `π/2` radians (from -90 to 90 degrees). 

In this example, the [`math:arcsin()`](https://library.humio.com/data-analysis/functions-math-arcsin.html) function is used to calculate the arc sine of `0.5`, which represents the angle whose sine is `0.5` (30 degrees or π/6 radians). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 0.5

Assigns the value `0.5` to field x. This value represents the sine ratio of an angle, which should result in an angle of π/6 radians (30 degrees). 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:arcsin(x, as=angle)

Calculates the arc sine of the value in field x and returns the result in radians in a field named angle. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-arcsin.html#query-functions-math-arcsin-as) parameter is not specified, the result is returned in a field named _arcsin as default. 

  4. Event Result set.




### Summary and Results

The query is used to find angles from sine ratios, which is useful in trigonometric calculations and in determining angles when working with perpendicular components of vectors. 

This query is useful, for example, to calculate angles from height-to-hypotenuse ratios, determine elevation angles, or analyze trigonometric relationships. 

Sample output from the incoming example data: 

angle  
---  
0.5235987755982989  
  
The result shows that the arc sine of `0.5` is approximately `0.5236 radians` (π/6 radians or 30 degrees). This means when the sine of an angle is `0.5`, the angle is `30` degrees. 

Note that the [`math:arcsin()`](https://library.humio.com/data-analysis/functions-math-arcsin.html) function only accepts input values between `-1` and `1` (inclusive) and returns values between `-π/2` and `π/2` radians (-90 to 90 degrees). Values outside this range will result in an error. 

The [`math:arcsin()`](https://library.humio.com/data-analysis/functions-math-arcsin.html) function is often used with [`math:rad2deg()`](https://library.humio.com/data-analysis/functions-math-rad2deg.html) when angles need to be displayed in degrees. Consider creating a dashboard comparing different inverse trigonometric functions ([`math:arcsin()`](https://library.humio.com/data-analysis/functions-math-arcsin.html), [`math:arccos()`](https://library.humio.com/data-analysis/functions-math-arccos.html), [`math:arctan()`](https://library.humio.com/data-analysis/functions-math-arctan.html)) to understand their relationships.
