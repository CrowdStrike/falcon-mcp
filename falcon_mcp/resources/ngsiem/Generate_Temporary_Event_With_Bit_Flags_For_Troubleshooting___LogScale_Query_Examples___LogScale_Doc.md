# Generate Temporary Event With Bit Flags For Troubleshooting | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-bitfield-extractflags-4.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Generate Temporary Event With Bit Flags For Troubleshooting

Generate temporary events with the [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function as part of the query to generate sample data for testing or troubleshooting 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2[\Add Field/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    createEvents(["flags=4"])
    | kvParse()
    | bitfield:extractFlags(
    field=flags,
    output=[
    [1, ErrorFlag],
    [2, WarningFlag]
    ])

### Introduction

The [`bitfield:extractFlags()`](https://library.humio.com/data-analysis/functions-bitfield-extractflags.html) can be used to code an integer to its bit-representation and extract the bits at specified indices to specified field names as a boolean. One or multiple flags can be extracted from a bit field. The [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function generates temporary events as part of the query and is ideal for generating sample data for testing or troubleshooting. The events are generated with no extracted fields but [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) can, advantageously, be combined with one of the many parsers. For example, given raw strings in the format of key/value pairs, the pairs can be parsed to fields using the [`kvParse()`](https://library.humio.com/data-analysis/functions-kvparse.html) function. 

In this example, the bit field is named `flags` and has the value `4` corresponding to the bit string `00000100`. The goal is to extract two flags based on their bit value. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2[\Add Field/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         createEvents(["flags=4"])

Creates a temporary event that includes a new field named flag to be used for testing purposes. Bit flags are one or more (up to 32) Boolean values stored in a single number variable. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2[\Add Field/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | kvParse()

Parses the raw text looking for the key/value pairs and creates the corresponding fields in the event. In this case a single field named flags with the value `8`. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2[\Add Field/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | bitfield:extractFlags(
         field=flags,
         output=[
         [1, ErrorFlag],
         [2, WarningFlag]
         ])

When specifying the values for the bit field, values start from bit 0 (`2^0` or decimal 1). The invidual bit values are defined using an array of arrays. Each array index should specify the bit number (not literal value) and the field to be created. Each field will then be set to `true` if the bit was enabled in the compared field. 

In the above example, `ErrorFlag` located at bit 1 (2^1, decimal 2), and `WarningFlag` located at index `2` (decimal 4). 

  5. Event Result set.




### Summary and Results

The query is used to extract and match values to bit flags. Creating events based on bit flags are useful when testing and troubleshooting on values, as it is faster to compare values stored as bitmasks compared to a series of booleans. Furthermore, events based on bit flags uses considerably less memory. 

Sample output from the incoming example data: 

ErrorFlag| WarningFlag  
---|---  
false| true
