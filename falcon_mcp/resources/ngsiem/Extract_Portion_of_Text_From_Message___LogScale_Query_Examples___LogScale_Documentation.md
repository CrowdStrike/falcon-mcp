# Extract Portion of Text From Message | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-textsubstring-extract-portion-length.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Portion of Text From Message

Extract specific characters from a message using the [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function with [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    text:substring(message, begin=4, end=text:length(message) - 4)

### Introduction

The [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function can be used with [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html) to extract a specific portion of text from a string. The [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html) function returns the total number of characters in a string. 

In this example, the [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function is used with [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html) to extract a portion of text from messages. It removes a certain number of characters from each end of the string using the _`begin`_ and _`end`_ parameters. 

Example incoming data might look like this: 

@timestamp| message  
---|---  
2025-08-06T10:15:00.000Z| The quick brown fox jumps over the lazy dog  
2025-08-06T10:15:01.000Z| Pack my box with five dozen liquor jugs  
2025-08-06T10:15:02.000Z| How vexingly quick daft zebras jump  
2025-08-06T10:15:03.000Z| The five boxing wizards jump quickly  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         text:substring(message, begin=4, end=text:length(message) - 4)

Extracts characters from the [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) field by: 

     * Starting at position 4 (the 5th character) 

     * Ending 4 characters before the end of the string, calculated by [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html)

  3. Event Result set.




### Summary and Results

The query is used to extract a portion of text by specifying start and end positions. 

This query is useful, for example, to extract specific parts of messages, remove certain number of characters from the beginning and end of strings, or process text of varying lengths. 

Sample output from the incoming example data: 

message| result  
---|---  
The quick brown fox jumps over the lazy dog| quick brown fox jumps over the lazy  
Pack my box with five dozen liquor jugs| k my box with five dozen liquor  
How vexingly quick daft zebras jump| vexingly quick daft zebras  
The five boxing wizards jump quickly| five boxing wizards jump quic  
  
Note that [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) uses zero-based numbering, so position 4 refers to the 5th character in the string (after positions 0,1,2,3,4). The end position is calculated dynamically for each message based on its total length using [`text:length()`](https://library.humio.com/data-analysis/functions-text-length.html).
