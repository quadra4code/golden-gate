from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from core import services

# Create your views here.

@api_view(["GET"])
def createjson(request):

    import pandas as pd
    import json
    import os

    # Define the path to the Excel file
    excel_file_path = os.path.join(os.path.dirname(__file__), 'day11.xlsx')

    # Read the Excel file
    df = pd.read_excel(excel_file_path)

    # Initialize an empty list to store the JSON data
    json_data = []

    # Loop through the DataFrame and convert each row to the desired JSON format
    for index, row in df.iterrows():
        # print(row.values[0])
        # print('0 => ', row.values[0])
        # print('1 => ', row.values[1])
        # print('2 => ', str(row.values[1]), type(row.values[2]))
        # if str(row.values[1]) == 'nan':
        #     print("yes truthy")
        # print('3 => ', row.values[3])
        # print('4 => ', row.values[4])
        # print('5 => ', row.values[5])
        # print('6 => ', row.values[6])
        print(row.values[1])
        prop = 0 if str(row.values[1]) == 'nan' else row.values[1]
        record = {
            "model": "core.DrawResult",
            "pk": index + 1 + 1923,
            "fields": {
                "winner_name": row.values[6],
                "property_number": prop,
                "building_or_region": row.values[3] if type(row.values[3]) is str else 0 if str(row.values[3]) == 'nan' else int(row.values[3]),
                "floor": "" if type(row.values[2]) is float else row.values[2],
                "area": 0 if str(row.values[0]) == 'nan' else row.values[0],
                "project_name": row.values[5]
            }
        }
        json_data.append(record)

    # Convert the list to a JSON string
    json_string = json.dumps(json_data, indent=4, ensure_ascii=False)
    print(json_string)

    # Define the path to the output JSON file
    json_file_path = os.path.join(os.path.dirname(__file__), 'day11.json')

    # Write the JSON string to the output file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json_string)

    print(f"Data has been successfully converted to JSON and saved to {json_file_path}")
    return Response({'message': 'Hello, World!'})
'''
input 
{
    "project_type_id": "1",
    "project_id": "2",
    "city_id": "7",
    "description": "thsislfj aljiaj;lf iaj fj;alej jwe jl",
    "area": "400",
    "payment_method": "IN",
    "installment_period": "5",
    "first_installment_value": "25000",
    "phone_number": "01118069749"
}
output
{
    "is_success":true,
    "data":{
        "pcp_id":26,
        "description":"thsislfj aljiaj;lf iaj fj;alej jwe jl",
        "area":400,
        "payment_method":"IN",
        "installment_period":5,
        "first_installment_value":"25000.0000",
        "phone_number":"01118069749",
        "created_by_id":1
    },
    "msg":"Request saved successfully"
}
'''
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def propose_unit_view(request):
    propose_result = services.propose_unit_service(request.data, request.headers)
    status_code = (
        status.HTTP_201_CREATED if propose_result.is_success
        else status.HTTP_401_UNAUTHORIZED if propose_result.msg.__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(propose_result.to_dict(), status=status_code)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_unit_view(request):
    request_result = services.request_unit_service(request.data, request.headers)
    status_code = (
        status.HTTP_201_CREATED if request_result.is_success
        else status.HTTP_401_UNAUTHORIZED if request_result.msg.__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(request_result.to_dict(), status=status_code)

@api_view(["GET"])
def proposal_form_data_view(request):
    form_data_result = services.proposal_form_data_service()
    status_code = (
        status.HTTP_200_OK if form_data_result.is_success
        else status.HTTP_401_UNAUTHORIZED if form_data_result.msg.__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(form_data_result.to_dict(), status=status_code)

@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def all_units_view(request):
    all_units_result = services.all_units_service()
    status_code = (
        status.HTTP_200_OK if all_units_result.is_success
        else status.HTTP_401_UNAUTHORIZED if all_units_result.msg.__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(all_units_result.to_dict(), status=status_code)

@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def filter_properties_view(request):
    filter_units_result = services.filter_properties_service(request.data)
    status_code = (
        status.HTTP_201_CREATED if filter_units_result.is_success
        else status.HTTP_401_UNAUTHORIZED if filter_units_result.msg.__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(filter_units_result.to_dict(), status=status_code)

@api_view(["GET"])
def home_top_reviews_view(request):
    reviews_result = services.home_reviews_service()
    status_code = (
        status.HTTP_200_OK if reviews_result.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(reviews_result.to_dict(), status=status_code)

@api_view(["GET"])
def home_articles_view(request):
    articles_result = services.home_articles_service()
    status_code = (
        status.HTTP_200_OK if articles_result.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(articles_result.to_dict(), status=status_code)

@api_view(["GET"])
def home_consultations_view(request):
    consultations_result = services.home_consultations_service()
    status_code = (
        status.HTTP_200_OK if consultations_result.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(consultations_result.to_dict(), status=status_code)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_review_view(request):
    send_result = services.add_review_service(request.data, request.headers)
    status_code = (
        status.HTTP_201_CREATED if send_result.is_success
        else status.HTTP_401_UNAUTHORIZED if send_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(send_result.to_dict(), status=status_code)

@api_view(["POST"])
def draw_results_view(request):
    draw_results = services.draw_results_service(request.data)
    status_code = (
        status.HTTP_200_OK if draw_results.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(draw_results.to_dict(), status=status_code)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_draw_result_view(request):
    send_result = services.add_draw_result_service(request.data, request.headers)
    status_code = (
        status.HTTP_200_OK if send_result.is_success
        else status.HTTP_401_UNAUTHORIZED if send_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(send_result.to_dict(), status=status_code)
