from datetime import timedelta
import cloudinary.uploader
from django.http import QueryDict
from django.utils import timezone
from core import models
from engagement.models import UserInteraction, Notification
from core import serializers
from core.base_models import ResultView
from engagement.models import UserInteraction
from users.utils import extract_payload_from_jwt
from django.db.models import Min, Max, F, Value, DecimalField, Q
from django.db.models.functions import Least, Greatest, Coalesce
from django.core.paginator import Paginator
import logging

# Create your services here.

# region Units
def propose_unit_service(request_data, client_id):
    result = ResultView()
    logger = logging.getLogger(__name__)
    try:
        if isinstance(request_data, QueryDict):
            request_data = request_data.copy()
        request_data['created_by_id'] = client_id
        serialized_unit = serializers.CreateUnitSerializer(data=request_data)
        if serialized_unit.is_valid():
            serialized_unit.save()
            interested_users_in_city = UserInteraction.objects.filter(
                city_id=request_data.get('city_id'),
                interaction_type__in=['register', 'filter']
            )
            interested_user_ids = interested_users_in_city.values_list('created_by_id', flat=True)
            if interested_users_in_city.exists():
                city = interested_users_in_city.first().city
                unit_type = 'قطعة أرض' if request_data['unit_type_id'] == "1" else "وحدة سكنية"
                notification_msg = f'تم إضافة {unit_type} جديدة فى مدينة {city.name}'
                notifications = [
                    Notification(created_by_id=user_id, message=notification_msg, city=city, unit_id=serialized_unit['id'])
                    for user_id in interested_user_ids
                ]
                Notification.objects.bulk_create(notifications)
            result.msg = 'تم حفظ الوحدة بنجاح'
            result.is_success = True
            result.data = serialized_unit.data
        else:
            result.msg = 'حدث خطأ أثناء معالجة البيانات'
            result.data = serialized_unit.errors
    except Exception as e:
        logger.error(f"Unexpected error in propose_unit_service: {e}", exc_info=True)
        result.msg = 'حدث خطأ غير متوقع أثناء حفظ الوحدة'
        result.data = {'error': str(e)}
    finally:
        return result

def request_unit_service(request_data, client_id):
    result = ResultView()
    try:
        # token = request_headers.get('Authorization', '')
        # token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
        request_data['created_by_id'] = client_id
        serialized_land_request = serializers.UnitRequestSerializer(data=request_data)
        if serialized_land_request.is_valid():
            serialized_land_request.save()
            result.msg = 'تم حفظ الطلب بنجاح'
            result.is_success = True
            result.data = serialized_land_request.data
        else:
            result.msg = 'حدث خطأ أثناء معالجة البيانات'
            result.data = serialized_land_request.errors
    except Exception as e:
        if str(e).__contains__('duplicate key value'):
            result.msg = 'لقد طلبت هذه الوحدة من قبل ولا يمكنك طلبها مره أخرى'
        else: 
            result.msg = 'حدث خطأ غير متوقع أثناء حفظ الطلب'
        result.data = {'error': str(e)}
    finally:
        return result

def paginated_client_requests_service(request_data, client_id):
    result = ResultView()
    try:
        page_number = int(request_data.get('page_number', 1))
        page_size = int(request_data.get('page_size', 10))
        client_requests = models.UnitRequest.objects.filter(is_deleted=False, created_by_id=client_id).order_by('-created_at')
        client_requests_count = client_requests.count()
        if client_requests_count <= 0:
            raise ValueError('لا يوجد طلبات متاحة')
        total_pages = (client_requests_count + page_size - 1) // page_size
        page_number = min(page_number, total_pages)
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        client_requests = client_requests[start_index:end_index]
        serialized_client_requests = serializers.GetAllRequestsSerializer(client_requests, many=True)
        result.data = serialized_client_requests.data
        result.is_success = True
        result.msg = 'تم جلب بيانات طلباتكم بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
        result.data = []
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب البيانات'
        result.data = {'error': str(e)}
    finally:
        return result

def cancel_request_service(request_id):
    result = ResultView()
    try:
        request = models.UnitRequest.objects.get(id=request_id)
        request.delete()
        result.is_success = True
        result.msg = 'تم إلغاء الطلب بنجاح'
    except models.UnitRequest.DoesNotExist as e:
        result.msg = 'الطلب غير موجود'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء إلغاء الطلب'
        result.data = {'errors': str(e)}
    finally:
        return result

