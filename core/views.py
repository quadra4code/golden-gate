from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from core import services

# Create your views here.

@api_view(["GET"])
def createjson(request):
    # import json

    # fullpath = r"C:\Users\mahmo\Documents\GitHub\GoldenGate-RoyalEstate\core\day16.json"
    # # Load the existing JSON file
    # with open(fullpath, "r", encoding="utf-8") as file:
    #     data = json.load(file)

    # # Add the new field "search_name" for each object
    # for idx, obj in enumerate(data):
    #     obj["pk"] = 3594 + idx
    #     # obj["fields"]["search_name"] = obj["fields"]["winner_name"].replace(' ', '').replace('ة', 'ه').replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ؤ', 'و').replace('ئ', 'ي').replace('ى', 'ي').replace('ء', 'ا')

    # # Save the updated JSON file
    # with open(fullpath, "w", encoding="utf-8") as file:
    #     json.dump(data, file, ensure_ascii=False, indent=4)
    
    # # absolute_path = os.path.abspath(filepath)

    # print("Updated day26.json with search_name field.")
    # return Response()
    import pandas as pd
    import json
    import os
    filename = 'day26'
    # Define the path to the Excel file
    json_data = []
    files = ['day8', 'day9', 'day10', 'day11']
    # for name in files:
    excel_file_path = os.path.join(os.path.dirname(__file__), f'{filename}.xlsx')
    # Read the Excel file
    df = pd.read_excel(excel_file_path)
    # Initialize an empty list to store the JSON data
    # Loop through the DataFrame and convert each row to the desired JSON format
    dict_names = {
        'day89': 0,
        # 'anas': 369,
        'day10': 1743,
        'day11': 2720,
        'day16': 3593,
        # 'day16': 1923,
        # 'day9': 3573,
        'day17': 5133,
        'day18': 6523,
        'day19': 7830,
        'day20': 9095,
        'day23': 11033,
        'day24': 12314,
        'day25': 12624,
        'day26': 13033,
        'coming': 14156,
    }
    pk = dict_names[filename]
    for index, row in df.iterrows():
        if row.values[0] == 'المساحة':
            continue
        pk += 1
        prop = 0 if str(row.values[1]) == 'nan' else row.values[1]
        record = {
            "model": "core.DrawResult",
            "pk": pk,
            "fields": {
                "winner_name": row.values[6],
                "search_name": row.values[6].replace(' ', '').replace('ة', 'ه').replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ؤ', 'و').replace('ئ', 'ي').replace('ى', 'ي').replace('ء', 'ا'),
                "property_number": prop,
                "building_or_region": row.values[3] if type(row.values[3]) is str else 0 if str(row.values[3]) == 'nan' else int(row.values[3]),
                "floor": "" if type(row.values[2]) is float else row.values[2],
                "area": 0 if str(row.values[0]) == 'nan' else row.values[0],
                "project_name": row.values[5]
            }
        }
        print(record['pk'])
        json_data.append(record)
    # Convert the list to a JSON string
    json_string = json.dumps(json_data, indent=4, ensure_ascii=False)
    # print(json_string)
    # Define the path to the output JSON file
    json_file_path = os.path.join(os.path.dirname(__file__), f'{filename}.json')
    # Write the JSON string to the output file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json_string)
    print(f"Data has been successfully converted to JSON and saved to {json_file_path}")
    return Response({'message': 'Hello, World!'})

