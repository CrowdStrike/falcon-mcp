# Format Duration Into Human Readable String | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-formatduration-human.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Format Duration Into Human Readable String

Format a duration into a human readable string using the [`formatDuration()`](https://library.humio.com/data-analysis/functions-formatduration.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    formatDuration(duration, precision=3)

### Introduction

The [`formatDuration()`](https://library.humio.com/data-analysis/functions-formatduration.html) function is used to format a duration into a human readable string. A duration string is a possibly signed sequence of decimal numbers, each with an optional fraction and an optional unit suffix. 

In this example, the [`formatDuration()`](https://library.humio.com/data-analysis/functions-formatduration.html) function is used to format the sequences of decimal numbers into a human readable string with limited precision. Note that the value of the field being formatted must always be an integer. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         formatDuration(duration, precision=3)

Formats a duration into a string. The duration field contains the value in milliseconds. 

For example, an input event with the field duration with the value `23452553` with a default interpretation of the source value as milliseconds, results in the field duration having the value `6h30m52s553ms`. 

The optional _`precision`_ parameter specifies the number of time units to include. In this example, precision equals `3`, which means, that it shows three units: hours, minutes, and seconds. If `precision=2` is used, it may show `6h30m` instead. 

  3. Event Result set.




### Summary and Results

The query is used to format the sequences of decimal numbers into a human readable string to improve readability of log entries with duration fields. The value of the field being formatted must always be an integer. If not an integer, you can use [`round()`](https://library.humio.com/data-analysis/functions-round.html) or [`format()`](https://library.humio.com/data-analysis/functions-format.html) to create an integer value. 

It is also possible to use the [`formatDuration()`](https://library.humio.com/data-analysis/functions-formatduration.html) function in combination with [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) to create a new formatted field: 
    
    
    formatDuration(processingTime, precision=3)
    |eval(formattedDuration = formatDuration(duration))