def proposal_form_data_service():
    result = ResultView()
    try:
        cities = models.City.objects.filter(is_deleted=False).values('id', 'name').order_by('id')
        proposals = models.Proposal.objects.filter(is_deleted=False).values('id', 'name').order_by('id')
        unit_types = models.UnitType.objects.filter(is_deleted=False).values('id', 'name').order_by('id')
        unit_types_projects = models.UnitTypeProject.objects.filter(is_deleted=False)
        units = models.Unit.objects.filter(is_deleted=False).annotate(
            min_price=Least(
                Coalesce(F('over_price'), Value(float('inf'))),
                Coalesce(F('total_price'), Value(float('inf'))),
                Coalesce(F('meter_price'), Value(float('inf'))),
                default=Value(0),
                output_field=DecimalField()
            ),
            max_price=Greatest(
                Coalesce(F('over_price'), Value(float('-inf'))),
                Coalesce(F('total_price'), Value(float('-inf'))),
                Coalesce(F('meter_price'), Value(float('-inf'))),
                default=Value(0),
                output_field=DecimalField()
            )
        )
        min_price = units.aggregate(Min('min_price'))['min_price__min']
        max_price = units.aggregate(Max('max_price'))['max_price__max']
        data = {
            "proposals": list(proposals),
            "cities": list(cities),
            "min_price": min_price,
            "max_price": max_price,
            "min_area": units.aggregate(Min('area'))['area__min'],
            "max_area": units.aggregate(Max('area'))['area__max'],
            "unit_types": [],
            "floors": [{"id": choice[0], "name": choice[1]} for choice in models.Unit.FLOOR_CHOICES],
            "facades": [{"id": choice[0], "name": choice[1]} for choice in models.Unit.FACADE_CHOICES],
            "currencies": [{"id": choice[0], "name": choice[1]} for choice in models.Unit.CURRENCY_CHOICES]
        }
        for unit_type in unit_types:
            unit_types_data = {
                "id": unit_type['id'],
                "name": unit_type['name'],
                "projects": []
            }
            for utp in unit_types_projects.filter(unit_type_id=unit_type['id']):
                project_data = {
                    "id": utp.project.id,
                    "name": utp.project.name
                }
                unit_types_data["projects"].append(project_data)
            data["unit_types"].append(unit_types_data)
        result.data = data
        result.is_success = True
        result.msg = 'Success'
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب بيانات نموذج الإضافة'
        result.data = {'error': str(e)}
    finally:
        return result

def recent_units_service():
    result = ResultView()
    try:
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        recent_units = models.Unit.objects.filter(is_deleted=False, status__code__in=[0, 1, 2], created_at__gte=twenty_four_hours_ago)
        if recent_units.count() <= 0:
            raise ValueError('لا يوجد وحدات متاحة')
        serialized_recent_units = serializers.GetAllUnitsSerializer(recent_units, many=True)
        result.data = serialized_recent_units.data
        result.is_success = True
        result.msg = 'تم جلب أحدث الوحدات بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب البيانات'
        result.data = {'error': str(e)}
    finally:
        return result

