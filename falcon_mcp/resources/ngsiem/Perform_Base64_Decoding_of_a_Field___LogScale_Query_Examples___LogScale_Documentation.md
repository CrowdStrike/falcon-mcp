# Perform Base64 Decoding of a Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-base64decode-store-decoded.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Perform Base64 Decoding of a Field

Perform Base64 decoding of a field using [`base64Decode()`](https://library.humio.com/data-analysis/functions-base64decode.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    decoded := base64Decode(encoded)

### Introduction

Base64 is used to encode binary data as printable text. This allows you to transport binary over protocols or mediums that cannot handle binary data formats and require simple text. For example, encoding an attachment as Base64 before sending, and then decoding when received, assures older SMTP servers will not interfere with the attachment. 

In this example, the [`base64Decode()`](https://library.humio.com/data-analysis/functions-base64decode.html) function is used to manipulate character strings that are base64 encoded and return a base64-decoded version of the input string. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         decoded := base64Decode(encoded)

Decodes the `Base64` value in encoded and stores it in the field decoded (the field on which to decode `Base64` values). The decoded value is subsequently decoded as binary representation of a string according to the [_`charset`_](https://library.humio.com/data-analysis/functions-base64decode.html#query-functions-base64decode-charset) parameter. The [_`charset`_](https://library.humio.com/data-analysis/functions-base64decode.html#query-functions-base64decode-charset) parameter is the character set to use when transforming bytes to string. To work with binary data, use `ISO-8859-1` character set. 

  3. Event Result set.




### Summary and Results

The query is used to filter on input fields that do not contain a valid Base64 encoding. When decoding to a code point that is invalid with respect to the selected charset, the invalid code point is replaced with a placeholder character. This process ensures that data can be easily processed by computers.
