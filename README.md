# openimis-be-dhis2_py

openIMIS Module to push data into DHIS2


This module will push metadata
- Location as OrgUnit
- Health facility as OrgUnit
- gender as optionset
- profession as optionset
- groupType as optionset
- education as optionset
- product as optionset
- diagnosis as optionset

This module will push data in two programs
- Family-insuree [enrollment] Policy [program registration / event]
- Claims (claim details[program registration / event], Claims Services[event], Claim Items[event])

## Getting started

1. install DHIS2 2.33 or 2.34 or 2.35 

1. get the metadata in the Script directory and take the right one for your DHIS2 instance

1. Import the metadata in DHIS2 (http://[dhis2Address]/dhis-web-importexport/index.html#/import/metadata)
    - JSON Format
    - UID identifier
    - Report Error
    - Reference pre-heat
    - New and udate strategy
    - Atomic mode all
    - Merge mode


1. create a root orgunit in DHIS 2 https://[dhis2Address]/dhis-web-maintenance/index.html#/list/organisationUnitSection and copy the uid in app.py

1. Push the optionset http://[openIMISAddress]/iapi/dhis2_etl/StartThreadTask?scope=optionset&startDate=[dateOfFirstOpeimisUsage]&stopDate=[dataOfToday]

1. Push the location http://[openIMISAddress]/iapi/dhis2_etl/StartThreadTask?scope=orgunit&startDate=[dateOfFirstOpeimisUsage]&stopDate=[dataOfToday]

1. Assign name to the level in DHIS2 (http://[dhis2Address]/dhis-web-maintenance/index.html#/list/organisationUnitSection/organisationUnitLevel)

1. Allow the family-insuree program to collect data on village: 
    - Go at http://[dhis2Address]/dhis-web-maintenance/index.html#/edit/programSection/program/IR5BiEXrBD7
    - in access tab, on orgUnit Group, select "Village"
    - Click on "Select" on the orgUnit group line
    - click on save for the program

1. Allow the family-insuree program to collect data on healthfacilities: 
    - Go at http://[dhis2Address]/dhis-web-maintenance/index.html#/edit/programSection/program/vPjOO7Jl6jC
    - in access tab, on orgUnit Group, select "HealthCenter"
    - Click on "Select" on the orgUnit group line
    - on orgUnit Group, select "Dispensary"
    - Click on "Select" on the orgUnit group line
    - on orgUnit Group, select "Hospitals"
    - Click on "Select" on the orgUnit group line
    - click on save for the program

1. You are now ready to start the module
    - to push insuree and Policies in the same time (good for first load) : http://[openIMISAddress]/iapi/dhis2_etl/StartThreadTask?scope=insureepolicies&startDate=[dateOfFirstOpeimisUsage]&stopDate=[dataOfToday]
    - to push insuree: http://[openIMISAddress]/iapi/dhis2_etl/StartThreadTask?scope=insuree&startDate=[dateOfFirstOpeimisUsage]&stopDate=[dataOfToday]
    - to push policy: http://[openIMISAddress]/iapi/dhis2_etl/StartThreadTask?scope=policy&startDate=[dateOfFirstOpeimisUsage]&stopDate=[dataOfToday]
    - to push claim: http://[openIMISAddress]/iapi/dhis2_etl/StartThreadTask?scope=claim&startDate=[dateOfFirstOpeimisUsage]&stopDate=[dataOfToday]
    - to push insurees, then policies, then claims: http://[openIMISAddress]/iapi/dhis2_etl/StartThreadTask?scope=all&startDate=[dateOfFirstOpeimisUsage]&stopDate=[dataOfToday]

1. customisation of the dataElement
    - to get the categoryOptionCombos for the population https://[dhis2Address]/api/categoryOptionCombos
    - Other uid can be found at the end of url when browsing on dhis2 webapp
    - update the app.py 

## development to do

- use django scheduler instead of view for triggering the jobs
- push the metadata along option set push
- harmonising Service and Items attributes and Data elements
- add perms and security if the view triggering the job is kept
- harmonising usage of insuranceID, InsureeNumber, InsureeID in DHIS2
- connection error management and DHIS2 answers parsing/logging (loggin only what matters and not including the 99% succesful)
- add orgUnit in programs
- safely remove all personal data (firstname. lastname, ...) because those data should't be shared with a BI systems
- push population to data set
- pull population from dataset
- use optionGroup in indicator iso option when the options are defined in IMIS (but for gender)
- add DE family in population dataset



 
-------------------------------------------------------------------------------------
Hisp india documetation for the programs
-------------------------------------------------------------------------------------

![](RackMultipart20201210-4-1agjxdr_html_81f805b27f195b6e.gif)

![](RackMultipart20201210-4-1agjxdr_html_8337311abc75b3be.gif) ![](RackMultipart20201210-4-1agjxdr_html_76e5e5e64c8f76d2.gif) ![](RackMultipart20201210-4-1agjxdr_html_f0378cec9a7f81b4.gif)

**Version 2.1**

# System Design Document

**openIMIS**** -DHIS2 Integration**

# Contents

**[1. Executive Summary 2](#_Toc24836604)**

**[2. System Overview 3](#_Toc24836605)**

**[3. Design and Development Approach 4](#_Toc24836606)**

**[3.1 Organisation units/ Reporting Units and hierarchy 4](#_Toc24836607)**

**[3.2 Data Input 5](#_Toc24836608)**

[3.2.1 Family/Insuree Program 5](#_Toc24836609)

[3.2.2 Claims Management Program 7](#_Toc24836610)

**[3.2 Data Analysis 10](#_Toc24836611)**

[3.3.1 Organisation Unit Dimensions 11](#_Toc24836612)

[**3.3.1.1 Organisation unit groups and Group Sets** 11](#_Toc24836613)

[3.3.4 Indicator Dimensions 12](#_Toc24836614)

[**3.3.4.1**** Indicator groups** 12](#_Toc24836615)

[3.3.5Dashboards 13](#_Toc24836616)

**[4.User management 13](#_Toc24836617)**

**[4.1 Admin user/Super user 13](#_Toc24836618)**

**[4.2 District User 14](#_Toc24836619)**

**[4.3 Facility User 14](#_Toc24836620)**

**[4.4 Health Insurance Board/National Insurance Agency 14](#_Toc24836621)**



# **Change Log**

| **Version** | **Date** | **Changes made** |
| --- | --- | --- |
| Version 1 | February 6th 2020 | - |
| Version 2 | May 26th 2020 | Updated Claims Management Program Design <br/>- Claim – Service program Stage<br/>- Claim – Item program Stage |
| Version 2.1 | May 26th 2020 | Updated based on the django dhis2 ETL |

# **Executive Summary**

The following document details out the overall system design, approach, and the functionalities available in the envisaged openIMIS-DHIS2 integrated instance. This document builds on the requirements document shared with GIZ/Digital Square team in August 2019. The report has the following parts:

The System Overview section provides a summary of key functionalities based on the requirements mentioned in the requirements document has been documented which include key aspects such as system metadata configuration, data input, data analysis, use of dashboards.

The System Design and Development section describes the design and development approach where each data input component defined in the requirements document has been described in terms of how the component will be defined in DHIS2. This section will be a living component, which will evolve, and any change in the data model based on feedback will be considered and correspondingly will be updated to maintain a record of the design decisions made.

The Data Analysis section defines the various data dimension, which will be configured to give the desired shape and fit the data being collected so that it reaps maximum value when analysed. The dimensions involve the use of various disaggregations in place to create combinations, the grouping of facilities based on qualifying factors to analyze by their type, location, area, etc.

The last section proposes the kind of users/user roles the system should have to be of use to all stakeholders involved in the health insurance data in the country/region of implementation.


# **System Overview**

The integrated openIMIS-DHIS2 integrated system will have the following key functionalities, which will encompass all the requirements mentioned in the requirements document. The below functionalities will be suitable for all openIMIS implementations, and minor modifications will be required to manage the localised context of the country.

1. Availability of reporting hierarchies as per the structure defined in openIMIS by defining the appropriate levels in DHIS2, the reporting hierarchies will further complement the programs designed for storing the incoming data from openIMIS for client enrollments and claims management.

1. Provision for data import for openIMIS on a daily frequency which will have the data received for new policy enrollments, updates in the policy status, new claims submissions, updates in the status of the submitted claims as they get processed.

1. Availability of all data dimensions required for data analysis such as groups and group sets for organisation units, data elements, and indicators.

1. Availability of dashboards for different stakeholders and indicator groups (Beneficiary Management, Claims Management, and Operational Indicators).

1. Supporting spatial analysis of data using the GIS apps in DHIS2 depending upon the availability of the shapefiles of the country which can be configured into DHIS2.

# **Design and Development Approach**

The system will be designed using the latest stable release DHIS2 2.32, which can be further upgraded to higher versions. The below sections define how the contents defined in the requirements document will be configured in DHIS2.


## 3.1 Organisation units/ Reporting Units and hierarchy

Organisation units refer to the reporting facilities in DHIS and are organized based on the hierarchy of reporting. The data reported by each facility is stored against the respective organisation unit. With context to openIMIS, the hierarchy structure defined in openIMIS will be taken as the base for importing into DHIS2. For example, the below structure is an example of hierarchy available in openIMIS implementation in Nepal which has been implemented in DHIS2:

| **Level** | **Organisation Unit** |
| --- | --- |
| Level 1 | Country |
| Level 2 | Province |
| Level 3 | District |
| Level 4 | Health Facilities, Wards |
| Level 5 | Villages |

The above structure will be modifiable based on the reporting structure defined in the country&#39;s openIMIS implementation. The further classification of organisation units into different dimensions and their use in data analysis has been elicited in the Data Analysis section of the document.

In the openIMIS-DHIS2 Demo instance, the hierarchy from the openIMIS demo instance has been taken as the base, where the following structure is followed:

| **Level** | **Organisation Unit** |
| --- | --- |
| Level 1 | Country |
| Level 2 | Province |
| Level 3 | District |
| Level 4 | Health Facilities |

## 3.2 Data Input

The data input structure is defined below for the information which will be fetched from openIMIS and stored in DHIS2 for aggregation, data presentation, visualisation, and analysis.

### 3.2.1 Family/Insuree Program

The Insuree program will be designed under the following considerations:

1. **Tracked Entity Type** : Person

| **Tracked Entity Attributes** | **Value Type** | **Menu Options** |
| --- | --- | --- | --- |
| **Family/Insuree** | Family ID | TEXT ||
| Insuree ID | TEXT ||
| CHF ID | TEXT ||
| Family ID | TEXT ||
| First Name | TEXT ||
| Last name | TEXT ||


1. **Enrollment entities** (as per openIMIS): All Insurees, including Household Heads.

1. **Organisation Units** : The program will be assigned to the village level, as registration in openIMIS is happening at the point of insuree&#39;s residence which is the village in case of the Nepal implementation.

Below are the key attributes/data elements captured in the Insuree Program concerning context with openIMIS Nepal implementation, these details can be changed based on local context in openIMIS country implementations.

1. **Family/Insuree Registration**

| **Program Name** | **enrollment Attributes** | **Value Type** | **Menu Options** |
| --- | --- | --- | --- |
| **Family/Insuree** | Family ID | TEXT ||
|| Family/group type | TEXT | Council, Organisation, Household, Priests, Students, Teacher, Others |
|| Insuree ID | TEXT ||
|| Identification type| TEXT | Drivers's Licence, Voter's ID, National ID, Passport|
|| CHF ID | TEXT ||
|| insurance number | TEXT ||
|| phone number | TEXT ||
|| Poverty status | TEXT | Yes/No |
|| Household head | TEXT | Yes/No |
|| First name | TEXT ||
|| Last name | TEXT ||
|| Date of birth/Age | DATE ||
|| Gender | TEXT | Male, Female, Other |
|| Marital status | TEXT | Single, Married, Divorced, Widowed, Not Specified |
|| First service point | TEXT ||
|| Education | TEXT | Options depends on openIMIS database |
|| Profession | TEXT | Options depends on openIMIS database |

1. **Policy Details**

**Program Stage Name:** Policy Details

**Type:** Repeatable (every time a change in the policy stage and policy status happens in openIMIS, a new event will be created in DHIS2 storing the updates made to the policy details.

Below are the data elements captured in the Policy Details program stage concerning the context of openIMIS Nepal implementation, these details can be changed based on the local context in openIMIS country implementations.

| **Program Name** | **Program Stage Name** | **Data Elements** | **Value Type** | **Menu Options** |
| --- | --- | --- | --- | --- |
| **Family/Insuree** | Policy Details | Policy ID | TEXT ||
||| Product | TEXT | Options depends on openIMIS database |
||| Policy Stage | TEXT | New Policy, Renewed Policy |
||| Policy Status | TEXT | Idle, Active, Suspended, Expired |
||| Policy value | NUMBER |  |
||| Policy expirity  date | DATE |  |
### 3.2.2 Claims Management Program

The Insuree program will be designed under the following considerations:

1. **Tracked Entity Type** : Person

1. **Enrollment entities** (as per openIMIS): All Claims submitted by the facilities for the insured individuals.

1. **Organisation Units** : The program will be assigned to the facility level, as services are given to the insuree at the facility level, and claims are submitted by the facility for processing for getting the required re-payments.

Below are the key attributes captured in the Claims Management Program concerning context with openIMIS Nepal implementation, these details can be changed based on local context in openIMIS country implementations.

1. **Claim Registration Attributes**

| **Program Name** | **Enrollment Attributes** | **Value Type** | **Menu Options** |
| --- | --- | --- | --- |
| **Claims Management** | Claim administrator | TEXT | |
|| Claim number | NUMBER | |
|| Primary Diagnosis | TEXT | Options depends on openIMIS database |
|| Secondary diagnosis | TEXT | Options depends on openIMIS database |
|| Secondary diagnosis | TEXT | Options depends on openIMIS database |
|| Secondary diagnosis | TEXT | Options depends on openIMIS database |
|| Secondary diagnosis | TEXT | Options depends on openIMIS database |
|| Visit type | TEXT | Emergency, Referral,Others |

1. **Claim Details**

**Program Stage Name:** Claim Details

**Type:** Repeatable (every time a new claim is submitted in openIMIS, or status of the claim is changed, this event will get created).

Below are the data elements captured in the Claim Details program stage concerning the context of openIMIS Nepal implementation, these details can be changed based on the local context in openIMIS country implementations.

| **Program Name** | **Program Stage Name** | **Data Elements** | **Value Type** | **Menu Options** |
| --- | --- | --- | --- | --- |
| **Claims Management** | Claims Details | Claim status | TEXT | Entered, Checked, Rejected, Processed, Valuated |
|||Claim amount | NUMBER ||
 ||| Adjusted amount | NUMBER ||
 ||| Approved amount | NUMBER ||
 ||| Valuated amount | NUMBER ||
 ||| Checked date | DATE ||
 ||| Valuation date | DATE ||
 ||| Rejected date | DATE ||
 

1. **Services Detail**

**Program Stage Name:** Claim - Services

**Type:** Repeatable (This stage will be created each time for capturing details for each service incurred by the insuree from the facility). For example, the claim in question has 10 services, then 10 events will be created for each service.

Below are the data elements captured in the Claim - Services program stage concerning the context of openIMIS Nepal implementation, these details can be changed based on the local context in openIMIS country implementations.

| **Program Name** | **Program Stage Name** | **Data Elements** | **Value Type** | **Menu Options** |
| --- | --- | --- | --- | --- |
| Claim - Services | Claimed Service | Service | TEXT | Options depends on openIMIS database |
||| Service Quantity | NUMBER ||
||| Service Price | NUMBER ||
||| Adjusted amount - Service | NUMBER ||
||| Approved amount - Service | NUMBER ||
||| Deductible amount - Service | NUMBER ||
||| Exceeded ceiling - Amount | NUMBER ||
||| Renumerted Amount - Service | NUMBER ||
||| Valuated amount - Service | NUMBER ||
||| Sequence ID | NUMBER ||
 
1. **Items Detail**

**Program Stage Name:** Claim - Items

**Type:** Repeatable (This stage will be created each time for capturing details for each item incurred by the insuree from the facility). For example, the claim in question has 10 items, then 10 events will be created for each service.

Below are the data elements captured in the Claim – Items program stage concerning the context of openIMIS Nepal implementation, these details can be changed based on the local context in openIMIS country implementations.

| **Program Name** | **Program Stage Name** | **Data Elements** | **Value Type** | **Menu Options** |
| --- | --- | --- | --- | --- |
| **Claims Management** | Claim - Items | Claimed Item | NUMBER | Options depends on openIMIS database |
 ||| Item Quantity | NUMBER ||
 ||| Item Price | NUMBER ||
 ||| Adjusted amount - Item | NUMBER ||
 ||| Approved amount – Item | NUMBER ||
 ||| Deductible amount - Item | NUMBER ||
 ||| Exceeded ceiling amount - Item | NUMBER ||
 ||| Remunerated Amount - Service | NUMBER ||
 ||| Valuated amount - Service | NUMBER ||
 ||| Sequence ID | NUMBER ||

## 3.2 Data Analysis

The data analysis will utilize the following modules in DHIS2 both for analyzing the raw data, as well as the indicators, generate from aggregate, and event-based data.

  1. Data Visualiser
  2. Pivot Tables
  3. GIS
  4. Event Reports
  5. Dashboards

Each of the above modules will be assisted with the following data dimensions, which help in adding additional layers to the data analysis:

### 3.3.1 Organisation Unit Dimensions

#### **3.3.1.1 Organisation unit groups and Group Sets**

The organisation unit groups will be created based on the facility attributes such as given below. The list has been generated from the reporting facilities available in the openIMIS Nepal implementation. These lists can be altered based on localised context of the country implementation.

**Facility-type Groups**

1. PHC
2. PHCC
3. District Hospitals
4. Zonal Hospitals
5. Medical College/Teaching Hospitals
6. NGOs

**Facility-wise Groups**

1. Primary Health Centres
2. General Hospitals
3. Eye Hospitals
4. Cardiothoracic and Vascular Hospitals
5. Cancer Hospitals
6. Health Institutes
7. Polytechnic Institutes

**Location-wise Groups**

1. Urban
2. Rural

**Facility type-wise groups**

1. Public facilities
2. Private facilities

Based on the above groups and group sets defined the analytics engine in DHIS2 will aggregate the data which can be used to carry out the analysis of data both raw data and indicators by adding these additional dimensions to understand the reach and coverage of services.

### 3.3.4 Indicator Dimensions

#### **Indicator groups**

1. Beneficiary Management
2. Claims Management
3. Operations Management

All indicators falling under the above groups have been defined in the requirements document along with their source.


### Dashboards

DHIS2 Dashboards app will be configured to create dashboards based on the following proposed structure, and the content:

1. **Beneficiary Management**

- Policy Management
- Individuals with an active policy
- Individuals enrolled and not covered
- Households with an active policy
- Households enrolled and not covered

1. **Claims Management**

- Claims Management
- Claims-Service Utilisation
- Claims-Item Utilisation


# **User management**

The following user roles and users are being proposed, but we expect the list to grow during the capacity-building phase and in discussions with the HIC-MoH team.

## 4.1 Admin user/Superuser

This role will be assigned to the system administrator. This role will enable the super user to manage, maintain, and configure the application, which involves various tasks such modifying organisation units, adding new data elements, indicators, creating new users, resetting passwords etc.

## 4.2 District User

This role will be assigned to the users at the district level. This role will allow the user to access the data entry, data quality, data analysis, and output/reporting modules of their particular district. Using these modules the user can, generate reports and analyse trends in data using the analysis tools.

## 4.3 Facility User

This user role allows the user to enter data for the respective facility, generate reports, and perform data quality checks and analysis.


## 4.4 Health Insurance Board/National Insurance Agency

User roles will be created and assigned to a user belonging to Health Insurance Board/National Insurance Agency in the country to allow them to access data for their specific thematic areas such as Beneficiary Enrollments/Coverage, Claims etc. and evaluate across the country/region/district depending upon their administrative authority. They can access reports, perform data analysis and use dashboards.


# **ADX Formatting** 
### ADX Data definition 
ADX Data definition can be defined using `dhis2_etl.adx_transform.adx_models.ADXMappingCubeDefinition`. 
```python 
ADXMappingCubeDefinition(
    name=str, # Name of ADX Mapping Definition 
    period_type=ISOFormatPeriodType(), # Format of handled period type, at the moment only ISO Format is supported 
    groups=[
        ADXMappingGroupDefinition(
            comment=str, # Generic comment 
            dataset=Model, # Django model, used as base for data value calcultions
            data_values=[
                ADXMappingDataValueDefinition(
                    data_element=str, # Name of calculated value 
                    related_from_dataset_func=function # Function extracting collection from group dataset object
                    aggregation_function=function # Function transofrming filtered queryset to dataset value 
                    categories=[
                        ADXMappingCategoryDefinition(
                            category_name=str,
                            category_options=[
                                ADXCategoryOptionDefinition(
                                    code=code,
                                    filter=function # Function Filtering output of `related_from_dataset_func`
                                )
    ])])])])
```
#### Example definition: [HF Number of insurees](dhis2_etl/tests/adx_tests.py)

### ADX Data Storage 
`dhis2_etl.adx_transform.adx_mapper.ADXBuilder` is used for creating ADX Data collection
based on data definition. 
Example:

```python
from dhis2_etl.adx_transform.builders import ADXBuilder
from dhis2_etl.adx_transform.adx_models.adx_definition import ADXMappingGroupDefinition

definition = ADXMappingGroupDefinition(...)
builder = ADXBuilder(definition)
period_type = "2019-01-01/P2Y"  # In format accepted by definition.period_type
org_units = HealthFaciltity.objects.filter(validity_to__isnull=True).values_list("uuid", flat=True)  # All HF
builder.create_adx_cube(period_type, org_units)  # Returns ADXMapping object
```

### ADX Formatters
ADX Formatters allow transforming ADXMapping objects to diffrent formats. 
At the moment only XML Format is implemented.

```python
from dhis2_etl.adx_transform.formatters import XMLFormatter
from dhis2_etl.adx_transform.adx_models.adx_data import ADXMapping

adx_format = ADXMapping(...)
xml_formatter = XMLFormatter()
xml_format = xml_formatter.format_adx(adx_format)
```

