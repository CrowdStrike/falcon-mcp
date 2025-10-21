# Basic Rounding | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-functions-round-basic.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Basic Rounding

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    round(myvalue)

### Introduction

The [`round()`](https://library.humio.com/data-analysis/functions-round.html) function rounds a number to the nearest integer (whole number) using standard math rules. Numbers greater than 0.5 are rounded up, numbers lower than 0.5 are rounded down. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         round(myvalue)

Rounds the number in myvalue. 

  3. Event Result set.




### Summary and Results

The query is used to round a floating point number to the nearest integer. Rounding is used to simplify numbers. The benefit to rounding is that it returns numbers that are easier to work with. 

### Note

To format a number, or round to a specific decimal accuracy, use [`format()`](https://library.humio.com/data-analysis/functions-format.html). See [Rounding to n Decimal Places](examples-functions-round-decimalpoint.html "Rounding to n Decimal Places").
