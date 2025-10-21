# Convert Rate Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-unitconvert-rate-hits.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Convert Rate Values

Convert rate values to hits using the [`unit:convert()`](https://library.humio.com/data-analysis/functions-unit-convert.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    | unit:convert(rate, as="rate", unit="hits")

### Introduction

The [`unit:convert()`](https://library.humio.com/data-analysis/functions-unit-convert.html) function can be used to convert values between different units of measurement, including converting rate values to hits. 

The following rate conversions are supported: `s`, `sec`, `m`, `min`, `h`, `hour`, `d`, `day`, `w`, `week`. 

Note that any unit is supported in LogScale. 

In this example, the [`unit:convert()`](https://library.humio.com/data-analysis/functions-unit-convert.html) function is used to convert rate values to hits. The function parses a value into a number by removing the unit. 

Example incoming data might look like this: 

@timestamp| service| rate  
---|---|---  
2023-08-06T10:00:00Z| api| 150hits/min  
2023-08-06T10:01:00Z| api| 25hits/s  
2023-08-06T10:02:00Z| api| 3600hits/h  
2023-08-06T10:03:00Z| api| 80hits/min  
2023-08-06T10:04:00Z| api| 40hits/s  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | unit:convert(rate, as="rate", unit="hits")

Converts the values in the rate field to hits. The [_`as`_](https://library.humio.com/data-analysis/functions-unit-convert.html#query-functions-unit-convert-as) parameter specifies that it is a conversion of a rate type measurement, and the [_`unit`_](https://library.humio.com/data-analysis/functions-unit-convert.html#query-functions-unit-convert-unit) parameter with value `hits` enforces that the desired output unit is actually hits. 

Note that since the unit in this case starts with a letter `h` from the supported prefixes, it will be interpreted as the prefix `h` (102) and unit `hits`. 

  3. Event Result set.




### Summary and Results

The query is used to convert rate values from different time units (per second, per minute, per hour) to a standardized hits per second format. 

This query is useful, for example, to normalize different rate measurements for consistent monitoring and analysis. 

Note that any unit is supported in LogScale. 

Sample output from the incoming example data: 

@timestamp| service| rate  
---|---|---  
2023-08-06T10:00:00Z| api| 2.5  
2023-08-06T10:01:00Z| api| 25  
2023-08-06T10:02:00Z| api| 1  
2023-08-06T10:03:00Z| api| 1.33  
2023-08-06T10:04:00Z| api| 40