def filter_paginated_units_service(request_data, user_id):
    result = ResultView()
    try:
        filters = Q(is_deleted=False)
        # Numeric Validations
        def validate_numeric(value, error_message):
            try:
                return float(value) if value is not None else None
            except (TypeError, ValueError):
                raise ValueError(error_message)
        min_price = validate_numeric(request_data.get('min_price'), "أقل سعر يجب أن يكون رقم صحيحاً")
        max_price = validate_numeric(request_data.get('max_price'), "أقصى سعر يجب أن يكون رقم صحيحاً")
        min_area = validate_numeric(request_data.get('min_area'), "أقل مساحة يجب أن يكون رقم صحيحاً")
        max_area = validate_numeric(request_data.get('max_area'), "أقصى مساحة يجب أن يكون رقم صحيحاً")
        if min_price and max_price and min_price > max_price:
            raise ValueError("أقل سعر لا يمكن أن يكون أكبر من أقصى سعر")
        if min_area and max_area and min_area > max_area:
            raise ValueError("أقل مساحة لا يمكن أن يكون أكبر من أقصى مساحة")
        # Add Filters Conditionally
        if request_data.get('unit_type_id'):
            filters &= Q(unit_type__id=request_data['unit_type_id'])
        if request_data.get('proposal_id'):
            filters &= Q(proposal__id=request_data['proposal_id'])
        if request_data.get('project_id'):
            filters &= Q(project__id=request_data['project_id'])
        if request_data.get('city_id'):
            filters &= Q(city__id=request_data['city_id'])
            if user_id:
                UserInteraction.objects.update_or_create(
                    created_by_id=user_id,
                    city_id=request_data['city_id'],
                    interaction_type='filter',
                    defaults={'updated_at': timezone.now()}
                )
        if min_area:
            filters &= Q(area__gte=min_area)
        if max_area:
            filters &= Q(area__lte=max_area)
        if min_price:
            filters &= Q(total_price__gte=min_price)
        if max_price:
            filters &= Q(total_price__lte=max_price)
        if request_data.get('facade'):
            filters &= Q(facade=request_data['facade'])
        if request_data.get('floor'):
            filters &= Q(floor=request_data['floor'])
        if request_data.get('featured'):
            filters &= Q(featured=request_data['featured'])
        # Fetch Filtered Units
        units = models.Unit.objects.filter(filters)
        if not units.exists():
            raise ValueError('لا يوجد وحدات متاحة')
        # Sorting
        sort_fields = {
            'date': 'created_at',
            'price': 'total_price',
            'area': 'area',
            'most_viewed': 'view_count'
        }
        sorting_key = next((sort_fields[key] for key in sort_fields if request_data.get(key)), None)
        if sorting_key:
            ordering = sorting_key if request_data.get('asc', True) else f'-{sorting_key}'
            units = units.order_by(ordering)
        # Pagination
        paginator = Paginator(units, int(request_data.get('page_size', 12)))
        page_number = int(request_data.get('page_number', 1))
        page = paginator.get_page(page_number)
        # Serialize Data
        serialized_units = serializers.GetAllUnitsSerializer(page.object_list, many=True)
        result.data = {
            "all": serialized_units.data,
            "pagination": {
                "total_items": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page.number,
                "has_next": page.has_next(),
                "has_previous": page.has_previous()
            }
        }
        result.is_success = True
        result.msg = 'تم تحديث الوحدات بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
        result.data = {"all": []}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب البيانات'
        result.data = {'error': str(e)}
    finally:
        return result

