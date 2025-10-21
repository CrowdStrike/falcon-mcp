# Determine a Score Based on Field Value | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-if-4.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Determine a Score Based on Field Value

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{Conditional} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    percentile(filesize, percentiles=[40,80],as=score)
    | symbol := if(filesize > score_80, then=":+1:", else=if(filesize > score_40, then="so-so", else=":-1:"))

### Introduction

When summarizing and displaying data, it may be necessary to derive a score or validity based on a test value. This can be achieved using [`if()`](https://library.humio.com/data-analysis/functions-if.html) by creating the score value if the underlying field is over a threshold value. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{Conditional} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         percentile(filesize, percentiles=[40,80],as=score)

Calculates the [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) for the filesize field and determines what filesize that is above 40% of the overall event set, and 80% of the overall event set. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{Conditional} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | symbol := if(filesize > score_80, then=":+1:", else=if(filesize > score_40, then="so-so", else=":-1:"))

Compares whether the filesize is greater than 80% of the events, setting symbol to `:+1:`. Because [`if()`](https://library.humio.com/data-analysis/functions-if.html) functions can be embedded, the [_`else`_](https://library.humio.com/data-analysis/functions-if.html#query-functions-if-else) parameter is another [`if()`](https://library.humio.com/data-analysis/functions-if.html) statement that sets symbol to `so-so` if the size is greater than 40%, or `:+1:` otherwise. 

  4. Event Result set.




### Summary and Results

Using [`if()`](https://library.humio.com/data-analysis/functions-if.html) is the best way to make conditional choices about values. The function has the benefit of being able to be embedded into other statements, unlike `case`.
