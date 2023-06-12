# **ADX Formatting** 
### ADX Data definition 
ADX Data definition can be defined using `dhis2_etl.models.adx.ADXMappingCubeDefinition`. 
```python 
ADXMappingCubeDefinition(
    name=str, # Name of ADX Mapping Definition 
    period_type=ISOFormatPeriodType(), # Format of handled period type, at the moment only ISO Format is supported 
    groups=[
        ADXMappingGroupDefinition(
            comment=str, # Generic comment 
            to_org_unit_code_func= lambda l: build_dhis2_id(l.uuid),
            data_values=[
                ADXMappingDataValueDefinition(
                    data_element=str, # Name of calculated value 
                    period_filter_func =  function # function expection an queryset to filter and a period as input and should return a queryset
                    dataset_from_orgunit_func=function # Function extracting collection from group orgunit object
                    aggregation_func=function # Function transofrming filtered queryset to dataset value 
                    categories=[
                        ADXMappingCategoryDefinition(
                            category_name=str,
                            category_options=[
                                ADXCategoryOptionDefinition(
                                    code=code,
                                    filter=function # Function Filtering output of `dataset_from_orgunit_func`
                                )
    ])])])])
```
#### Example definition: [HF Number of insurees](dhis2_etl/tests/adx_tests.py)

### ADX Data Storage 
`dhis2_etl.converters.adx.ADXBuilder` is used for creating ADX Data collection
based on data definition. 
Example:

```python
from dhis2_etl.converters.adx.builders import ADXBuilder
from dhis2_etl.models.adx.definition import ADXMappingGroupDefinition

definition = ADXMappingGroupDefinition(...)
builder = ADXBuilder(definition)
period_type = "2019-01-01/P2Y"  # In format accepted by definition.period_type
org_units = HealthFaciltity.objects.filter(validity_to__isnull=True)  # All HF
builder.create_adx_cube(period_type, org_units)  # Returns ADXMapping object
```

### ADX Formatters
ADX Formatters allow transforming ADXMapping objects to diffrent formats. 
At the moment only XML Format is implemented.

```python
from dhis2_etl.converters.adx.formatters import XMLFormatter
from dhis2_etl.models.adx.data import ADXMapping

adx_format = ADXMapping(...)
xml_formatter = XMLFormatter()
xml_format = xml_formatter.format_adx(adx_format)
```

