from datetime import timedelta
from django.utils import timezone
from core import models
from core import serializers
from core.base_models import ResultView
from users.utils import extract_payload_from_jwt
# Create your services here.

def propose_property_service(request_data, request_headers):
    result = ResultView()
    try:
        token = request_headers.get('Authorization', '')
        token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
        request_data['created_by_id'] = str(token_decode_result.get('user_id'))
        serialized_property = serializers.PropertySerializer(data=request_data)
        if serialized_property.is_valid():
            serialized_property.save()
            result.msg = 'Request saved successfully'
            result.is_success = True
            result.data = serialized_property.data
        else:
            result.msg = 'Error happened while serializing data'
            result.data = serialized_property.errors
    except Exception as e:
        result.msg = 'Unexpected error happened while saving request'
        result.data = {'error': str(e)}
    finally:
        return result

# def propose_property_service(request_data, request_headers):
#     result = ResultView()
#     try:
#         token = request_headers.get('Authorization', '')
#         token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
#         request_data['created_by_id'] = str(token_decode_result.get('user_id'))
#         serialized_property = None
#         if request_data.get('project_type_id') == "1":
#             serialized_property = serializers.LandSerializer(data=request_data)
#         elif request_data.get('project_type_id') == "2":
#             serialized_property = serializers.UnitSerializer(data=request_data)
#         else:
#             raise LookupError("Invalid Project Type")
#         if serialized_property.is_valid():
#             serialized_property.save()
#             result.msg = 'Request saved successfully'
#             result.is_success = True
#             result.data = serialized_property.data
#         else:
#             result.msg = 'Error happened while serializing data'
#             result.data = serialized_property.errors
#     except Exception as e:
#         result.msg = 'Unexpected error happened while saving request'
#         result.data = {'error': str(e)}
#     finally:
#         return result

def request_property_service(request_data, request_headers):
    result = ResultView()
    try:
        token = request_headers.get('Authorization', '')
        token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
        request_data['created_by_id'] = str(token_decode_result.get('user_id'))
        serialized_land_request = serializers.PropertyRequestSerializer(data=request_data)
        if serialized_land_request.is_valid():
            serialized_land_request.save()
            result.msg = 'Request saved successfully'
            result.is_success = True
            result.data = serialized_land_request.data
        else:
            result.msg = 'Error happened while serializing data'
            result.data = serialized_land_request.errors
    except Exception as e:
        result.msg = 'Unexpected error happened while saving request'
        result.data = {'error': str(e)}
    finally:
        return result

def proposal_form_data_service():
    result = ResultView()
    try:
        cities = models.City.objects.filter(is_deleted=False).values('id', 'name').order_by('id')
        project_types = models.ProjectType.objects.filter(is_deleted=False).values('id', 'name').order_by('id')
        pcps = models.PCP.objects.filter(is_deleted=False).select_related('project_type', 'project', 'city').distinct('project_type', 'project')
        data = {
            "cities": list(cities),
            "project_types": [],
            "floors": [{"id": choice[0], "name": choice[1]} for choice in models.Property.FLOOR_CHOICES]
        }
        for project_type in project_types:
            project_type_data = {
                "id": project_type['id'],
                "name": project_type['name'],
                "projects": []
            }
            for pcp in pcps.filter(project_type_id=project_type['id']):
                project_data = {
                    "id": pcp.project.id,
                    "name": pcp.project.name
                }
                project_type_data["projects"].append(project_data)
            data["project_types"].append(project_type_data)
        result.data = data
        result.is_success = True
        result.msg = 'Success'
    except Exception as e:
        result.msg = 'Unexpected error happened while saving request'
        result.data = {'error': str(e)}
    finally:
        return result

def all_properties_service():
    result = ResultView()
    try:
        now = timezone.now()
        twenty_four_hours_ago = now - timedelta(hours=24)
        for_sale_status = models.Status.objects.get(code=1)
        properties = models.Property.objects.filter(is_deleted=False, status=for_sale_status)
        props_data = {
            "recent": [],
            "all": []
        }
        def add_properties(properties):
            for prop in properties:
                is_recent = prop.created_at >= twenty_four_hours_ago if hasattr(prop, 'created_at') else False
                rate_list = [''] * prop.rate if prop.rate else []
                property_data = {
                    "id": prop.id,
                    "title": prop.title,
                    "description": prop.description,
                    "city": prop.pcp.city.name,
                    "payment_method": prop.get_payment_method_display(),
                    "project_type": prop.pcp.project_type.name,
                    "project": prop.pcp.project.name,
                    "rate": rate_list,
                    "area": prop.area,
                    "floor": prop.get_floor_display(),
                    "price": prop.price
                }
                if is_recent:
                    props_data["recent"].append(property_data)
                props_data["all"].append(property_data)
        add_properties(properties)
        result.data = props_data
        result.is_success = True
        result.msg = 'Success'
    except Exception as e:
        result.msg = 'Unexpected error happened while saving request'
        result.data = {'error': str(e)}
    finally:
        return result