# def filter_paginated_units_service(request_data):
#     result = ResultView()
#     try:
#         # Extract filters
#         unit_type_id = request_data.get('unit_type_id')
#         proposal_id = request_data.get('proposal_id')
#         project_id = request_data.get('project_id')
#         city_id = request_data.get('city_id')
#         min_price = request_data.get('min_price')
#         max_price = request_data.get('max_price')
#         min_area = request_data.get('min_area')
#         max_area = request_data.get('max_area')
#         currency = request_data.get('currency')
#         facade = request_data.get('facade')
#         floor = request_data.get('floor')
#         featured = request_data.get('featured')
#         sorting = request_data.get('sorting', False)
#         asc = request_data.get('asc', True)
#         price = request_data.get('price')
#         date = request_data.get('date')
#         area = request_data.get('area')
#         most_viewed = request_data.get('most_viewed')
#         page_number = int(request_data.get('page_number', 1))
#         page_size = int(request_data.get('page_size', 12))
#         filters = {
#             'is_deleted': False,
#             # 'status__code__in': [0, 1, 2]
#         }
#         # price validation
#         if min_price is not None:
#             try:
#                 min_price = float(min_price)
#             except (TypeError, ValueError):
#                 raise ValueError("أقل سعر يجب أن يكون رقم صحيحاً")
#         if max_price is not None:
#             try:
#                 max_price = float(max_price)
#             except (TypeError, ValueError):
#                 raise ValueError("أقصى سعر يجب أن يكون رقم صحيحاً")
#         if min_price is not None and max_price is not None and min_price > max_price:
#             raise ValueError("أقل سعر لا يمكن أن يكون أكبر من أقصى سعر")
#         # area validation
#         if min_area is not None:
#             try:
#                 min_area = float(min_area)
#             except (TypeError, ValueError):
#                 raise ValueError("أقل مساحة يجب أن يكون رقم صحيحاً")
#         if max_area is not None:
#             try:
#                 max_area = float(max_area)
#             except (TypeError, ValueError):
#                 raise ValueError("أقصى مساحة يجب أن يكون رقم صحيحاً")
#         if min_area is not None and max_area is not None and min_area > max_area:
#             raise ValueError("أقل مساحة لا يمكن أن يكون أكبر من أقصى مساحة")
#         if unit_type_id:
#             filters['unit_type__id'] = unit_type_id
#         if proposal_id:
#             filters['proposal__id'] = proposal_id
#         if project_id:
#             filters['project__id'] = project_id
#         if city_id:
#             filters['city__id'] = city_id
#         if min_area and max_area:
#             filters['area__gte'] = min_area
#             filters['area__lte'] = max_area
#         if min_price:
#             filters['total_price__gte'] = min_price
#         if max_price:
#             filters['total_price__lte'] = max_price
#         if currency:
#             filters['total_price_currency'] = currency
#         if facade:
#             filters['facade'] = facade
#         if floor:
#             filters['floor'] = floor
#         if featured:
#             filters['featured'] = featured
#         units = models.Unit.objects.filter(**filters)
#         if sorting:
#             if date:
#                 units = units.order_by('created_at') if asc else units.order_by('-created_at')
#             if price:
#                 units = units.order_by('total_price') if asc else units.order_by('-total_price')
#             if area:
#                 units = units.order_by('area') if asc else units.order_by('-area')
#             if most_viewed:
#                 units = units.order_by('view_count') if asc else units.order_by('-view_count')
#         all_units_count = units.count()
#         if all_units_count <= 0:
#             raise ValueError('لا يوجد وحدات متاحة')
#         total_pages = (all_units_count + page_size - 1) // page_size
#         page_number = min(page_number, total_pages)
#         start_index = (page_number - 1) * page_size
#         end_index = start_index + page_size
#         units = units[start_index:end_index]
#         serialized_units = serializers.GetAllUnitsSerializer(units, many=True)
#         result.data = {
#             "all": serialized_units.data,
#             "pagination": {
#                 "total_items": all_units_count,
#                 "total_pages": total_pages,
#                 "current_page": page_number,
#                 "has_next": page_number < total_pages,
#                 "has_previous": page_number > 1
#             }
#         }
#         result.is_success = True
#         result.msg = 'Success'
#     except ValueError as ve:
#         result.msg = str(ve)
#         result.is_success = True
#         result.data = {
#             "all": []
#         }
#     except Exception as e:
#         result.msg = 'حدث خطأ غير متوقع أثناء جلب البيانات'
#         result.data = {'error': str(e)}
#     finally:
#         return result

def unit_details_service(unit_id, user_id):
    result = ResultView()
    try:
        unit = models.Unit.objects.filter(is_deleted=False, id=unit_id).first()
        if not unit:
            raise ValueError('الوحدة غير موجودة')
        same_city_units = (
            models.Unit.objects.filter(is_deleted=False, city=unit.city)
                .exclude(id=unit_id).order_by('-updated_at')
            or models.Unit.objects.filter(is_deleted=False, project=unit.project)
                .exclude(id=unit_id).order_by('-updated_at')
            or models.Unit.objects.filter(is_deleted=False, proposal=unit.proposal)
                .exclude(id=unit_id).order_by('-updated_at')
        )
        unit.view_count += 1
        unit.save()
        if user_id:
            UserInteraction.objects.update_or_create(
            created_by_id=user_id,
            unit=unit,
            interaction_type='view',
            defaults={'updated_at': timezone.now()}
        )
        serialized_unit = serializers.UnitDetailsSerializer(unit)
        serialized_same_city_units = serializers.GetAllUnitsSerializer(same_city_units[:12], many=True)
        result.data = {
            'unit_details': serialized_unit.data,
            'discover_more': serialized_same_city_units.data
        }
        result.is_success = True
        result.msg = 'تم جلب تفاصيل الوحدة بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب تفاصيل الوحدة'
        result.data = {'error': str(e)}
    finally:
        return result

