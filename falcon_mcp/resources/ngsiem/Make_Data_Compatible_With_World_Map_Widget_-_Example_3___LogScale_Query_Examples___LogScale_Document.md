# Make Data Compatible With World Map Widget - Example 3 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-worldmap-latency-3.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Make Data Compatible With World Map Widget - Example 3

Make data compatible with [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html) using the [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function and average latency as magnitude of the points 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    worldMap(ip=myIpField, magnitude=avg(latency))

### Introduction

The [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html) displays geographical data on a world map. Typical fields used in the [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html) are lat, lon, geohash, precision, and magnitude. 

The [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function is a helper function to produce data compatible with the [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html). 

In this example, the `worldMap` function is used with the `magnitude` function to calculate the magnitude (weight) of each bucket. This value is used to determine the size or opacity of the world map markers. 

The [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function will automatically bucket the locations to reduce the number of points. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         worldMap(ip=myIpField, magnitude=avg(latency))

Plots IP addresses on the world map and uses average latency as magnitude of the points. 

  3. Event Result set.




### Summary and Results

The query with the [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function is used to visualize and present location data, in this example IP addresses and the average latency, in a [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html). The query is useful, for example, to identify performance patterns based on latency across different regions, or to identify potential network bottlenecks or performance issues in specific locations. 

Visualization of IP addresses and average latency values on a global map is useful in network monitoring and performance analysis to quickly spot geographical patterns in network latency. Larger average latency values will create bigger/more intense points on the world map.
