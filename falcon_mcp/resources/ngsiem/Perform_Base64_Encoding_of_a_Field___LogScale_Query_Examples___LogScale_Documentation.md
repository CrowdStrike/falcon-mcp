# Perform Base64 Encoding of a Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-base64encode-store-encoded.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Perform Base64 Encoding of a Field

Perform Base64 encoding of a field using the [`base64Encode()`](https://library.humio.com/data-analysis/functions-base64encode.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    base64Encode(a)

### Introduction

Base64 is used to encode binary data as printable text. This allows you to transport binary over protocols or mediums that cannot handle binary data formats and require simple text. For example, encoding an attachment as Base64 before sending, and then decoding when received, assures older SMTP servers will not interfere with the attachment. 

In this example, the [`base64Encode()`](https://library.humio.com/data-analysis/functions-base64encode.html) function is used to manipulate input string that are `UTF-8` encoded and return a base64-encoded version of the input string in field a in a new field named _base64Encode. The input string is: `Hello, World!`. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         base64Encode(a)

Takes the input string `Hello, World!` in field a, converts the string to UTF-8 encoding, and then encodes this string with Base64. 

The output value would be `_base64Encode = "SGVsbG8sIFdvcmxkIQ=="`

It is also possible to use an [_`as`_](https://library.humio.com/data-analysis/syntax-fields.html#syntax-fields-from-functions) parameter to specify another output field than the default _base64Encode: [`base64Encode(a, as=out)`](https://library.humio.com/data-analysis/functions-base64encode.html)

  3. Event Result set.




### Summary and Results

The [`base64Encode()`](https://library.humio.com/data-analysis/functions-base64encode.html) function is used to encode strings that may contain special characters, to be able to transmit or store these, and later be decoded using the [`base64Decode()`](https://library.humio.com/data-analysis/functions-base64decode.html) function if needed. The query converts data into a format suitable for systems that only accept ASCII characters. This process ensures that data can be easily processed by computers. 

A reverse of the encoding is performed using this query: `base64Encode(a, as=a) | base64Decode(field=a, as=a) `

Note that while Base64 encoding is useful for data handling, it is not a secure encryption method.