def paginated_client_units_service(request_data, client_id):
    result = ResultView()
    try:
        page_number = request_data.get('page_number', 1)
        page_size = request_data.get('page_size', 12)
        units = models.Unit.objects.filter(is_deleted=False, created_by_id=client_id)
        all_units_count = units.count()
        if all_units_count <= 0:
            raise ValueError('لا يوجد وحدات متاحة')
        total_pages = (all_units_count + page_size - 1) // page_size
        page_number = min(page_number, total_pages)
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        units = units[start_index:end_index]
        serialized_units = serializers.GetAllUnitsSerializer(units, many=True)
        result.data = {
            "all": serialized_units.data,
            "pagination": {
                "total_items": all_units_count,
                "total_pages": total_pages,
                "current_page": page_number,
                "has_next": page_number < total_pages,
                "has_previous": page_number > 1
            }
        }
        result.is_success = True
        result.msg = 'Success'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
        result.data = {
            "all": []
        }
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب الوحدات الخاصة بكم'
        result.data = {'error': str(e)}
    finally:
        return result

def get_update_unit_service(unit_id, user_obj):
    result = ResultView()
    try:
        if user_obj.is_staff and user_obj.groups.filter(name__in=['Manager', 'Admin']):
            unit_data = models.Unit.objects.get(id=unit_id)
        else:
            unit_data = models.Unit.objects.get(id=unit_id, created_by=user_obj)
        serialized_unit_data = serializers.UpdateUnitSerializer(unit_data)
        result.data = serialized_unit_data.data
        result.is_success = True
        result.msg = 'تم جلب بيانات الوحدة بنجاح'
    except models.Unit.DoesNotExist as e:
        result.msg = 'الوحدة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب بيانات الوحدة'
        result.data = {'errors': str(e)}
    finally:
        return result

def update_unit_service(request_data, user_obj):
    result = ResultView()
    try:
        if isinstance(request_data, QueryDict):
            request_data = request_data.copy()
        request_data['update'] = True
        request_data['created_by'] = user_obj
        request_data['created_by_id'] = user_obj.id
        logger = logging.getLogger(__name__)
        serialized_updated_unit = serializers.CreateUnitSerializer(data=request_data)
        if serialized_updated_unit.is_valid():
            serialized_updated_unit.save()
            interested_users_in_unit = UserInteraction.objects.filter(
                unit_id=request_data.get('unit_id'),
                interaction_type__in=['view', 'favorite']
            )
            interested_user_ids = interested_users_in_unit.values_list('created_by_id', flat=True)
            if interested_users_in_unit.exists():
                unit = interested_users_in_unit.first().unit
                notification_msg = f'حدث تحديث فى بيانات الوحدة ({unit.title[:14]}...) !'
                notifications = [
                    Notification(created_by_id=user_id, message=notification_msg, city_id=serialized_updated_unit['city_id'], unit=unit)
                    for user_id in interested_user_ids
                ]
                Notification.objects.bulk_create(notifications)
            result.msg = 'تم تحديث الوحدة بنجاح'
            result.is_success = True
        else:
            result.msg = 'حدث خطأ أثناء معالجة بيانات الوحدة'
            result.data = serialized_updated_unit.errors
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تعديل الوحدة'
        result.data = {'errors': str(e)}
        logger.error(str(e))
    finally:
        return result

def hard_delete_unit_service(unit_id):
    result = ResultView()
    try:
        unit_obj = models.Unit.objects.get(id=unit_id)
        allimgs = unit_obj.unitimage_set.all()
        print(allimgs)
        counter = 0
        for img in allimgs:
            counter += 1
            print(f"img number {counter} is {img}")
            if img.image:
                print(f'found image inside img number {counter} and here it is {img.image} and that\'s the public id => {img.image.public_id} and we r gonna destroy it')
                api_call_res = cloudinary.uploader.destroy(img.image.public_id)
                print('destroyed it successfully, moving to next one')
                print(f'and here is the api call result => {api_call_res}')
            else:
                print(f'didn\'t find image inside img number {counter} instead it\'s {img.image} so we skip')
        print(f'finished destroying all images in for loop now to delete all the images query from db and here it is before deleting => {allimgs}')
        allimgs.delete()
        print(f'deleted all imgs from db successfully and here it is after deleting => {allimgs}')
        print(f'now to delete the unit itself => {unit_obj}')
        unit_obj.delete()
        print(f'deleted the unit itself successfully, after deletion => {unit_obj}')
        result.is_success = True
        result.msg = 'تم حذف الوحدة بنجاح'
    except models.Unit.DoesNotExist as e:
        result.msg = 'الوحدة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حذف الوحدة'
        result.data = {'errors': str(e)}
    finally:
        return result
# endregion

