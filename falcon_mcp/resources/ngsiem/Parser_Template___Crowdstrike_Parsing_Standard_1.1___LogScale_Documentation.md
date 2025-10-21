# Parser Template | Crowdstrike Parsing Standard 1.1 | LogScale Documentation

**URL:** https://library.humio.com/logscale-parsing-standard/pasta-parser-guidelines-template.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Crowdstrike Parsing Standard 1.1](pasta.html)

/ [Parser Guidelines](pasta-parser-guidelines.html)

### Parser Template

The following template can be used as a staring point for creating a correctly defined parser. 
    
    
    name: template
    tests: []
    $schema: https://schemas.humio.com/parser/v0.3.0
    script: |
      // #region PREPARSE
      /************************************************************
      ****** Parse timestamp and log headers
      ****** Extract message field for parsing 
      ****** Parse structured data 
      ************************************************************/
        
      
      // #endregion
    
      // #region METADATA
      /************************************************************
      ****** Static Metadata Definitions
      ************************************************************/
      | ecs.version := "8.17.0"
      | Cps.version := "2.0.0"
      | Parser.version := "1.0.0"
      | Vendor := ""
      | event.module := ""
      | event.dataset := ""
    
      // #endregion
    
      // #region NORMALIZATION
      /************************************************************
      ****** Parse unstructured data (i.e. message field)
      ****** Normalize fields to data model
      ************************************************************/
    
    
      // #endregion
    
      // #region POST-NORMALIZATION
      /************************************************************
      ****** Post Normalization
      ****** Custom parser logic needed after normalization
      ************************************************************/
    
    
      // #endregion
    
    tagFields:
    - Cps.version
    - Vendor
    - ecs.version
    - event.dataset
    - event.kind
    - event.module
    - event.outcome
    - observer.type
