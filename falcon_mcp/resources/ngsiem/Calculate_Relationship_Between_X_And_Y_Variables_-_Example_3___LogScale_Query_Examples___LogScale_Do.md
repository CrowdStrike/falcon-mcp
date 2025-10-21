# Calculate Relationship Between X And Y Variables - Example 3
      
     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-linreg-groupby-correlation.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Relationship Between X And Y Variables - Example 3 

Calculate the linear relationship between server load and each of several types of request types using the [`linReg()`](https://library.humio.com/data-analysis/functions-linreg.html) function with [`bucket()`](https://library.humio.com/data-analysis/functions-bucket.html) and [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    bucket(function=[ avg(server_load_pct, as=y), groupBy(request_type, function=count(as=x)) ])
    | groupBy(request_type, function=linReg(x=x, y=y))

### Introduction

The [`linReg()`](https://library.humio.com/data-analysis/functions-linreg.html) function can be used to calculate a linear relationship between two variables by using least-squares fitting. The function is used to analyze different performance relationships in a system, for example: response size and transmission time, server load and total response size, or server load and request types. 

In this example, the [`linReg()`](https://library.humio.com/data-analysis/functions-linreg.html) function is used to calculate the linear relationship between request_type (`x` variable) and server_load_pct (`y` variable). The example shows the relationship between server load and each of several types of HTTP request types across time. 

Example incoming data might look like this: 

@timestamp| server_load_pct| request_type  
---|---|---  
2024-01-15T09:00:00.000Z| 45.2| GET  
2024-01-15T09:00:00.000Z| 45.2| POST  
2024-01-15T09:00:00.000Z| 45.2| GET  
2024-01-15T09:05:00.000Z| 52.8| GET  
2024-01-15T09:05:00.000Z| 52.8| PUT  
2024-01-15T09:05:00.000Z| 52.8| POST  
2024-01-15T09:10:00.000Z| 48.6| GET  
2024-01-15T09:10:00.000Z| 48.6| GET  
2024-01-15T09:10:00.000Z| 48.6| DELETE  
2024-01-15T09:15:00.000Z| 65.3| POST  
2024-01-15T09:15:00.000Z| 65.3| POST  
2024-01-15T09:15:00.000Z| 65.3| GET  
2024-01-15T09:20:00.000Z| 42.1| GET  
2024-01-15T09:20:00.000Z| 42.1| PUT  
2024-01-15T09:20:00.000Z| 42.1| GET  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         bucket(function=[ avg(server_load_pct, as=y), groupBy(request_type, function=count(as=x)) ])

Buckets the data points by time, then calculates the average server load for each time bucket returning the result in a field named y. It also groups the request types in a field named request_type and makes a count of requests by type in each time bucket returning the result in a field named x. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(request_type, function=linReg(x=x, y=y))

Correlates x with y, showing the relationship between the variables `x` and `y` for each HTTP request type and outputs the results in fields named _slope (slope value),_intercept (intercept value),_r2 (adjusted R-squared value), and _n (number of data points). These four key values indicate relationship strength and reliability. 

  4. Event Result set.




### Summary and Results

The query is used to analyze how different HTTP request types affect server load. The analysis helps identify which HTTP request types have the strongest impact on server performance. 

Sample output from the incoming example data: 

request_type| _slope| _intercept| _r2| _n  
---|---|---|---|---  
DELETE| <no value>| <no value>| <no value>| <no value>  
GET| -13.749999999999941| 72.7999999999999| 0.5941824574313592| 5  
POST| 16.29999999999992| 32.70000000000012| 0.7196207242484238| 3  
PUT| <no value>| <no value>| <no value>| <no value>  
  
_slope is the impact rate of request volume on server load. 

_intercept is the baseline server load when there are no requests of a specific type. 

_r2 is the statistical accuracy of the relationship. 

_n is the total number of data points analyzed.