# region Home
def home_reviews_service():
    result = ResultView()
    try:
        top_reviews = models.ClientReview.objects.filter(is_deleted=False, rate__gte=4)[:15]
        serialized_reviews = serializers.ReviewSerializer(top_reviews, many=True)
        result.data = serialized_reviews.data
        result.is_success = True
        result.msg = "Success"
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب البيانات'
        result.data = {'error': str(e)}
    finally:
        return result

def home_articles_service():
    result = ResultView()
    try:
        articles = models.Article.objects.filter(is_deleted=False)
        serialized_articless = serializers.ArticleSerializer(articles, many=True)
        result.data = serialized_articless.data
        result.is_success = True
        result.msg = "Success"
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب البيانات'
        result.data = {'error': str(e)}
    finally:
        return result

def home_consultation_types_service():
    result = ResultView()
    try:
        consult_types = models.ConsultationType.objects.filter(is_deleted=False)
        result.data = serializers.ConsultationTypeSerializer(consult_types, many=True).data
        result.is_success = True
        result.msg = "تم جلب أنواع الإستشارات بنجاح"
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب أنواع الإستشارات'
        result.data = {'error': str(e)}
    finally:
        return result

def consultations_by_type_service(consult_type_id):
    result = ResultView()
    try:
        consults_by_type = models.Consultation.objects.filter(is_deleted=False, consultation_type__id=consult_type_id)
        serialized_consults = serializers.ConsultationSerializer(consults_by_type, many=True)
        result.data = serialized_consults.data
        result.is_success = True
        result.msg = "تم جلب الإستشارات بنجاح"
    except Exception as e:
        result.msg = "حدث خطأ غير متوقع أثناء جلب الإستشارات"
        result.data = {'error': str(e)}
    finally:
        return result

def home_featured_units_service():
    result = ResultView()
    try:
        units = models.Unit.objects.filter(is_deleted=False, status__code__in=[0, 1, 2], featured=True)
        if units.count() <= 0:
            raise ValueError('لا يوجد وحدات متاحة')
        serialized_featured_units = serializers.GetAllUnitsSerializer(units, many=True)
        result.data = serialized_featured_units.data
        result.is_success = True
        result.msg = 'Success'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب الوحدات المميزة'
        result.data = {'error': str(e)}
    finally:
        return result

def home_most_viewed_units_service():
    result = ResultView()
    try:
        most_viewed_units = models.Unit.objects.filter(is_deleted=False, status__code__in=[0, 1, 2]).order_by('-view_count')[:12]
        if most_viewed_units.count() <= 0:
            raise ValueError('لا يوجد وحدات متاحة')
        serialized_most_viewed_units = serializers.GetAllUnitsSerializer(most_viewed_units, many=True)
        result.data = serialized_most_viewed_units.data
        result.is_success = True
        result.msg = 'Success'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب الوحدات الأكثر عرضاً'
        result.data = {'error': str(e)}
    finally:
        return result
# endregion

