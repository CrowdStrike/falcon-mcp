# Rounding to n Decimal Places | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-functions-round-decimalpoint.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Rounding to n Decimal Places

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    format("%.2f", field=value)

### Introduction

To round a number to a specific number of decimal points, use [`format()`](https://library.humio.com/data-analysis/functions-format.html) rather than [`round()`](https://library.humio.com/data-analysis/functions-round.html). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         format("%.2f", field=value)

Rounds the field value to two decimal places. 

  3. Event Result set.




### Summary and Results

When using [`format()`](https://library.humio.com/data-analysis/functions-format.html), rounding is performed using standard math rules. The [`format()`](https://library.humio.com/data-analysis/functions-format.html) rounds a number to a specific decimal accuracy. 

### Note

To round a number to the nearest integer, use [`round()`](https://library.humio.com/data-analysis/functions-round.html). See [Basic Rounding](examples-functions-round-basic.html "Basic Rounding").
