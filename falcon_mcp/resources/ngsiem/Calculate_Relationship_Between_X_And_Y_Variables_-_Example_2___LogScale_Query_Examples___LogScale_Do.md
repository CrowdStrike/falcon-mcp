# Calculate Relationship Between X And Y Variables - Example 2
      
     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-linreg-bucket-correlation.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Relationship Between X And Y Variables - Example 2 

Calculate the linear relationship between server load and total response size using the [`linReg()`](https://library.humio.com/data-analysis/functions-linreg.html) function with [`bucket()`](https://library.humio.com/data-analysis/functions-bucket.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    bucket(function=[ sum(bytes_sent, as=x), avg(server_load_pct, as=y) ])
    | linReg(x=x, y=y)

### Introduction

The [`linReg()`](https://library.humio.com/data-analysis/functions-linreg.html) function can be used to calculate a linear relationship between two variables by using least-squares fitting. The function is used to analyze different performance relationships in a system, for example: response size and transmission time, server load and total response size, or server load and request types. 

In this example, the [`linReg()`](https://library.humio.com/data-analysis/functions-linreg.html) function is used to calculate the linear relationship between bytes_sent (`x` variable) and server_load_pct (`y` variable). The example shows the relationship between server load percentage and total response size across time. 

Example incoming data might look like this: 

@timestamp| bytes_sent| server_load_pct  
---|---|---  
2024-01-15T09:00:00Z| 156780| 45.2  
2024-01-15T09:05:00Z| 234567| 52.8  
2024-01-15T09:10:00Z| 189234| 48.6  
2024-01-15T09:15:00Z| 345678| 65.3  
2024-01-15T09:20:00Z| 123456| 42.1  
2024-01-15T09:25:00Z| 278901| 58.7  
2024-01-15T09:30:00Z| 198765| 51.4  
2024-01-15T09:35:00Z| 287654| 59.2  
2024-01-15T09:40:00Z| 167890| 46.8  
2024-01-15T09:45:00Z| 298765| 61.5  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         bucket(function=[ sum(bytes_sent, as=x), avg(server_load_pct, as=y) ])

Buckets the data points by time, then calculates the sum of bytes sent for each bucket returning the result in a field named x, and calculates the average server load percentage for each bucket returning the result in a field named y. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | linReg(x=x, y=y)

Correlates x with y, showing the relationship between the variables `x` and `y` and outputs the results in fields named _slope (slope value),_intercept (intercept value),_r2 (adjusted R-squared value), and _n (number of data points). These four key values indicate relationship strength and reliability. 

  4. Event Result set.




### Summary and Results

The query is used to calculate a linear relationship between bytes_sent (`x` variable) and server_load_pct (`y` variable). 

Calculating the relationship between server load percentage and total response size is useful to identify different operational patterns, such as, for example, performance bottlenecks, resource allocation issues, or to identify system optimization opportunities. 

Sample output from the incoming example data: 

_slope| _intercept| _r2| _n  
---|---|---|---  
0.00010617525557193158| 28.934098111407938| 0.991172367336835| 10  
  
_slope is the rate of change between server load and response size. 

_intercept is the baseline relationship value. 

_r2 is the statistical accuracy of the linear model. 

_n is the total number of data points analyzed.
