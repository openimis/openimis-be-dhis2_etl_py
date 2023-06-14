import logging
from dhis2_etl.models.adx.definition import *
from dhis2_etl.models.dhis2.metadata import Category,CategoryOption, DataElement,CategoryCombo,DataSet,DataSetElement
from dhis2_etl.utils import build_dhis2_id, clean_code
from dhis2_etl.models.dhis2.type import DHIS2Ref
from dhis2_etl.models.dhis2.enum import ValueType,DomainType,DataDimensionType,AggregationType,PeriodType

logger = logging.getLogger('openIMIS')
def build_categories(adx : ADXMappingCubeDefinition,   categoryOptions = [],  categories = {},    categoryCombo = {},   dataElement = [], dataSets = []):

    
    # for each adx group get the list of cat
    for group  in adx.groups:
        curDE = []
        for dv in group.data_values:
            dv_cat = {}
            
            for cat  in dv.categories:
                #save the cat / cat option
                options = build_categoryOption(cat.category_options, "categoryOption")
                if len(options)>0:
                    cat_id = build_dhis2_id(cat.category_name,'Category')
                    dv_cat[cat_id] =  Category(
                        id=cat_id,
                        dataDimensionType =  DataDimensionType.disagregation,
                        shortName=cat.category_name,
                        name = cat.category_name,
                        code = clean_code(cat.category_name),
                        categoryOptions = [DHIS2Ref(id=build_dhis2_id(x.code,"categoryOption")) for x in options]
                    )
                    # merge with main list
                    if cat_id not in categories:
                            categories[cat_id] = dv_cat[cat_id]
                            for opt in options:
                                if not any([catOpt.id == opt.id for catOpt in categoryOptions]):
                                    categoryOptions.append(opt)
                    else:
                        if any(len(x.categoryOptions) != len(cat.category_name) and x.name == cat.category_name for x in categories.values()):
                            logger.error('two categories have the same name but not the same amout of option')

            
            if len(dv_cat)>0:
                cat_keys= get_sorted_codes([x.name for x in dv_cat.values()])
                combo_name = '_'.join(cat_keys)
                combo_id = build_dhis2_id(combo_name, 'CategoryCombo')
                combo_code = '_'.join([x[:3] for x in cat_keys])
                if combo_name not in categoryCombo:
                    categoryCombo[combo_name]= CategoryCombo(
                        shortName=combo_code,
                        name = combo_name,
                        dataDimensionType =  DataDimensionType.disagregation,
                        id = combo_id,
                        code = clean_code(combo_code),
                        categories = [DHIS2Ref(id=x.id) for x in dv_cat.values()]
                    )
            else:
                combo_id = None

            curDE.append(DataElement(
                aggregationType = AggregationType.sum,
                domainType = DomainType.aggregate,
                valueType = ValueType.number,
                code = clean_code(dv.data_element), 
                name = dv.data_element, 
                shortName= dv.data_element, 
                id=build_dhis2_id(dv.data_element,'DataElement'),
                categoryCombo = None if combo_id is None else DHIS2Ref(id=combo_id),
            ))
        ds_id = build_dhis2_id(group.data_set,"DataSet")
        dataSets.append(DataSet(
            id =  ds_id,
            name = group.data_set,
            shortName = group.data_set,
            code =  clean_code(group.data_set),
            dataSetElements = build_dataSetElement(curDE, ds_id),
            periodType  = PeriodType.monthly
            
        ))
        dataElement += curDE
        
    return categoryOptions, categories , categoryCombo , dataElement , dataSets
  
def build_dataSetElement(dataElements, ds_id):
    res = []
    for de in dataElements:
        res.append(DataSetElement(
            dataElement= DHIS2Ref(id= de.id),
            dataSet=DHIS2Ref(id= ds_id)
        ))
    return res

def build_categoryOption(options, salt):
    dhis2_category_options = []
    for opt in options:
        dhis2_category_options.append(CategoryOption(
            code = clean_code(opt.code), 
            id = build_dhis2_id(opt.code, salt), 
            name = opt.name if opt.name is not None else opt.code, shortName = opt.code))
    return dhis2_category_options





def get_sorted_codes(code_list):
    return sorted([x.code for x in code_list]) if not isinstance(code_list[0], str) else sorted(code_list)