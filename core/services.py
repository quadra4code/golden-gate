from datetime import timedelta
from django.utils import timezone
from core import models
from core import serializers
from core.base_models import ResultView
from users.utils import extract_payload_from_jwt
from django.db.models import Min, Max, F, Value, DecimalField
from django.db.models.functions import Least, Greatest, Coalesce
import logging

# Create your services here.

def propose_unit_service(request_data, request_headers):
    result = ResultView()
    logger = logging.getLogger(__name__)
    try:
        token = request_headers.get('Authorization', '')
        token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
        request_data['created_by_id'] = str(token_decode_result.get('user_id'))
        images = request_data.pop('images')
        serialized_unit = serializers.CreateUnitSerializer(data=request_data)
        if serialized_unit.is_valid():
            new_unit = serialized_unit.save()
            if images:
                unit_images = [models.UnitImage(unit=new_unit, image=img, created_by_id=request_data.get('created_by_id')) for img in images]
                models.UnitImage.objects.bulk_create(unit_images)
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

def request_unit_service(request_data, request_headers):
    result = ResultView()
    try:
        token = request_headers.get('Authorization', '')
        token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
        request_data['created_by_id'] = str(token_decode_result.get('user_id'))
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
            # "payment_methods": [{"id": choice[0], "name": choice[1]} for choice in models.Unit.PAYMENT_METHOD_CHOICES]
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
        result.msg = 'Success'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب البيانات'
        result.data = {'error': str(e)}
    finally:
        return result

