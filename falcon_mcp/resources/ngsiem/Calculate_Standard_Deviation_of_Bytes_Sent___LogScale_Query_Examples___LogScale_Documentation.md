# Calculate Standard Deviation of Bytes Sent | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-stddev-bytes.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Standard Deviation of Bytes Sent

Calculate standard deviation of Bytes sent using the [`stdDev()`](https://library.humio.com/data-analysis/functions-stddev.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    stdDevBytes := stdDev(field=bytes_sent)

### Introduction

The [`stdDev()`](https://library.humio.com/data-analysis/functions-stddev.html) function can be used to measure the amount of variation in a set of numeric values from their average value. 

In this example, the [`stdDev()`](https://library.humio.com/data-analysis/functions-stddev.html) is used to calculate how much the number of bytes sent varies from the mean value. 

Example incoming data might look like this: 

@timestamp| endpoint| bytes_sent| status_code  
---|---|---|---  
1686837825000| /api/users| 1450| 200  
1686837826000| /api/products| 8920| 200  
1686837827000| /api/orders| 1670| 200  
1686837828000| /api/payment| 12900| 500  
1686837829000| /api/users| 1560| 200  
1686837830000| /api/items| 780| 200  
1686837831000| /api/orders| 9340| 200  
1686837832000| /api/checkout| 9230| 200  
1686837833000| /api/products| 1340| 200  
1686837834000| /api/users| 4450| 200  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         stdDevBytes := stdDev(field=bytes_sent)

Calculates the standard deviation of values in the bytes_sent field and assigns the result to a new field named stdDevBytes. 

The [`stdDev()`](https://library.humio.com/data-analysis/functions-stddev.html) function measures how widely the values are dispersed from their average value. 

  3. Event Result set.




### Summary and Results

The query is used to understand the variability in the size of data being transferred. 

This query is useful, for example, to identify unusual patterns in data transfer sizes, establish normal ranges for network traffic, or detect anomalies in data transmission. 

Sample output from the incoming example data: 

stdDevBytes  
---  
4289.32  
  
Note that the result is a single value representing the standard deviation. A higher value indicates greater variation in the data. 

The unit of measurement is the same as the input field (bytes in this case).
