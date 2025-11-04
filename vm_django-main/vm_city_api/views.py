import json

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import os, sys
from django.db import transaction
from django.utils.dateparse import parse_datetime, parse_date, parse_time
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
# from vm_city.models import Issue
# from vm_city.models import RootCause, IssuePart, Parts, Vendor


from vm_city.models import Issue, RootCause, IssuePart, Parts, Vendor
from django.http import JsonResponse
from .serializers import IssueSerializer
from django.utils.decorators import method_decorator



class IssueCreateAPIView(APIView):
    print('sagar')
    def post(self, request):
        print(request.data)
        serializer = IssueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Issue created sucessfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class SyncIssuePartsView(APIView):
    def post(self, request, *args, **kwargs):
        print("yaaa")
        print(request.body)  # raw bytes
        print(request.body.decode('utf-8'))  # string
        try:
            data = json.loads(request.body.decode('utf-8'))
            print(request.body)  # raw bytes
            print(request.body.decode('utf-8'))  # string
            firebase_id = data.get('firebase_id')
            parts_data = data.get('parts', [])
            if not firebase_id or not isinstance(parts_data,list):
                return JsonResponse({"error": "invalid payload"}, status=400)

            try:
                issue = Issue.objects.get(firebase_id=firebase_id)
            except Issue.DoesNotExist:
                return JsonResponse({"error":f"issue with firebase_id dont exist {firebase_id}"})

            for part in parts_data:
                part_id = part.get("part_id")
                if not part_id:
                    continue
                try:
                    part_obj = Parts.objects.get(id=part_id)
                except Parts.DoesNotExist:
                    continue  # Skip if part doesn't exist

                IssuePart.objects.create(
                    issue=issue,
                    part=part_obj,
                    stock=part.get("stock"),
                    qty=part.get("qty", 1),
                    price=part.get("price", 0),
                    amount=part.get("amount", 0),
                    purchase_id=part.get("purchase_id")
                )

                return JsonResponse({"message": "Parts synced successfully"}, status=201)
        except json.JSONDecodeError:
            print(request.body)  # raw bytes
            print(request.body.decode('utf-8'))  # string
            return JsonResponse({"error": "Invalid JSON"}, status=400)