# def all_properties_service():
#     result = ResultView()
#     try:
#         now = timezone.now()
#         twenty_four_hours_ago = now - timedelta(hours=24)
#         for_sale_status = models.Status.objects.get(code=1)
#         lands = models.Land.objects.filter(is_deleted=False, status=for_sale_status)
#         units = models.Unit.objects.filter(is_deleted=False, status=for_sale_status)
#         props_data = {
#             "recent": [],
#             "all": []
#         }
#         def add_properties(properties):
#             for prop in properties:
#                 is_recent = prop.created_at >= twenty_four_hours_ago if hasattr(prop, 'created_at') else False
#                 payment_method = prop.get_payment_method_display()
#                 rate_list = [''] * prop.rate if prop.rate else []
#                 property_data = {
#                     "id": prop.id,
#                     "title": prop.title,
#                     "description": prop.description,
#                     "city": prop.pcp.city.name,
#                     "payment_method": payment_method,
#                     "project": prop.pcp.project.name,
#                     "rate": rate_list,
#                     "area": prop.area,
#                     "price": prop.price
#                 }
#                 if is_recent:
#                     props_data["recent"].append(property_data)
#                 props_data["all"].append(property_data)
#         add_properties(lands)
#         add_properties(units)
#         result.data = props_data
#         result.is_success = True
#         result.msg = 'Success'
#     except Exception as e:
#         result.msg = 'Unexpected error happened while saving request'
#         result.data = {'error': str(e)}
#     finally:
#         return result

def filter_properties_service(request_data):
    result = ResultView()
    try:
        project_id = request_data.get('project_id')
        project_type_id = request_data.get('project_type_id')
        city_id = request_data.get('city_id')
        min_price = request_data.get('min_price')
        max_price = request_data.get('max_price')
        payment_method = request_data.get('payment_method')
        if min_price is not None:
            try:
                min_price = float(min_price)
            except (TypeError, ValueError):
                raise ValueError("min_price must be a valid number")
        if max_price is not None:
            try:
                max_price = float(max_price)
            except (TypeError, ValueError):
                raise ValueError("max_price must be a valid number")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValueError("min_price cannot be greater than max_price")
        for_sale_status = models.Status.objects.get(code=1)
        properties = models.Property.objects.filter(is_deleted=False, status=for_sale_status)
        if project_id:
            properties = properties.filter(pcp__project__id=project_id)
        if project_type_id:
            properties = properties.filter(pcp__project__project_type__id=project_type_id)
        if city_id:
            properties = properties.filter(pcp__city__id=city_id)
        if min_price and max_price:
            properties = properties.filter(price__gte=min_price, price__lte=max_price)
        if payment_method:
            properties = properties.filter(payment_method=payment_method)
        props_data = []
        def add_properties(properties):
            for prop in properties:
                rate_list = [''] * prop.rate if prop.rate else []
                props_data.append({
                    "id": prop.id,
                    "title": prop.title,
                    "description": prop.description,
                    "city": prop.pcp.city.name,
                    "payment_method": prop.get_payment_method_display(),
                    "project": prop.pcp.project.name,
                    "rate": rate_list,
                    "area": prop.area,
                    "floor": prop.get_floor_display(),
                    "price": prop.price
                })
        add_properties(properties)
        result.data = props_data
        result.is_success = True
        result.msg = 'Success'
    except Exception as e:
        result.msg = 'Unexpected error happened while saving request'
        result.data = {'error': str(e)}
    finally:
        return result

# def filter_properties_service(request_data):
#     result = ResultView()
#     try:
#         project_id = request_data.get('project_id')
#         project_type_id = request_data.get('project_type_id')
#         city_id = request_data.get('city_id')
#         min_price = request_data.get('min_price')
#         max_price = request_data.get('max_price')
#         payment_method = request_data.get('payment_method')
#         if min_price is not None:
#             try:
#                 min_price = float(min_price)
#             except (TypeError, ValueError):
#                 raise ValueError("min_price must be a valid number")
#         if max_price is not None:
#             try:
#                 max_price = float(max_price)
#             except (TypeError, ValueError):
#                 raise ValueError("max_price must be a valid number")
#         if min_price is not None and max_price is not None and min_price > max_price:
#             raise ValueError("min_price cannot be greater than max_price")
#         for_sale_status = models.Status.objects.get(code=1)
#         lands = models.Land.objects.filter(is_deleted=False, status=for_sale_status)
#         units = models.Unit.objects.filter(is_deleted=False, status=for_sale_status)
#         if project_id:
#             lands = lands.filter(pcp__project__id=project_id)
#             units = units.filter(pcp__project__id=project_id)
#         if project_type_id:
#             lands = lands.filter(pcp__project__project_type__id=project_type_id)
#             units = units.filter(pcp__project__project_type__id=project_type_id)
#         if city_id:
#             lands = lands.filter(pcp__city__id=city_id)
#             units = units.filter(pcp__city__id=city_id)
#         if min_price and max_price:
#             lands = lands.filter(price__gte=min_price, price__lte=max_price)
#             units = units.filter(price__gte=min_price, price__lte=max_price)
#         if payment_method:
#             lands = lands.filter(payment_method=payment_method)
#             units = units.filter(payment_method=payment_method)
#         props_data = []
#         def add_properties(properties):
#             for prop in properties:
#                 payment_method = prop.get_payment_method_display()
#                 rate_list = [''] * prop.rate if prop.rate else []
#                 props_data.append({
#                     "id": prop.id,
#                     "title": prop.title,
#                     "description": prop.description,
#                     "city": prop.pcp.city.name,
#                     "payment_method": payment_method,
#                     "project": prop.pcp.project.name,
#                     "rate": rate_list,
#                     "area": prop.area,
#                     "price": prop.price
#                 })
#         add_properties(lands)
#         add_properties(units)
#         result.data = props_data
#         result.is_success = True
#         result.msg = 'Success'
#     except Exception as e:
#         result.msg = 'Unexpected error happened while saving request'
#         result.data = {'error': str(e)}
#     finally:
#         return result
