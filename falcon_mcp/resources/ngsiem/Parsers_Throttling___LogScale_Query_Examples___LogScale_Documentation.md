# Parsers Throttling | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-parsers.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Parsers Throttling

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    #kind=logs class=/ParserLimitingJob/ "Top element for parser id"
    pct:=100*costSum/threshold
    timeChart(function=max(pct), minSpan=10s)

### Introduction

Throttling is used to maintain the optimal performance and reliability of the system, as throttling limits the number of API calls or operations within a time window to prevent the overuse of resources. 

In this example, the [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function is used to show how close (in percentage) the system has been to start throttling any parser. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #kind=logs class=/ParserLimitingJob/ "Top element for parser id"

Filters on all logs in humio that are tagged with `kind` equal to `logs` and then returns the events where the class field has values containing `/ParserLimitingJob/`, and where the logline contains the string `Top element for parser id`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         pct:=100*costSum/threshold

Calculates the percentage of the values in the field costSum divided with values in the field threshold and returns the results in a new field named pct. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(function=max(pct), minSpan=10s)

Shows the calculated sum of the max values in the field pct in percentage in spans of 10 sec in a timechart. 

  5. Event Result set.




### Summary and Results

The query is used to show how close (in percentage) the system has been to start throttling any parser.
