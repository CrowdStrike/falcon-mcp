# Make Data Compatible With World Map Widget - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-worldmap-magnitude-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Make Data Compatible With World Map Widget - Example 1

Make data compatible with [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html) using the [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function and magnitude 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    worldMap(ip=myIpField)

### Introduction

The [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html) displays geographical data on a world map. Typical fields used in the [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html) are lat, lon, geohash, precision, and magnitude. 

The [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function is a helper function to produce data compatible with the [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html). 

In this example, the [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function takes IP addresses and buckets points using the magnitude, the number of observations in each bucket. 

The [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function will automatically bucket the locations to reduce the number of points. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         worldMap(ip=myIpField)

Plots IP addresses on the world map. `ip=myIpField` specifies which field contains IP addresses. The magnitude is the number of observations in each bucket (the default) - the count of IP addresses per location. 

  3. Event Result set.




### Summary and Results

The query with the [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function is used to visualize and present location data, in this case IP addresses and their geo-coordinates, in a [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html). 

Visualization of IP addresses on a global map is useful, for example, to show concentration/density of IPs by location, to visualize attack sources, to monitor user access locations, to track network traffic origins, or identify suspicious geographic patterns.
