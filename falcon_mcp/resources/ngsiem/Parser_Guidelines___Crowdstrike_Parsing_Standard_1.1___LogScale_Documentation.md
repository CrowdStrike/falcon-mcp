# Parser Guidelines | Crowdstrike Parsing Standard 1.1 | LogScale Documentation

**URL:** https://library.humio.com/logscale-parsing-standard/pasta-parser-guidelines.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Crowdstrike Parsing Standard 1.1](pasta.html)

## Parser Guidelines

These guidelines aim to provide the best practices to follow when you create a parser. 

  * Define test cases which exercise all of the logic in the parser. Test cases should not contain personally identifiable information (PII). PII in this scenario could be: 

    * IP addresses 

    * URLs 

    * User names/email addresses 

To replace PII in test cases, use valid test data instead. See our [Parser Sample Data](pasta-parser-guidelines-sample.html "Parser Sample Data") and [Asset Guidelines](https://library.humio.com/integrations/packages-developer-guidelines-assets.html) for more information. 

  * Add comments which fully describe the parser logic, for example [Example Parser Logic](pasta-parser-guidelines-parser-yaml.html "Example Parser Logic"). 

  * Follow the [_CrowdStrike Parsing Standard (CPS) 1.1_](pasta.html "CrowdStrike Parsing Standard \(CPS\) 1.1") on how to set individual fields. 

  * Parsers should be written under the assumption that they will: 

    * Receive one event at a time. Therefore events should not be in bulk by the time they reach the parser. When logs are sent in bulk to the parser, the parser needs to be customized to split them into separate events. Additionally any transport method that we explicitly support in the package should target this way of working. 

    * Receive events that are not wrapped in custom transport layers (e.g. a layer of JSON). If logs are wrapped in, for example, a layer of JSON, the parser needs to be customized to remove the data wrapper. Additionally any transport methods that we explicitly support in the package should target this way of working. 

  * Parsers should follow the [Parser Template](pasta-parser-guidelines-template.html "Parser Template").
