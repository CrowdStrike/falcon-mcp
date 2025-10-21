# Calculate the Mean of CPU Time | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-avg-format-cpu.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate the Mean of CPU Time

Calculate the sum of all numbers (mean) of the CPU time 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2>Augment Data] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    avg(field=cputimeNanos)
    | cputime := (_avg/1000000)
    | format("%,.2f", field=_avg, as=_avg)

### Introduction

CPU time is the exact amount of time that the CPU has spent processing data for a specific program or process. In this example the [`avg()`](https://library.humio.com/data-analysis/functions-avg.html) function is used to calculate the sum of all numbers; the mean of the CPU Time. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2>Augment Data] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         avg(field=cputimeNanos)

Calculates the mean of the field cputimeNanos. This can be run in the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) system repository to get the average time spent in nanoseconds for different activities. The mean is calculated by summing all of the values in the cputimeNanos field and dividing by the number of values across all events. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2>Augment Data] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | cputime := (_avg/1000000)

Calculates the average CPU time to milliseconds to make it easier to read. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2>Augment Data] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | format("%,.2f", field=_avg, as=_avg)

Overwrites the field _avg to contain the _avg field to show only two decimals. 

  5. Event Result set.




### Summary and Results

The query is used to averaging the field containing the CPU value. This value is then piped to the [`format()`](https://library.humio.com/data-analysis/functions-format.html) function, which provides a formatting code — how the field value should be formatted. In this example, it formats the value to two decimal. Calculation of CPU times is useful to determine processing power - for example if troubleshooting a system with high CPU usage. 

Sample output from the incoming example data: 

_avg  
---  
0.14
