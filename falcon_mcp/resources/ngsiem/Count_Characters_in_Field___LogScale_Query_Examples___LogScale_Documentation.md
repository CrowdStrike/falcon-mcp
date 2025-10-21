# Count Characters in Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-length-rawstring.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Count Characters in Field

Count the number of characters in a field using the [`length()`](https://library.humio.com/data-analysis/functions-length.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    length(@rawstring)

### Introduction

The [`length()`](https://library.humio.com/data-analysis/functions-length.html) function can be used to count the number of characters in a field. It counts all characters, including spaces and special characters. 

In this example, the [`length()`](https://library.humio.com/data-analysis/functions-length.html) function is used to count the number of characters in the @rawstring field and output the result in a field named _length. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         length(@rawstring)

Counts the number of characters in the field @rawstring field and outputs the result in a field named _length. This count includes all visible characters, spaces, and punctuation marks in the log entry. 

Using the [_`as`_](https://library.humio.com/data-analysis/functions-length.html#query-functions-length-as) parameter, it is also possible to define another output field, for example, rawLength, if adding the following: 

`length(@rawstring, as="rawLength")`

  3. Event Result set.




### Summary and Results

The query is used to make a count of all characters (all visible characters, spaces, and punctuation marks) in a log entry. Making a count of all characters is useful for managing and analyzing, for example, security logs, ensuring complete data capture for threat detection and incident response.