# region Draw Results | Reviews | Contact Us
def draw_results_service(request_data):
    result = ResultView()
    try:
        applicant_name = request_data.get('full_name')
        if applicant_name:
            print(applicant_name.replace(' ', '').replace('ة', 'ه').replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ؤ', 'و').replace('ئ', 'ي').replace('ى', 'ي').replace('ء', 'ا'))
            draw_results = models.DrawResult.objects.filter(is_deleted=False, search_name__icontains=applicant_name.replace(' ', '').replace('ة', 'ه').replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ؤ', 'و').replace('ئ', 'ي').replace('ى', 'ي').replace('ء', 'ا'))
            normaldraw_results = models.DrawResult.objects.filter(is_deleted=False, winner_name__icontains=applicant_name)
            print('search name look up => ', draw_results)
            print('winner normal name look up => ', normaldraw_results)
            if draw_results.count() == 1:
                serialized_draw_results = serializers.DrawResultSerializer(draw_results.first())
                result.data = serialized_draw_results.data
                result.is_success = True
                result.msg = "Success"
            elif draw_results.count() > 1:
                result.msg = "هذا الإسم مكرر؛ يرجى إدخال الإسم بالضبط كما هو فى الإستمارة"
            else:
                result.msg = "هذا الإسم غير موجود أو لم يفز"
        else:
            result.msg = f"لم يتم إرسال الإسم المطلوب؛ بدلا عن ذلك وصل {applicant_name}"
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء البحث'
        result.data = {'error': str(e)}
    finally:
        return result

def add_review_service(request_data, request_headers):
    result = ResultView()
    try:
        token = request_headers.get('Authorization', '')
        token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
        request_data['created_by_id'] = str(token_decode_result.get('user_id'))
        serialized_review = serializers.ReviewSerializer(data=request_data)
        if serialized_review.is_valid():
            serialized_review.save()
            result.data = serialized_review.data
            result.is_success = True
            result.msg = "تم حفظ التقييم بنجاح؛ شكراً لك"
        else:
            result.msg = "حدث خطأ أثناء معالجة البيانات"
            result.data = serialized_review.errors
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حفظ التقييم'
        result.data = {'error': str(e)}
    finally:
        return result

def add_contact_us_msg_service(request_data):
    result = ResultView()
    try:
        serialized_contact_us_msg = serializers.ContactUsSerializer(data=request_data)
        if serialized_contact_us_msg.is_valid():
            serialized_contact_us_msg.save()
            result.data = serialized_contact_us_msg.data
            result.is_success = True
            result.msg = "تم حفظ الرسالة بنجاح"
        else:
            result.msg = "حدث خطأ أثناء معالجة البيانات"
            result.data = serialized_contact_us_msg.errors
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حفظ الرسالة'
        result.data = {'error': str(e)}
    finally:
        return result
# endregion

# region Favorites
def add_favorite_service(request_data, request_headers):
    result = ResultView()
    try:
        token = request_headers.get('Authorization', '')
        token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
        request_data['created_by_id'] = str(token_decode_result.get('user_id'))
        serialized_favorite = serializers.UnitFavoriteSerializer(data=request_data)
        if serialized_favorite.is_valid():
            serialized_favorite.save()
            result.data = serialized_favorite.data
            result.is_success = True
            result.msg = "تم إضافة الوحدة للمفضلة بنجاح"
        else:
            result.msg = "حدث خطأ أثناء معالجة البيانات"
            result.data = serialized_favorite.errors
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء إضافة الوحدة للمفضلة'
        result.data = {'error': str(e)}
    finally:
        return result

def list_favorites_service(request_data, request_headers):
    result = ResultView()
    try:
        token = request_headers.get('Authorization', '')
        token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
        page_number = int(request_data.get('page_number', 1))
        page_size = int(request_data.get('page_size', 12))
        fav_units = UserInteraction.objects.filter(is_deleted=False, interaction_type='favorite', created_by_id=token_decode_result.get('user_id'))
        all_fav_units_count = fav_units.count()
        if all_fav_units_count <= 0:
            raise ValueError('لا يوجد وحدات مفضلة')
        if all_fav_units_count > page_size*(page_number-1):
            fav_units = fav_units[page_size*(page_number-1):page_size*page_number]
        else:
            fav_units = fav_units[page_size*int(all_fav_units_count/page_size) if all_fav_units_count%page_size!=0 else int(all_fav_units_count/page_size)-1:]
            page_number = int(all_fav_units_count/page_size) if all_fav_units_count%page_size == 0 else int(all_fav_units_count/page_size)+1
        total_pages = (all_fav_units_count + page_size - 1) // page_size
        page_number = min(page_number, total_pages)
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        fav_units = fav_units[start_index:end_index]
        serialized_units = serializers.UnitFavoriteSerializer(fav_units, many=True)
        result.data = {
            "all": serialized_units.data,
            "pagination": {
                "total_items": all_fav_units_count,
                "total_pages": total_pages,
                "current_page": page_number,
                "has_next": page_number < total_pages,
                "has_previous": page_number > 1
            }
        }
        result.is_success = True
        result.msg = 'Success'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
        result.data = {
            "all": []
        }
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب الوحدات المفضلة'
        result.data = {'error': str(e)}
    finally:
        return result

def delete_favorite_service(favorite_id):
    result = ResultView()
    try:
        UserInteraction.objects.get(is_deleted=False, id=favorite_id).delete()
        result.is_success = True
        result.msg = "تم إزالة الوحدة من المفضلة بنجاح"
    except UserInteraction.DoesNotExist as e:
        result.msg = 'لم يتم العثور على الوحدة المطلوبة'
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء إزالة الوحدة من المفضلة'
        result.data = {'error': str(e)}
    finally:
        return result
# endregion



