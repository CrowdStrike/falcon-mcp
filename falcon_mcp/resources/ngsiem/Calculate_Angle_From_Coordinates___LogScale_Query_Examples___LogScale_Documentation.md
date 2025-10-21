# Calculate Angle From Coordinates | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-matharctan2-calculate-angle.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Angle From Coordinates

Calculate the angle to a point using the [`math:arctan2()`](https://library.humio.com/data-analysis/functions-math-arctan2.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 1.0
    y := 1.0
    | math:arctan2(y=y, x=x, as=angle)

### Introduction

The [`math:arctan2()`](https://library.humio.com/data-analysis/functions-math-arctan2.html) function can be used to calculate the angle in radians between the positive x-axis and a point in a 2D plane (two-dimensional coordinate system like a graph with x and y axes. It takes two parameters: [_`y`_](https://library.humio.com/data-analysis/functions-math-arctan2.html#query-functions-math-arctan2-y) and [_`x`_](https://library.humio.com/data-analysis/functions-math-arctan2.html#query-functions-math-arctan2-x), representing the point's vertical and horizontal positions, and returns the angle in the range `-π` to `π` radians. 

In this example, the [`math:arctan2()`](https://library.humio.com/data-analysis/functions-math-arctan2.html) function is used to calculate the angle to a point on a coordinate graph where both `x` and `y` equal `1.0`, similar to finding the angle of a line drawn from the center (0,0) to a point on a graph paper. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 1.0
         y := 1.0

Assigns the coordinates (`1.0`, `1.0`) to the fields x and y. This point lies at `45` degrees (π/4 radians) from the positive x-axis. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:arctan2(y=y, x=x, as=angle)

Calculates the angle in radians from the positive x-axis to the point (x, y) and returns the result in a field named angle. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-arctan2.html#query-functions-math-arctan2-as) parameter is not specified, the result is returned in a field named _arctan2 as default. 

  4. Event Result set.




### Summary and Results

The query is used to calculate the angle to a point in a 2D plane, which is essential in various geometric calculations, direction finding, and vector operations. 

This query is useful, for example, to determine directions in navigation systems, calculate angles in geometric applications, or analyze circular motion patterns. 

Sample output from the incoming example data: 

angle  
---  
0.7853981633974483  
  
The result shows that the angle to the point (1.0, 1.0) is approximately 0.7854 radians (π/4 radians or 45 degrees). The [`math:arctan2()`](https://library.humio.com/data-analysis/functions-math-arctan2.html) function returns angles in the range -π to π radians, with positive angles measured counterclockwise from the x-axis. 

Note that [`math:arctan2()`](https://library.humio.com/data-analysis/functions-math-arctan2.html) differs from regular arctangent by considering the quadrant of the point, using both x and y coordinates to determine the correct angle. For example, points (1,1) and (-1,-1) have the same arctangent but different arctan2 values (π/4 and -3π/4 respectively).
