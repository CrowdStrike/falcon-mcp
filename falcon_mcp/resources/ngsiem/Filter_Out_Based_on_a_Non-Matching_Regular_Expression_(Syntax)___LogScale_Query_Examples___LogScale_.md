# Filter Out Based on a Non-Matching Regular Expression (Syntax) | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-negative-regex-filter.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter Out Based on a Non-Matching Regular Expression (Syntax)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    method != /(PUT
    | POST)/

### Introduction

Typically a regular expression is used to filter events based on a value that the regular expression matches. The opposite can also be achieved, filtering events by those that do not match the regular expression. 

This example searches weblog data looking for events where the method does not match a specified value. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         method != /(PUT
         | POST)/

This line performs a negative regular expression match, returning only the events where the method does not match either `PUT` or `POST`. 

  3. Event Result set.




### Summary and Results

This format of the query can be a simple way to perform a negative regular expression match, or more specifically, returning a list of the events that do not match the given regular expression.
