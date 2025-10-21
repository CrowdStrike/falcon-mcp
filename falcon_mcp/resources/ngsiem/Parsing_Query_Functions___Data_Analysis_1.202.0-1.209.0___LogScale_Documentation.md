# Parsing Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-parsing.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Parsing Query Functions

LogScale's parsing functions can be used to extract data, or to identify specific data types, such as dates, time or JSON values from events. 

**Table: Parsing Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`base64Decode([as], [charset], field)`](functions-base64decode.html "base64Decode\(\)")| [_`field`_](functions-base64decode.html#query-functions-base64decode-field)|  |  Performs Base64 decoding of a field.   
[`base64Encode([as], field)`](functions-base64encode.html "base64Encode\(\)")| [_`field`_](functions-base64encode.html#query-functions-base64encode-field)|  |  Performs Base64 encoding of a field.   
[`kvParse([as], [excludeEmpty], [field], [onDuplicate], [override], [prefix], [separator], [separatorPadding])`](functions-kvparse.html "kvParse\(\)")| [_`field`_](functions-kvparse.html#query-functions-kvparse-field)|  |  Key-value parse events.   
[`parseCEF([field], [headerprefix], [keeplabels], [labelprefix], [prefix])`](functions-parsecef.html "parseCEF\(\)")| [_`field`_](functions-parsecef.html#query-functions-parsecef-field)|  |  Parses CEF version 0.x encoded messages.   
[`parseCsv(columns, [delimiter], [excludeEmpty], field, [trim])`](functions-parsecsv.html "parseCsv\(\)")| [_`field`_](functions-parsecsv.html#query-functions-parsecsv-field)|  |  Parses a CSV-encoded field into known columns.   
[`parseFixedWidth(columns, [field], [trim], widths)`](functions-parsefixedwidth.html "parseFixedWidth\(\)")| [_`field`_](functions-parsefixedwidth.html#query-functions-parsefixedwidth-field)|  |  Parses a fixed width-encoded field into known columns.   
[`parseHexString([as], [charset], field)`](functions-parsehexstring.html "parseHexString\(\)")| [_`field`_](functions-parsehexstring.html#query-functions-parsehexstring-field)|  |  Parses input from hex encoded bytes, decoding resulting bytes as a string.   
[`parseInt([as], [endian], field, [radix])`](functions-parseint.html "parseInt\(\)")| [_`field`_](functions-parseint.html#query-functions-parseint-field)|  |  Converts an integer from any radix or base to base-ten, decimal radix.   
[`parseJson([exclude], [excludeEmpty], field, [handleNull], [include], [prefix], [removePrefixes])`](functions-parsejson.html "parseJson\(\)")| [_`field`_](functions-parsejson.html#query-functions-parsejson-field)|  |  Parses specified fields as JSON.   
[`parseLEEF([delimiter], [field], [headerprefix], [keeplabels], [labelprefix], [parsetime], [prefix], [timezone])`](functions-parseleef.html "parseLEEF\(\)")| [_`field`_](functions-parseleef.html#query-functions-parseleef-field)|  |  Parses LEEF version 1.0 and 2.0 encoded messages.   
[`parseTimestamp([addErrors], [as], [caseSensitive], field, [format], [timezone], [timezoneAs], [timezoneField])`](functions-parsetimestamp.html "parseTimestamp\(\)")| [_`format`_](functions-parsetimestamp.html#query-functions-parsetimestamp-format)|  |  Parses a string into a timestamp.   
[`parseUri([defaultBase], field, [prefix])`](functions-parseuri.html "parseUri\(\)")| [_`field`_](functions-parseuri.html#query-functions-parseuri-field)|  |  Extracts URI components from a field.   
[`parseUrl([as], [field])`](functions-parseurl.html "parseUrl\(\)")| [_`field`_](functions-parseurl.html#query-functions-parseurl-field)|  |  Extracts URL components from a field.   
[`parseXml(field, [prefix], [strict])`](functions-parsexml.html "parseXml\(\)")| [_`field`_](functions-parsexml.html#query-functions-parsexml-field)|  |  Parses specified field as XML.
