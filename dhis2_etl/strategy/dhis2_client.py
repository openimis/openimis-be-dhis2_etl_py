import datetime
import json
# import the logging library
import logging
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from dhis2 import Api

from dhis2_etl.models.dhis2.enum import ImportStrategy, MergeMode
from dict2obj import Dict2Obj
from django.core.paginator import Paginator

from dhis2_etl.configurations import GeneralConfiguration

# Get an instance of a logger
logger = logging.getLogger('openIMIS')
# Get DHIS2 credentials from the config
dhis2 = Dict2Obj(GeneralConfiguration.get_dhis2())
# create the DHIS2 API object
api = Api(dhis2.host, dhis2.username, dhis2.password)
# define the page size
page_size = int(GeneralConfiguration.get_default_page_size())

path = GeneralConfiguration.get_json_out_path()


def printPaginated(ressource, queryset, convertor,  **kwargs):
    local_page_size = kwargs.get('page_size', page_size)
    p = Paginator(queryset, local_page_size)
    pages = p.num_pages
    curPage = 1
    logger.debug('print paginated %s, %i pages', ressource, pages)
    timestamp = datetime.datetime.now().strftime("%d%m%Y%H%M%S.%f")
    while curPage <= pages:
        f = open(path + '\out_' + timestamp + '_' + ressource + '-' + str(curPage) + ".json", "w+")
        page = p.page(curPage)
        Obj = page.object_list
        objConv = convertor(Obj, **kwargs)
        f.write(json.dumps(objConv.dict(exclude_none=True, exclude_defaults=True)))
        f.close()
        curPage += 1


def postPaginatedThreaded(ressource, queryset, convertor, **kwargs):
    local_page_size = kwargs.get('page_size', page_size)
    p = Paginator(queryset, local_page_size)
    pages = p.num_pages
    curPage = 1
    futures = []
    max_workers=6
    logger.debug('post paginated threaded %s, %i pages, %i workers', ressource, pages, max_workers)
    with  ThreadPoolExecutor(max_workers=max_workers) as executor:
        while curPage <= pages:
            page = p.page(curPage)
            futures.append(executor.submit(postPage, ressource=ressource, page=page, convertor=convertor, **kwargs))
            curPage += 1
    responses = []
    for future in futures:
        res = future.result()
        if res is not None:
            responses.append(res)
    return responses


def postPaginated(ressource, queryset, convertor, **kwargs):
    local_page_size = kwargs.get('page_size', page_size)
    p = Paginator(queryset, local_page_size)
    pages = p.num_pages
    curPage = 1
    responses = []
    logger.debug('post paginated %s, %i pages', ressource, pages)
    while curPage <= pages:
        page = p.page(curPage)
        postPage(ressource, page, convertor, **kwargs)
        # responses.append(postPage(ressource,page,convertor))
        curPage += 1
    return responses


def post(ressource, objs, convertor, **kwargs):
    # just to retrive the value of the queryset to avoid calling big count .... FIXME a better way must exist ...

    objConv = convertor(objs, **kwargs)

    # Send the Insuree page per page, page size defined by config get_default_page_size
    jsonPayload = objConv.dict(exclude_none=True, exclude_defaults=True)
    logger.debug('Paylaod: %s', json.dumps(jsonPayload, indent=2))
    try:
        response = api.post(
            ressource,
            json=jsonPayload,
            params={'mergeMode': MergeMode.merge}) #,'importStrategy':'CREATE_AND_UPDATE'}) #, "async":"false", "preheatCache":"true"})
        logger.debug(response)
        # fix me to avoid too much ram
        return None
    except requests.exceptions.RequestException as e:
        if e.code == 409:
            response = {'status_code': e.code, 'url': e.url, 'text': e.description}
            logger.debug(e)
            return response
            pass
        else:
            logger.error(e)


def postPage(ressource, page, convertor, **kwargs):
    # just to retrive the value of the queryset to avoid calling big count .... FIXME a better way must exist ...
    obj = page.object_list
    objConv = convertor(obj, **kwargs)

    # Send the Insuree page per page, page size defined by config get_default_page_size
    jsonPayload = objConv.dict(exclude_none=True, exclude_defaults=True)
    logger.debug('Paylaod: %s', json.dumps(jsonPayload, indent=2))
    try:
        response = api.post(
            ressource,
            json=jsonPayload,
            params={'mergeMode': MergeMode.merge,'strategy':ImportStrategy.createUpdate}) #, "async":"false", "preheatCache":"true"})
        logger.debug(response)
        # fix me to avoid too much ram
        return None
    except requests.exceptions.RequestException as e:
        if e.code == 409:
            response = {'status_code': e.code, 'url': e.url, 'text': e.description}
            logger.debug(e)
            return response
            pass
        else:
            logger.error(e)

def postRaw(ressource,objConv, **kwargs):   
    # Send the Insuree page per page, page size defined by config get_default_page_size
    jsonPayload = objConv.dict(exclude_none=True, exclude_defaults=True)
    logger.debug('Paylaod: %s', json.dumps(jsonPayload, indent=2))
    try:
        response = api.post(
            ressource,
            json=jsonPayload,
            params={'mergeMode': MergeMode.merge,'strategy':ImportStrategy.createUpdate}) #, "async":"false", "preheatCache":"true"})
        logger.debug(response)
        # fix me to avoid too much ram
        return None
    except requests.exceptions.RequestException as e:
        if e.code == 409:
            response = {'status_code': e.code, 'url' : e.url, 'text' : e.description}
            logger.debug(e)
            return response
            pass
        else:
            logger.error(e)
            
            
