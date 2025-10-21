# Make Data Compatible With World Map Widget - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-worldmap-geocoordinates-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Make Data Compatible With World Map Widget - Example 2

Make data compatible with [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html) using the [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function and geo-coordinates 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    worldMap(lat=location.latitude, lon=location.longitude)

### Introduction

The [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html) displays geographical data on a world map. Typical fields used in the [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html) are lat, lon, geohash, precision, and magnitude. 

The [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function is a helper function to produce data compatible with the [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html). 

In this example, the [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function takes either IP addresses or geo-coordinates (latitude/longitude) as input and buckets points using a geohashing algorithm. 

The [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function will automatically bucket the locations to reduce the number of points. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         worldMap(lat=location.latitude, lon=location.longitude)

Plots existing geo-coordinates (latitude/longitude) on the world map. 

  3. Event Result set.




### Summary and Results

The query with the [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function is used to visualize and present location data, in this case IP addresses and their exact geo-coordinates, in a [World Map](https://library.humio.com/data-analysis/widgets-worldmap.html). 

Visualization of IP addresses and their exact geo-coordinates on a global map is more accurate and useful in cases where high precision is required, for example for physical asset tracking.
