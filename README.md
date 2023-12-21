# openimis-be-dhis2_etl_py

openIMIS Module to push data into DHIS2


there is 2 methods available, both require to push for the metadata first: 
- ADX : pushd agregated data
- PROGAM :  push trackend entity program


## seting up the module

please update the django module configuration to with DHIS2 url and credentials

```
    "dhis2" : {
        "host":"https://play.dhis2.org/2.39/",
        "username":"admin",
        "password":"district"
    }

```

the full default configuration can be found in the app.py file where DE and program id could be updated

## Pushing metadata

can be done in one command 

`python manage.py pushmetadata 2000-01-01 all`

2000-01-01 is the reference date, it is use to push only newer data, usefull when updating the metadata

or can be done step by step are described below

    #. create or configure a  root orgunit

    `python manage.py pushmetadata 2000-01-01 createRoot`

    (python manage.py pushmetadata startdate enddate createRoot)

    ```
        "location":{
            "rootOrgUnit":"E0FtAX5eNc3",
            "rootOrgUnitName":"DemOpenIMIS",
            "rootOrgUnitCode":"Root",
            "attributes":{
                "locationId":"gMNNTAdZbW1",
                "locationType":"ffZOxd5V2UK"
            }
        },
    ```

    #. create openIMIS orgunit structure

    for the ADX, a function can be specified to do the mapping between the openIMIS orgunit and existing DHIS2 orgunit but this is not supported yet for the program

    `python manage.py pushmetadata 2000-01-01 orgunit`

    #. push the optionset

    this is only usefull for pogram


    `python manage.py pushmetadata 2000-01-01 optionset`

    This  will push optionset
        - gender 
        - profession 
        - groupType 
        - education 
        - product 
        - diagnosis 
        - item
        - service

    they all can be pushed manualy ex :  `python manage.py pushmetadata 2000-01-01 product`


 
## pushing program 

    `python manage.py pushprogram 2000-01-01 all`

    will update the enrolment then the policy, then the claim, then the funding

    each step can be done independently: 

    - `python manage.py pushprogram 2000-01-01 enroll`
    - `python manage.py pushprogram 2000-01-01 insureepolicies`
    - `python manage.py pushprogram 2000-01-01 insureepoliciesclaims`
    - `python manage.py pushprogram 2000-01-01 funding`


    it is also possible to send population data (in village) to DHIS2 witht he command `python manage.py pushprogram 2000-01-01 population`



    This will push data in 3 programs (TBC)
    - Family-insuree [enrollment] Policy [program registration / event]
    - Claims (claim details[program registration / event], Claims Services[event], Claim Items[event])
    - Funding (claim details[program registration / event], Claims Services[event], Claim Items[event])




## pushing ADX

    adx requires specific metadata definition that can be created automatically with 

    `python manage.py pushadx 2000-01-01 pushMetadata`


    then each month the datasets can be pushed via 


    `python manage.py pushadx 2023-02-01 pushMetadata`

    this code will push data for Jan 23

   

