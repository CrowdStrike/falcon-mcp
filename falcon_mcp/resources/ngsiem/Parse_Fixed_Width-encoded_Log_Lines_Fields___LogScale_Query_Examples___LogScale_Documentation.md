# Parse Fixed Width-encoded Log Lines Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-parsefixedwith-logline-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Parse Fixed Width-encoded Log Lines Fields

Parse fixed width-encoded field from log lines into columns using the [`parseFixedWidth()`](https://library.humio.com/data-analysis/functions-parsefixedwidth.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    parseFixedWidth(result, columns=[count, status, completion, precision, sourcetask], widths=[3,9,4,10,10])

### Introduction

The [`parseFixedWidth()`](https://library.humio.com/data-analysis/functions-parsefixedwidth.html) function can be used to parse fixed width-encoded fields into known columns. 

A fixed width file can be a very compact representation of numeric data. The file type is fast to parse, because every field is in the same place in every line. A disadvantages of fixed width file is, that it is necessary to describe the length of every field being parsed. 

In this example, the [`parseFixedWidth()`](https://library.humio.com/data-analysis/functions-parsefixedwidth.html) function is used to parse an accesslog. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         parseFixedWidth(result, columns=[count, status, completion, precision, sourcetask], widths=[3,9,4,10,10])

Parses the fixed width-encoded field in the accesslog and adds the returned values as known columns in the result field. 

  3. Event Result set.




### Summary and Results

The query is used to parse compact numeric data consisting of fixed width-encoded fields into columns. 

In case a field value is longer than, for example, `10` characters, the parser handles overflow by truncating data that exceeds the specified field width while maintaining the structure of the parsed output. 

As an example, if the original sourcetask value was: `SCAN_FILES_WITH_VERY_LONG_NAME` (29 characters), then the extra characters `_WITH_VERY_LONG_NAME` would be truncated. 

This parsing method is particularly valuable when dealing with structured data that must maintain strict positional formatting and character length requirements.
