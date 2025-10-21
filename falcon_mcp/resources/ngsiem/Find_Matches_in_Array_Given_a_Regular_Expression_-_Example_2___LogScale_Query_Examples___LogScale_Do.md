# Find Matches in Array Given a Regular Expression - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-regex-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Matches in Array Given a Regular Expression - Example 2

Use regular expressions to search for and match specific patterns ignoring case in flat arrays 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Array Manipulation]] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:regex("responses[]", regex="bear$", flags="i")

### Introduction

A regular expression is a form of advanced searching that looks for specific patterns, as opposed to certain terms and phrases. You can use a regular expression to find all matches in an array. 

In this example, the regular expression is used to search for patterns where the value `bear` appears at the end of a value in an array element, ignoring the case. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Array Manipulation]] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:regex("responses[]", regex="bear$", flags="i")

Searches in the responses array for values that begins with `bear`, ignoring the case (due to the [`i`](https://library.humio.com/data-analysis/functions-array-regex.html#query-functions-array-regex-flags-value-i) flag). 

  3. Event Result set.




### Summary and Results

The queries using the regex expression are used to quickly search and return results for specific values in arrays. Regular expressions are useful when searching for different strings containing the same patterns; such as social security numbers, URLs, email addresses, and other strings that follow a specific pattern.