# region Units
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def propose_unit_view(request):
    propose_result = services.propose_unit_service(request.data, request.user.id if request.user else None)
    status_code = (
        status.HTTP_201_CREATED if propose_result.is_success
        else status.HTTP_401_UNAUTHORIZED if propose_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(propose_result.to_dict(), status=status_code)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_unit_view(request):
    request_result = services.request_unit_service(request.data, request.headers)
    status_code = (
        status.HTTP_201_CREATED if request_result.is_success
        else status.HTTP_401_UNAUTHORIZED if request_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(request_result.to_dict(), status=status_code)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def paginated_client_requests_view(request):
    requests_result = services.paginated_client_requests_service(request.data, request.user.id)
    status_code = (
        status.HTTP_200_OK if requests_result.is_success
        else status.HTTP_401_UNAUTHORIZED if requests_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(requests_result.to_dict(), status=status_code)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cancel_request_view(request, request_id):
    cancel_request_result = services.cancel_request_service(request_id)
    status_code = (
        status.HTTP_200_OK if cancel_request_result.is_success
        else status.HTTP_401_UNAUTHORIZED if cancel_request_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(cancel_request_result.to_dict(), status=status_code)

@api_view(["GET"])
def proposal_form_data_view(request):
    form_data_result = services.proposal_form_data_service()
    status_code = (
        status.HTTP_200_OK if form_data_result.is_success
        else status.HTTP_401_UNAUTHORIZED if form_data_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(form_data_result.to_dict(), status=status_code)

@api_view(["GET"])
def recent_units_view(request):
    recent_units_result = services.recent_units_service()
    status_code = (
        status.HTTP_200_OK if recent_units_result.is_success
        else status.HTTP_401_UNAUTHORIZED if recent_units_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(recent_units_result.to_dict(), status=status_code)

@api_view(["POST"])
def filter_paginated_units_view(request):
    filter_paginated_units_result = services.filter_paginated_units_service(request.data)
    status_code = (
        status.HTTP_201_CREATED if filter_paginated_units_result.is_success
        else status.HTTP_401_UNAUTHORIZED if filter_paginated_units_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(filter_paginated_units_result.to_dict(), status=status_code)

@api_view(["GET"])
def unit_details_view(request, unit_id):
    unit_details_result = services.unit_details_service(unit_id)
    status_code = (
        status.HTTP_200_OK if unit_details_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(unit_details_result.to_dict(), status=status_code)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def paginated_client_units_view(request):
    print(request.user)
    paginated_client_units_result = services.paginated_client_units_service(request.data, request.user.id if request.user else None)
    status_code = (
        status.HTTP_200_OK if paginated_client_units_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(paginated_client_units_result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_update_unit_view(request, unit_id):
    result = services.get_update_unit_service(unit_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_unit_view(request):
    result = services.update_unit_service(request.data, request.user.id if request.user else None)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def hard_delete_unit_view(request, unit_id):
    result = services.hard_delete_unit_service(unit_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region Home
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
def home_consultation_types_view(request):
    consultation_types_result = services.home_consultation_types_service()
    status_code = (
        status.HTTP_200_OK if consultation_types_result.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(consultation_types_result.to_dict(), status=status_code)

@api_view(["GET"])
def consultations_by_type_view(request, consult_type_id):
    consultations_result = services.consultations_by_type_service(consult_type_id)
    status_code = (
        status.HTTP_200_OK if consultations_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(consultations_result.to_dict(), status=status_code)

@api_view(["GET"])
def home_featured_units_view(request):
    featured_units_result = services.home_featured_units_service()
    status_code = (
        status.HTTP_200_OK if featured_units_result.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(featured_units_result.to_dict(), status=status_code)

@api_view(["GET"])
def home_most_viewed_units_view(request):
    most_viewed_units_result = services.home_most_viewed_units_service()
    status_code = (
        status.HTTP_200_OK if most_viewed_units_result.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(most_viewed_units_result.to_dict(), status=status_code)
# endregion

# region Reviews
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
# endregion

# region Draw Results
@api_view(["POST"])
def draw_results_view(request):
    draw_results = services.draw_results_service(request.data)
    status_code = (
        status.HTTP_200_OK if draw_results.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(draw_results.to_dict(), status=status_code)
# endregion

# region Contact Us
@api_view(["POST"])
def add_contact_us_msg_view(request):
    send_result = services.add_contact_us_msg_service(request.data)
    status_code = (
        status.HTTP_201_CREATED if send_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(send_result.to_dict(), status=status_code)
# endregion

# region Favorites
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_favorite_view(request):
    add_favorite_result = services.add_favorite_service(request.data, request.headers)
    status_code = (
        status.HTTP_201_CREATED if add_favorite_result.is_success
        else status.HTTP_401_UNAUTHORIZED if add_favorite_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(add_favorite_result.to_dict(), status=status_code)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def list_paginated_favorites_view(request):
    list_favorites_result = services.list_favorites_service(request.data, request.headers)
    status_code = (
        status.HTTP_200_OK if list_favorites_result.is_success
        else status.HTTP_401_UNAUTHORIZED if list_favorites_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(list_favorites_result.to_dict(), status=status_code)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_favorite_view(request, favorite_id):
    delete_favorite_result = services.delete_favorite_service(favorite_id)
    status_code = (
        status.HTTP_200_OK if delete_favorite_result.is_success
        else status.HTTP_401_UNAUTHORIZED if delete_favorite_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(delete_favorite_result.to_dict(), status=status_code)
# endregion



