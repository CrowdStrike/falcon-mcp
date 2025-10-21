# Understanding Schema Requirements | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-field-aliasing-schema-requirements.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

/ [Field Aliasing](searching-data-field-aliasing.html)

### Understanding Schema Requirements

Schemas contain a collection of field mappings. Every mapping will contain [tag conditions](searching-data-field-aliasing-configure.html#searching-data-field-aliasing-configure-step7) to identify the event that the mapping should be applied to. Each event can be matched with at most one mapping, hence you need to ensure that the set conditions used in all mappings are not ambiguous. See following examples of two mappings that belong to one schema: 

Example Mapping 1 |  Example Mapping 2 |  Explanation   
---|---|---  
#vendor = A |  #vendor = A  #other = X  |  Invalid because they share the same condition #vendor = A   
#vendor = A |  #other = X |  Invalid because there is no common field   
#vendor = A |  #vendor = B |  Valid because they share a common field, but with different values   
#vendor = A  #other1 = X  |  #vendor = B  #other2 = Y  |  Valid because they share a common field (#vendor), but with different values   
  
A good rule of thumb is to ensure that all your mappings share at least one common tag field, but with different required values on each mapping.
