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
        result.msg = 'Unexpected error happened while filtering'
        result.data = {'error': str(e)}
    finally:
        return result

def client_property_reviews_service():
    result = ResultView()
    try:
        top_reviews = models.PropertyClientReview.objects.filter(is_deleted=False, rate__gte=4)[:15]
        serialized_reviews = serializers.ReviewSerializer(top_reviews, many=True)
        result.data = serialized_reviews.data
        result.is_success = True
        result.msg = "Success"
    except Exception as e:
        result.msg = 'Unexpected error happened while fetching data'
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
        result.msg = 'Unexpected error happened while fetching data'
        result.data = {'error': str(e)}
    finally:
        return result

def home_consultations_service():
    result = ResultView()
    try:
        consults = models.Consultation.objects.filter(is_deleted=False)
        serialized_consults = serializers.ConsultationSerializer(consults, many=True)
        result.data = serialized_consults.data
        result.is_success = True
        result.msg = "Success"
    except Exception as e:
        result.msg = 'Unexpected error happened while fetching data'
        result.data = {'error': str(e)}
    finally:
        return result

def draw_results_service():
    result = ResultView()
    try:
        today = timezone.now().date()
        draw_results = models.DrawResult.objects.filter(is_deleted=False, created_at__date=today)
        serialized_draw_results = serializers.DrawResultSerializer(draw_results, many=True)
        result.data = serialized_draw_results.data
        result.is_success = True
        result.msg = "Success"
    except Exception as e:
        result.msg = 'Unexpected error happened while fetching data'
        result.data = {'error': str(e)}
    finally:
        return result


def add_draw_result_service(request_data, request_headers):
    result = ResultView()
    try:
        token = request_headers.get('Authorization', '')
        token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
        request_data['created_by_id'] = str(token_decode_result.get('user_id'))
        if 'Admin' not in token_decode_result.get('roles'):
            result.msg = 'Unauthorized user, only admins can access'
        else:
            serialized_draw_result = serializers.DrawResultSerializer(data=request_data)
            if serialized_draw_result.is_valid():
                serialized_draw_result.save()
                result.data = serialized_draw_result.data
                result.is_success = True
                result.msg = "Request saved successfully"
            else:
                result.msg = "Error occured while serializing data"
                result.data = serialized_draw_result.errors
    except Exception as e:
        result.msg = 'Unexpected error happened while fetching data'
        result.data = {'error': str(e)}
    finally:
        return result

