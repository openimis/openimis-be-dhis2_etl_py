from django.db.models import Q, F
from medical.models import Diagnosis, Item, Service
from product.models import Product

from dhis2_etl.services.locationServices import syncRegion, syncDistrict, syncWard, syncVillage, syncHospital, \
    syncDispensary, syncHealthCenter
from dhis2_etl.services.optionSetServices import syncProduct, syncGender, syncProfession, syncGroupType, syncEducation, \
    syncDiagnosis, syncItem, syncService
from location.models import Location, HealthFacility


def has_model_changed_in_timeframe(model_qs, from_date, to_date):\
    return model_qs.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=to_date)\
        .filter(validity_from__gte=from_date)\
        .exists()


def sync_product_if_changed(from_date, to_date):
    if has_model_changed_in_timeframe(Product.objects, from_date, to_date):
        return syncProduct(from_date, to_date)


def sync_optionset_if_changed(from_date, to_date):
    # Doesn't have validity_to attribute
    syncGender(from_date, to_date)
    syncProfession(from_date, to_date)
    syncGroupType(from_date, to_date)
    syncEducation(from_date, to_date)
    if has_model_changed_in_timeframe(Diagnosis.objects, from_date, to_date):
        syncDiagnosis(from_date, to_date)
    if has_model_changed_in_timeframe(Item.objects, from_date, to_date):
        syncItem(from_date, to_date)
    if has_model_changed_in_timeframe(Service.objects, from_date, to_date):
        syncService(from_date, to_date)


def sync_location_if_changed(from_date, to_date):
    # Location
    base_location_qs = Location.objects\
        .filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id'))).all()

    location_levels = {
        'region': (base_location_qs.filter(type='R'), syncRegion),
        'district': (base_location_qs.filter(type='D'), syncDistrict),
        'ward': (base_location_qs.filter(type='W'), syncWard),
        'village': (base_location_qs.filter(type='V'), syncVillage)
    }

    # Health Facility
    base_hf_qs = HealthFacility.objects\
        .filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id'))).all()

    location_levels.update({
        'hospital': (base_hf_qs.filter(level='H'), syncHospital),
        'dispensary': (base_hf_qs.filter(level='D'), syncDispensary),
        'center': (base_hf_qs.filter(level='C'), syncHealthCenter),
    })

    for qs, sync_func in location_levels.values():
        if has_model_changed_in_timeframe(qs, from_date, to_date):
            sync_func(from_date, to_date)
