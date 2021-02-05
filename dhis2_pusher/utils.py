from django.core.paginator import Paginator
from dhis2 import Api

from .configurations import GeneralConfiguration
from dict2obj import Dict2Obj
import datetime
import requests
import re
from concurrent.futures.thread import ThreadPoolExecutor
import json

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Get DHIS2 credentials from the config
dhis2 = Dict2Obj(GeneralConfiguration.get_dhis2())
# create the DHIS2 API object
api = Api(dhis2.host, dhis2.username, dhis2.password)
# define the page size
page_size = int(GeneralConfiguration.get_default_page_size())

def printPaginated(ressource,queryset, convertor):
    p = Paginator(queryset, page_size)
    pages = p.num_pages
    curPage = 1
    timestamp = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
    while curPage <= pages :
        f = open(r'C:\temp\out_'+timestamp+'_'+ressource+'-'+str(curPage)+".json", "w+")
        page = p.page(curPage)
        Obj = page.object_list
        objConv = convertor(Obj)
        f.write(json.dumps(objConv.dict(exclude_none=True, exclude_defaults=True)))
        f.close()
        curPage+=1

def postPaginated(ressource,queryset, convertor):
    p = Paginator(queryset, page_size)
    pages = p.num_pages
    curPage = 1
    futures = []
    with  ThreadPoolExecutor(max_workers=4) as executor:
        while curPage <= pages :
            page = p.page(curPage)
            futures.append(executor.submit(postPage, ressource = ressource, page = page, convertor = convertor))
            curPage+=1
    responses = []
    for future in futures:
        res = future.result()
        if res is not None:
            responses.append(res)
    return responses


def postPage(ressource,page,convertor):
    # just to retrive the value of the queryset to avoid calling big count .... FIXME a better way must exist ...
    obj = page.object_list
    objConv = convertor(obj)
    
    # Send the Insuree page per page, page size defined by config get_default_page_size
    jsonPayload = objConv.dict(exclude_none=True, exclude_defaults=True)
    try:
        response = api.post(ressource,\
            json = jsonPayload,\
            params = {'mergeMode': 'MERGE_IF_NOT_NULL','strategy':'CREATE_AND_UPDATE'}) #, "async":"false", "preheatCache":"true"})
        logger.info(response)
        return response
    except requests.exceptions.RequestException as e:
        if e.code == 409:
            response = {'status_code': e.code, 'url' : e.url, 'text' : e.description}
            logger.debug(e)
            return response
            pass
        else:
            logger.error(e)

def toDatetimeStr(dateIn): 
    if dateIn is None:
        return None
    elif isinstance(dateIn, datetime.datetime):
        return (dateIn.isoformat()+".000")[:23]
    elif isinstance(dateIn, datetime.date):
        return (dateIn.isoformat()+"T00:00:00.000")[:23]
    elif isinstance(dateIn, String):
        regex = re.compile("^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3,6})?$")
        if regex.match(dateIn):
            return (dateIn+".000")[:23]
        regex = re.compile("^\d{4}-\d{2}-\d{2}$")
        if regex.match(dateIn):
            return (dateIn+"T00:00:00.000")[:23]
        else:
            return None
    else:
        return None


def toDateStr(dateIn):
    if dateIn is None:
        return None
    elif isinstance(dateIn, datetime.datetime) or isinstance(dateIn, datetime.date):
        return dateIn.isoformat()[:10]
    elif isinstance(dateIn, String):
        regex = re.compile("^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d{3,6})?)?$")
        if regex.match(dateIn):
            return dateIn[:10]
        else:
            return None
    else:
        return None


