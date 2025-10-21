# Query Language Syntax | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

# Query Language Syntax

The CrowdStrike Query Language (CQL) is the syntax that lets you compose queries to retrieve, process, and analyze data in Falcon LogScale. 

The query language is built around a chain of data-processing commands linked together. Each expression passes its result to the next expression in the sequence, allowing you to create complex queries by combining query expressions. This architecture is similar to [command pipes](https://en.wikipedia.org/wiki/Pipeline_\(Unix\)), a powerful and flexible mechanism for advanced data analysis in Unix and Linux shells. 

This reference section on the CrowdStrike Query Language provides detailed explanations on several related topics. They are listed in the following with brief descriptions — click on a heading to see more: 

  * **[Comments](syntax-comments.html "Comments")**

Adding comments to query syntax is a great way to facilitate knowledge transfer and make query triage much easier. The CrowdStrike Query Language (CQL) supports `//` (single-line) and `/* ... */` (multi-line) comments. 

  * **[Query Filters](syntax-filters.html "Query Filters")**

When querying data in LogScale, filters may be used to reduce the results to the relevant data. You can use free-text filters to grep data, or you can filter based on fields, stipulating acceptable field values or using regular expressions for matching field contents. 

  * **[Operators](syntax-operators.html "Operators")**

For filtering, there are several operators available: besides logical operators, there are also some comparison operators to narrow search results to what's most important to you. 

  * **[Adding Fields to Events](syntax-fields.html "Adding Fields to Events")**

To improve result sets, as well as to construct more complex queries, you can create new fields when querying data. You can do this using the `:=` syntax, the [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter (available within some functions), a regex, or [`eval()`](functions-eval.html "eval\(\)") function. 

  * **[User Parameters/Variables](syntax-fields-user-input.html "User Parameters \(Variables\)")**

User-configurable parameters can be added to a query to allow for the user to specify a value in place of a fixed value within the query. 

  * **[Conditional Evaluation](syntax-conditional.html "Conditional Evaluation")**

Although CrowdStrike Query Language does not provide a typical conditional syntax, there are ways to evaluate data conditionally. You can use a `case` statement or a `match` statement. 

  * **[Array Syntax](syntax-array.html "Array Syntax")**

Guidance on using, processing and identifying information from array. This applies to [Array Query Functions](functions-array.html "Array Query Functions"), for indexing and selecting members in objects using a syntax similar to JSON. 

  * **[Function Syntax](syntax-function.html "Function Syntax")**

LogScale query functions take a set of events, parameters, or configurations. 

  * **[Expressions](syntax-expressions.html "Expressions")**

Some LogScale functions and constructs allow writing expressions instead of simple values or field names, for example, to perform computations. 

  * **[Relative Time Syntax](syntax-time-relative.html "Relative Time Syntax")**

For time related queries, you may want to know about Rate Unit Conversion, or about relative time syntax. 




Section in other parts of this manual 

  * **[_Query Functions_](functions.html "Query Functions")**

You can use query functions to get values, or reduce results. LogScale provides many built-in query functions, and you can combine them to create your own. 

  * **[_Query Joins and Lookups_](query-joins.html "Query Joins and Lookups")**

LogScale supports different methods for joining content between event sets. 




Other manuals: 

  * **[Regular Expression Syntax](syntax-regex.html "Regular Expression Syntax")**

Regular expressions in CrowdStrike Query Language are similar to most regular expression environments, with slight differences though. 




Section in other parts of this manual: 

  * **[_Query Functions_](functions.html "Query Functions")**

You can use query functions to get values, or reduce results. LogScale provides many built-in query functions, and you can combine them to create your own. 

  * **[_Query Joins and Lookups_](query-joins.html "Query Joins and Lookups")**

LogScale supports different methods for joining content between event sets. 




Other manuals: 

  * **[CrowdStrike Query Language Grammar Subset](https://library.humio.com/lql-grammar/syntax-grammar-guide.html)**

This grammar is a subset of the CrowdStrike Query Language, intended as a guide for programmatically generating LogScale queries (not for parsing them). 

  * **[Falcon LogScale Beginner Introduction](https://library.humio.com/training/training-getting-started.html)**

The [Falcon LogScale Beginner Introduction](https://library.humio.com/training/training-getting-started.html). It will link you to an interactive tutorial that will introduce you to queries in LogScale and let you try sample queries that will demonstrate the basic principles.
