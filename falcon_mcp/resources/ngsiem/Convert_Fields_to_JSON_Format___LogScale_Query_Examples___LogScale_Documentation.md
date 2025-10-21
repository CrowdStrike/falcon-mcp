# Convert Fields to JSON Format | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-writejson-nested-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Convert Fields to JSON Format

Convert values and fields to JSON format using the [`writeJson()`](https://library.humio.com/data-analysis/functions-writejson.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    writeJson(["a.b.c", "a.b.e[0]", "a.d", "a.f.g"])

### Introduction

The [`writeJson()`](https://library.humio.com/data-analysis/functions-writejson.html) function can be used to convert values and fields to JSON format. 

Sometimes, the JSON format is preferred when exchanging data between different systems and programming languages because of its language-independent nature. Furthermore, JSON supports several data types, such as; objects, arrays, strings, boolean values, null values and both possitive and negative numbers and decimal/floating point format. JSON is also ideal for storing temporary data. 

In this example, the [`writeJson()`](https://library.humio.com/data-analysis/functions-writejson.html) function is used to create a nested JSON structure from an array of field paths. The function handles both regular nested fields and array indexing. 

Example incoming data might look like this: 

@timestamp| a.b.c| a.b.e[0]| a.d| a.f.g  
---|---|---|---|---  
2023-06-15T10:30:00Z| value1| value2| value3| value4  
2023-06-15T10:30:01Z| test1| test2| test3| test4  
2023-06-15T10:30:02Z| data1| data2| data3| data4  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         writeJson(["a.b.c", "a.b.e[0]", "a.d", "a.f.g"])

Creates a JSON structure from the specified field paths and returns the JSON formatted results in a new field named _json. 

In this example, the [`writeJson()`](https://library.humio.com/data-analysis/functions-writejson.html) function: 

     * Takes an array of field paths as input. 

     * Handles nested field paths using dot notation. 

     * Supports array indexing with square bracket notation. 

     * Maintains the hierarchical relationship between fields in the resulting JSON. 

  3. Event Result set.




### Summary and Results

The query is used to transform flat field references into a structured JSON object, preserving the hierarchical relationships between fields. 

This query is useful, for example, to reconstruct nested data structures from flattened fields, to prepare data for external systems that expect nested JSON or to create structured views of related fields 

Sample output from the incoming example data: 

_json| a.b.c| a.b.e[0]| a.d| a.f.g  
---|---|---|---|---  
{"a":{"b":{"c":"value1","e":["value2"]},"d":"value3","f":{"g":"value4"}}}| value1| value2| value3| value4  
{"a":{"b":{"c":"test1","e":["test2"]},"d":"test3","f":{"g":"test4"}}}| test1| test2| test3| test4  
{"a":{"b":{"c":"data1","e":["data2"]},"d":"data3","f":{"g":"data4"}}}| data1| data2| data3| data4
