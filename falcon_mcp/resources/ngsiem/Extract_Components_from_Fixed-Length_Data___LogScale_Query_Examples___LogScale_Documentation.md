# Extract Components from Fixed-Length Data | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-textsubstring-extract-fixed-length-data.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Components from Fixed-Length Data

Extract Components from Variable Length Data using the [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function with regex 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    data = /^(?<id>\d{2})(?<payloadLength>\d{4})(?<remaining>.+)$/
    payload := text:substring(remaining, end=payloadLength)
    transactionID := text:substring(remaining, begin=payloadLength)

### Introduction

The [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function combined with regular expressions can be used to parse and extract components from variable-length data strings. 

In this example, the [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function is used with a regular expression to break down variable-length data strings into their component parts based on predefined positions and lengths. 

Example incoming data might look like this: 

@timestamp| data  
---|---  
2025-08-06T10:15:00.000Z| 6800091A3C5B78F4468  
2025-08-06T10:15:01.000Z| 420004E2E228930  
2025-08-06T10:15:02.000Z| 7800123ABC45DE6789  
2025-08-06T10:15:03.000Z| 910007DEFG89HI1234  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         data = /^(?<id>\d{2})(?<payloadLength>\d{4})(?<remaining>.+)$/

Uses a regular expression to parse the data field with these capture groups: 

     * id: `^` matches the start of the string, followed by `\d{2}` which captures exactly two digits. 

     * payloadLength: `\d{4}` captures exactly four digits after the id. 

     * remaining: `.+` captures one or more of any character until `$` (end of string). 

The regex pattern ensures that the entire string matches this format with no additional characters before or after, due to the `^` (start) and `$` (end) anchors. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         payload := text:substring(remaining, end=payloadLength)

Extracts a substring from the remaining field starting at position 0 and ending at the position specified by payloadLength (extracted by the regular expression in the previous line) and returns the result in a new field named payload. 

The [_`end`_](https://library.humio.com/data-analysis/functions-text-substring.html#query-functions-text-substring-end) parameter specifies the exclusive end position of the substring. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         transactionID := text:substring(remaining, begin=payloadLength)

Extracts a substring from the remaining field starting at the position specified by payloadLength until the end of the string and returns the result in a new field named transactionID. 

The [_`begin`_](https://library.humio.com/data-analysis/functions-text-substring.html#query-functions-text-substring-begin) parameter specifies the inclusive start position of the substring. 

  5. Event Result set.




### Summary and Results

The query is used to parse variable-length data strings where different portions of the string represent specific pieces of information in a predefined format. 

This query is useful, for example, to process type-length-value like data formats, which are common in network protocols, or any variable-length formatted messages where different segments of the data have specific meanings based on their position and length. 

Sample output from the incoming example data: 

data| id| payload| payloadLength| remaining| transactionID  
---|---|---|---|---|---  
6800091A3C5B78F4468| 68| 1A3C5B78F| 0009| 1A3C5B78F4468| 4468  
420004E2E228930| 42| E2E2| 0004| E2E228930| 28930  
7800123ABC45DE6789| 78| 3ABC45DE6789| 0012| 3ABC45DE6789| <no value>  
910007DEFG89HI1234| 91| DEFG89H| 0007| DEFG89HI1234| I1234  
  
Note that the payloadLength field determines exactly how many characters to extract for the payload field. When the payloadLength equals the length of remaining, then the transactionID field will be empty. 

Also note that the payload and transactionID fields together make up the complete remaining field.