def filter_paginated_units_service(request_data):
    result = ResultView()
    try:
        unit_type_id = request_data.get('unit_type_id')
        proposal_id = request_data.get('proposal_id')
        project_id = request_data.get('project_id')
        city_id = request_data.get('city_id')
        min_price = request_data.get('min_price')
        max_price = request_data.get('max_price')
        min_area = request_data.get('min_area')
        max_area = request_data.get('max_area')
        # payment_method = request_data.get('payment_method')
        facade = request_data.get('facade')
        floor = request_data.get('payment_method')
        page_number = int(request_data.get('page_number', 1))
        page_size = int(request_data.get('page_size', 12))
        filters = {
            'is_deleted': False,
            # 'status__code__in': [0, 1, 2]
        }
        # price validation
        if min_price is not None:
            try:
                min_price = float(min_price)
            except (TypeError, ValueError):
                raise ValueError("أقل سعر يجب أن يكون رقم صحيحاً")
        if max_price is not None:
            try:
                max_price = float(max_price)
            except (TypeError, ValueError):
                raise ValueError("أقصى سعر يجب أن يكون رقم صحيحاً")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValueError("أقل سعر لا يمكن أن يكون أكبر من أقصى سعر")
        # area validation
        if min_area is not None:
            try:
                min_area = float(min_area)
            except (TypeError, ValueError):
                raise ValueError("أقل مساحة يجب أن يكون رقم صحيحاً")
        if max_area is not None:
            try:
                max_area = float(max_area)
            except (TypeError, ValueError):
                raise ValueError("أقصى مساحة يجب أن يكون رقم صحيحاً")
        if min_area is not None and max_area is not None and min_area > max_area:
            raise ValueError("أقل مساحة لا يمكن أن يكون أكبر من أقصى مساحة")
        if unit_type_id:
            filters['unit_type__id'] = unit_type_id
        if proposal_id:
            filters['proposal__id'] = proposal_id
        if project_id:
            filters['project__id'] = project_id
        if city_id:
            filters['city__id'] = city_id
        if min_price and max_price:
            filters['price__gte'] = min_price
            filters['price__lte'] = max_price
        if min_area and max_area:
            filters['area__gte'] = min_area
            filters['area__lte'] = max_area
        # if payment_method:
        #     filters['payment_method'] = payment_method
        if facade:
            filters['facade'] = facade
        if floor:
            filters['floor'] = floor
        units = models.Unit.objects.filter(**filters)
        all_units_count = units.count()
        if all_units_count <= 0:
            raise ValueError('لا يوجد وحدات متاحة')
        if all_units_count > page_size*(page_number-1):
            units = units[page_size*(page_number-1):page_size*page_number]
        else:
            units = units[page_size*int(all_units_count/page_size) if all_units_count%page_size!=0 else int(all_units_count/page_size)-1:]
            page_number = int(all_units_count/page_size) if all_units_count%page_size == 0 else int(all_units_count/page_size)+1
        serialized_units = serializers.GetAllUnitsSerializer(units, many=True)
        result.data = {
            "all": serialized_units.data,
            "pagination": {
                "total_items": all_units_count,
                "total_pages": all_units_count/int(all_units_count/page_size) if all_units_count%page_size == 0 else int(all_units_count/page_size)+1,
                "current_page": page_number,
                "has_next": True if all_units_count > page_size*page_number else False,
                "has_previous": True if page_number > 1 else False
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
        result.msg = 'حدث خطأ غير متوقع أثناء جلب البيانات'
        result.data = {'error': str(e)}
    finally:
        return result

def unit_details_service(unit_id):
    result = ResultView()
    try:
        unit = models.Unit.objects.filter(is_deleted=False, id=unit_id).first()
        if not unit:
            raise ValueError('الوحدة غير موجودة')
        serialized_unit = serializers.UnitDetailsSerializer(unit)
        result.data = serialized_unit.data
        result.is_success = True
        result.msg = 'Success'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب البيانات'
        result.data = {'error': str(e)}
    finally:
        return result

def paginated_client_units_service(request_data, client_id):
    result = ResultView()
    try:
        page_number = request_data.get('page_number', 1)
        page_size = request_data.get('page_size', 1)
        client_units = models.Unit.objects.filter(created_by__id=client_id, is_deleted=False)
        client_units_count = client_units.count()
        if client_units_count <= 0:
            raise ValueError('لا يوجد وحدات متاحة')
        if client_units_count > page_size*(page_number-1):
            client_units = client_units[page_size*(page_number-1):page_size*page_number]
        else:
            client_units = client_units[page_size*int(client_units_count/page_size) if client_units_count%page_size!=0 else int(client_units_count/page_size)-1:]
            page_number = int(client_units_count/page_size) if client_units_count%page_size == 0 else int(client_units_count/page_size)+1
        serialized_client_units = serializers.GetAllUnitsSerializer(client_units, many=True)
        result.data = {
            "all": serialized_client_units.data,
            "pagination": {
                "total_items": client_units_count,
                "total_pages": client_units_count/int(client_units_count/page_size) if client_units_count%page_size == 0 else int(client_units_count/page_size)+1,
                "current_page": page_number,
                "has_next": True if client_units_count > page_size*page_number else False,
                "has_previous": True if page_number > 1 else False
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
        result.msg = 'حدث خطأ غير متوقع أثناء جلب البيانات'
        result.data = {'error': str(e)}
    finally:
        return result

def client_paginated_units_service(request_data, request_headers):
    result = ResultView()
    try:
        token = request_headers.get('Authorization', '')
        token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
        page_number = int(request_data.get('page_number', 1))
        page_size = int(request_data.get('page_size', 12))
        units = models.Unit.objects.filter(is_deleted=False, created_by_id=token_decode_result.get('user_id'))
        all_units_count = units.count()
        if all_units_count <= 0:
            raise ValueError('لا يوجد وحدات متاحة')
        if all_units_count > page_size*(page_number-1):
            units = units[page_size*(page_number-1):page_size*page_number]
        else:
            units = units[page_size*int(all_units_count/page_size) if all_units_count%page_size!=0 else int(all_units_count/page_size)-1:]
            page_number = int(all_units_count/page_size) if all_units_count%page_size == 0 else int(all_units_count/page_size)+1
        serialized_units = serializers.GetAllUnitsSerializer(units, many=True)
        result.data = {
            "all": serialized_units.data,
            "pagination": {
                "total_items": all_units_count,
                "total_pages": all_units_count/int(all_units_count/page_size) if all_units_count%page_size == 0 else int(all_units_count/page_size)+1,
                "current_page": page_number,
                "has_next": True if all_units_count > page_size*page_number else False,
                "has_previous": True if page_number > 1 else False
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
        units_data = []
        if units.count() <= 0:
            raise ValueError('لا يوجد وحدات متاحة')
        for unit in units:
            price = unit.over_price if unit.over_price else unit.total_price if unit.total_price else unit.meter_price
            price_type = 'الأوفر' if unit.over_price else 'الإجمالى' if unit.total_price else 'سعر المتر'
            units_data.append({
                "id": unit.id,
                "title": unit.title,
                "city": unit.city.name,
                "unit_type": unit.unit_type.name,
                "project": unit.project.name,
                "area": unit.area,
                "price_obj": {'price_type': price_type, 'price_value': f'{price:,.0f}', 'currency': unit.get_currency_display()}
            })
        result.data = units_data
        result.is_success = True
        result.msg = 'Success'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        result.msg = 'Unexpected error happened while saving request'
        result.data = {'error': str(e)}
    finally:
        return result

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
        fav_units = models.UnitFavorite.objects.filter(is_deleted=False, created_by_id=token_decode_result.get('user_id'))
        all_fav_units_count = fav_units.count()
        if all_fav_units_count <= 0:
            raise ValueError('لا يوجد وحدات مفضلة')
        if all_fav_units_count > page_size*(page_number-1):
            fav_units = fav_units[page_size*(page_number-1):page_size*page_number]
        else:
            fav_units = fav_units[page_size*int(all_fav_units_count/page_size) if all_fav_units_count%page_size!=0 else int(all_fav_units_count/page_size)-1:]
            page_number = int(all_fav_units_count/page_size) if all_fav_units_count%page_size == 0 else int(all_fav_units_count/page_size)+1
        serialized_units = serializers.UnitFavoriteSerializer(fav_units, many=True)
        result.data = {
            "all": serialized_units.data,
            "pagination": {
                "total_items": all_fav_units_count,
                "total_pages": all_fav_units_count/int(all_fav_units_count/page_size) if all_fav_units_count%page_size == 0 else int(all_fav_units_count/page_size)+1,
                "current_page": page_number,
                "has_next": True if all_fav_units_count > page_size*page_number else False,
                "has_previous": True if page_number > 1 else False
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
        models.UnitFavorite.objects.get(is_deleted=False, id=favorite_id).delete()
        result.is_success = True
        result.msg = "تم إزالة الوحدة من المفضلة بنجاح"
    except models.UnitFavorite.DoesNotExist as e:
        result.msg = 'لم يتم العثور على الوحدة المطلوبة'
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء إزالة الوحدة من المفضلة'
        result.data = {'error': str(e)}
    finally:
        return result

# def add_draw_result_service(request_data, request_headers):
#     result = ResultView()
#     try:
#         token = request_headers.get('Authorization', '')
#         token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
#         request_data['created_by_id'] = str(token_decode_result.get('user_id'))
#         if 'Admin' not in token_decode_result.get('roles'):
#             result.msg = 'Unauthorized user, only admins can access'
#         else:
#             serialized_draw_result = serializers.DrawResultSerializer(data=request_data)
#             if serialized_draw_result.is_valid():
#                 serialized_draw_result.save()
#                 result.data = serialized_draw_result.data
#                 result.is_success = True
#                 result.msg = "Request saved successfully"
#             else:
#                 result.msg = "Error occured while serializing data"
#                 result.data = serialized_draw_result.errors
#     except Exception as e:
#         result.msg = 'Unexpected error happened while fetching data'
#         result.data = {'error': str(e)}
#     finally:
#         return result

