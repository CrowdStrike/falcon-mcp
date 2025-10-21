# Replace Word or Substring With Another | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-replace-spelling-mistake.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Replace Word or Substring With Another

Replace a word or substring with another in an event set using the [`replace()`](https://library.humio.com/data-analysis/functions-replace.html) function with a regular expression 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    replace(regex=propperties, with=properties)

### Introduction

The [`replace()`](https://library.humio.com/data-analysis/functions-replace.html) function can be used to replace each substring of the specified fields value that matches a given regular expression with the given replacement. 

In this example, the [`replace()`](https://library.humio.com/data-analysis/functions-replace.html) function is used to correct a spelling mistake. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         replace(regex=propperties, with=properties)

Replaces the word `propperties` with the word `properties`. 

  3. Event Result set.




### Summary and Results

The query is used to correct spelling mistakes in an event set. Changing words or other substrings like this with a regular expression is useful in many situations, where it is necessary to make quick changes of field values.
