# Find Range of CPU Usage by Host | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-range-groupby-cpu.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

##  Find Range of CPU Usage by Host

Find numeric range between the smallest and largest numbers in specified field using the [`range()`](https://library.humio.com/data-analysis/functions-range.html) function with [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    groupBy([host], function=range(cpu_usage))

### Introduction

A numeric range is the difference between the highest and lowest values in a specified numeric field across a set of events. The [`range()`](https://library.humio.com/data-analysis/functions-range.html) function can be used to calculate this difference and it works with both integer and floating-point fields. 

In this example, the [`range()`](https://library.humio.com/data-analysis/functions-range.html) function is used to find the CPU usage by host by finding the range of the values in the field cpu_usage. 

Example incoming event data might look like this: 

timestamp| host| cpu_usage  
---|---|---  
2025-04-30T07:00:00Z| host1.com| 50  
2025-04-30T07:01:00Z| host1.com| 75  
2025-04-30T07:02:00Z| host1.com| 95  
2025-04-30T07:03:00Z| host1.com| 65  
2025-04-30T07:00:00Z| host2.com| 50  
2025-04-30T07:01:00Z| host2.com| 70  
2025-04-30T07:02:00Z| host2.com| 55  
2025-04-30T07:03:00Z| host2.com| 65  
2025-04-30T07:00:00Z| host3.com| 25  
2025-04-30T07:01:00Z| host3.com| 100  
2025-04-30T07:02:00Z| host3.com| 45  
2025-04-30T07:03:00Z| host3.com| 80  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy([host], function=range(cpu_usage))

Groups events by host name in the field host ([host]), then calculates the range (the difference) between highest CPU usage value and lowest CPU usage value for each host, returning the results in a new field named _range. 

The [`range()`](https://library.humio.com/data-analysis/functions-range.html) function always returns a single number (the difference between maximum and minimum). 

  3. Event Result set.




### Summary and Results

The query is used to find the CPU usage by host. The smaller the range (0-20), the more stable is the system. 

Sample output from the incoming example data: 

host| _range  
---|---  
host1.com| 45  
host2.com| 20  
host3.com| 75
