# CrowdStrike Parsing Standard Release Notes | Crowdstrike Parsing Standard 1.1 | LogScale Documentation

**URL:** https://library.humio.com/logscale-parsing-standard/pasta-rn.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Crowdstrike Parsing Standard 1.1](pasta.html)

# CrowdStrike Parsing Standard Release Notes

The following changes have been identified between releases of the Crowdstrike Parsing Standard. 

## 1.1.0

Compared to the previous standard from the Package Standards document, the Parsing Standard is changed in the following ways: 

  * Adds rule of keeping original Vendor. field when normalizing to ECS 

  * Adds event.severity mapping rules 

  * Updates the rules and explanation for parser versioning 

  * Adds rule of using array:append with event.category and event.type

  * Adds rule to lowercase all *.email field values 

  * Adds rule that `event.kind := "alert"` should only be set when event.category, event.type, and event.severity fields are present and set 




## 1.0.0

The Parsing Standard was previously embedded in the old Package Standards document. That document still exists to document our approach to packages as a whole, but the parsing standard has been extracted so it can be referenced outside of packages. Going forward, the PaSta acronym refers to the parsing standard only. 

Compared to the previous standard from the Package Standards document, the Parsing Standard is changed in the following ways: 

  * Adds new fields to tag 

  * Removes the `Product` field, replaced by guidelines for `event.module` and `event.dataset`

  * Removes the `event.code` field (to be reinstated later) 

  * Removes the `related` fields 

  * Normalises values for a range of new fields
