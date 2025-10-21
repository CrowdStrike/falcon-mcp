# Count Characters Including Emojis in String | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-textlength-count-characters-emojis.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Count Characters Including Emojis in String

Get string length including emojis using the [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    text:length(CommandLine)

### Introduction

The [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html) function can be used to count the number of characters in a string, including special characters and emojis. 

In this example, the [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html) function is used to count characters in a command line string that contains emojis. 

Example incoming data might look like this: 

CommandLine=🎯data_exfil.zip📦&rarr;💾backup_srv🔓admin123  
---  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         text:length(CommandLine)

Counts the total number of characters in the CommandLine field, counting each emoji as a single character, and returns the result in a new field named _length. 

  3. Event Result set.




### Summary and Results

The query is used to determine the exact length of strings that may contain special characters or emojis. 

This query is useful, for example, to analyze command line lengths, validate string sizes, or identify unusually long commands that might indicate malicious activity. 

Sample output from the incoming example data: 

_length  
---  
38  
  
Note that each emoji is counted as a single character in the total length calculation.
