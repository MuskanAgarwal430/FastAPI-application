# vm_city/views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import os
import traceback
from django.db import transaction
from django.utils.dateparse import parse_datetime, parse_date, parse_time
from decimal import Decimal, InvalidOperation
from django.utils import timezone # Import timezone for handling aware datetimes
from django.views.decorators.csrf import csrf_exempt
from .models import Issue # Only import Issue, as Vehicle is no longer directly linked by Issue
from .models import RootCause, IssuePart, Parts, Vendor, Vehicle, City, CityTransferHistory
from django.http import JsonResponse

# --- Firebase Initialization ---
# Ensure your 'vehicle_data/vehicle_cred1.json' path is correct
# relative to your Django project's base directory.
try:
    cred = credentials.Certificate("vm_city/vehicle_cred1.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://wevois-qa-vm-default-rtdb.firebaseio.com/', # Set base URL here
            'storageBucket': 'gs://wevois-qa-vm.appspot.com'
        })
    print("Firebase app initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    # You might want to handle this error more robustly in a production environment
    # e.g., by logging it and preventing the app from starting if critical.

# --- Class-Based View for Syncing Firebase Issues ---
class FirebaseIssueSyncView(APIView):
    """
    APIView to fetch vehicle issue data from Firebase Realtime Database
    and synchronize it with the Django database (Issue model).
    """

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to trigger the Firebase data synchronization.
        """
        if not firebase_admin._apps:
            return Response(
                {"status": "error", "message": "Firebase app is not initialized."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        synced_issues_count = 0
        created_issues_count = 0
        updated_issues_count = 0
        errors = []

        try:
            # Reference to the specific path where issues are stored in Firebase
            # and the full path is '/CompaniesData/wevois/VehicleIssues/Issues'
            ref = db.reference('/CompaniesData/wevois/VehicleIssues/Issues')
            firebase_data = ref.get()

            if not firebase_data:
                return Response(
                    {"status": "success", "message": "No data found in Firebase for synchronization."},
                    status=status.HTTP_200_OK
                )

            # Use a database transaction to ensure atomicity
            # If any record fails, the entire transaction can be rolled back
            with transaction.atomic():
                # Firebase Realtime DB returns data as a dictionary where keys are Firebase IDs
                for firebase_id, issue_data in firebase_data.items():
                    try:
                        # Get vehicle_no directly, as it's now a CharField on Issue model
                        vehicle = issue_data.get('vehicle')


                        # Prepare issue data for saving/updating
                        # Parse date/time fields safely. Use .get() for optional fields.
                        resolved_date_str = issue_data.get('resolvedDate')
                        confirm_date_str = issue_data.get('confirmDate')
                        created_time_str = issue_data.get('createdTime')
                        creation_date_str = issue_data.get('creationDate')
                        date_field_str = issue_data.get('date')
                        working_hrs_str = issue_data.get('workingHrs')

                        # --- Timezone-aware parsing for DateTimeFields ---
                        resolved_date = None
                        if resolved_date_str:
                            naive_datetime = parse_datetime(resolved_date_str)
                            if naive_datetime and timezone.is_naive(naive_datetime):
                                resolved_date = timezone.make_aware(naive_datetime)
                            else:
                                resolved_date = naive_datetime

                        confirm_date = None
                        if confirm_date_str:
                            naive_datetime = parse_datetime(confirm_date_str)
                            if naive_datetime and timezone.is_naive(naive_datetime):
                                confirm_date = timezone.make_aware(naive_datetime)
                            else:
                                confirm_date = naive_datetime

                        created_time = parse_time(created_time_str) if created_time_str else None
                        creation_date = parse_date(creation_date_str) if creation_date_str else None
                        date_field = parse_date(date_field_str) if date_field_str else None

                        # --- Parse workingHrs from "H:M" string to Decimal ---
                        parsed_working_hrs = None
                        if working_hrs_str is not None:
                            working_hrs_str = str(working_hrs_str).strip() # Ensure it's a string and strip whitespace
                            if working_hrs_str: # Only proceed if not an empty string after stripping
                                try:
                                    if ':' in working_hrs_str:
                                        hours, minutes = map(int, working_hrs_str.split(':'))
                                        parsed_working_hrs = Decimal(f"{hours + (minutes / 60.0):.2f}") # Format to 2 decimal places for precision
                                    else:
                                        # If it's already a number or a simple string that can be cast
                                        parsed_working_hrs = Decimal(working_hrs_str)
                                except InvalidOperation: # Catch specific Decimal conversion error
                                    print(f"Warning: Decimal ConversionSyntax error for workingHrs '{working_hrs_str}' for Firebase issue ID '{firebase_id}'. Setting to None.")
                                    parsed_working_hrs = None
                                except (ValueError, TypeError) as e:
                                    print(f"Warning: Could not parse workingHrs '{working_hrs_str}' for Firebase issue ID '{firebase_id}'. Error: {e}. Setting to None.")
                                    parsed_working_hrs = None
                        # --- End workingHrs parsing ---

                        # --- Parse repairCost to Decimal ---
                        repair_cost_str = issue_data.get('repairCost')
                        parsed_repair_cost = None
                        if repair_cost_str is not None:
                            repair_cost_str = str(repair_cost_str).strip()
                            if repair_cost_str:
                                try:
                                    parsed_repair_cost = Decimal(repair_cost_str)
                                except InvalidOperation: # Catch specific Decimal conversion error
                                    print(f"Warning: Decimal ConversionSyntax error for repairCost '{repair_cost_str}' for Firebase issue ID '{firebase_id}'. Setting to None.")
                                    parsed_repair_cost = None
                                except (ValueError, TypeError) as e:
                                    print(f"Warning: Could not parse repairCost '{repair_cost_str}' for Firebase issue ID '{firebase_id}'. Error: {e}. Setting to None.")
                                    parsed_repair_cost = None
                        # --- End repairCost parsing ---


                        # Use update_or_create to handle new or existing issues
                        issue_instance, created = Issue.objects.update_or_create(
                            firebase_id=firebase_id, # Use the unique Firebase ID for lookup
                            defaults={
                                'canRunInWard': issue_data.get('canRunInWard', ''),
                                'canRunInWardResolved': issue_data.get('canRunInWardResolved', ''),
                                'city': issue_data.get('city', ''),
                                'confirmBy': issue_data.get('confirmBy'),
                                'confirmDate': confirm_date,
                                'createdBy': issue_data.get('createdBy'),
                                'createdTime': created_time,
                                'creationDate': creation_date,
                                'date': date_field,
                                'description': issue_data.get('description'),
                                'driverId': issue_data.get('driverId', ''),
                                'driverName': issue_data.get('driverName', ''),
                                'isBillAvailable': issue_data.get('isBillAvailable', ''), # Now handling as CharField
                                'jobCardId': issue_data.get('jobCardId'),
                                'mechanicName': issue_data.get('mechanicName', ''),
                                'reopenKey': issue_data.get('reopenKey'),
                                'repairCost': parsed_repair_cost, # Use the parsed Decimal value
                                'resolvedDate': resolved_date, # Use the parsed timezone-aware datetime
                                'resolvedDescription': issue_data.get('resolvedDescription'),
                                'rootCauses': issue_data.get('rootCauses'),
                                'status': issue_data.get('status', ''), # Changed default from 'open' to '' for CharField
                                'unpaidBills': issue_data.get('unpaidBills', Decimal('0.00')), # Ensure default is Decimal
                                'updateKey': issue_data.get('updateKey'),
                                'vehicle': vehicle,
                                'vehicleIssue': issue_data.get('vehicleIssue', ''),
                                'workingHrs': parsed_working_hrs, # Use the parsed Decimal value
                                # 'created_at' is auto_now_add, no need to set
                            }
                        )

                        if created:
                            created_issues_count += 1
                            print(f"Created new Issue: {issue_instance.id} (Firebase ID: {firebase_id})")
                        else:
                            updated_issues_count += 1
                            print(f"Updated Issue: {issue_instance.id} (Firebase ID: {firebase_id})")

                        synced_issues_count += 1

                    except Exception as e:
                        error_message = f"Error processing Firebase issue ID '{firebase_id}': {e}"
                        errors.append(error_message)
                        print(error_message)

            return Response({
                "status": "success",
                "message": (f"Synchronization complete. {synced_issues_count} issues processed. "
                            f"{created_issues_count} created, {updated_issues_count} updated."),
                "errors": errors
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Catch any high-level errors during the Firebase fetch or transaction
            return Response(
                {"status": "error", "message": f"An unexpected error occurred: {e}", "errors": errors},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@csrf_exempt
def import_root_causes(request):
    ref = db.reference('/CompaniesData/wevois/RootCauses')  # Adjust the reference path if needed
    data = ref.get()
    print(data)



    created, updated = 0, 0
    for key, item in data.items():
        print(key, item)
        obj, is_created = RootCause.objects.update_or_create(
            firebase_id=key,
            defaults={
                'name': item.get('name', ''),
                'CreatedById': item.get('CreatedById', ''),
            }
        )
        if is_created:
            created += 1
        else:
            updated += 1

    return Response({
        "status": "success",

    }, status=status.HTTP_200_OK)

@csrf_exempt
def fetch_issue_parts_from_firebase(request):
    try:
        ref = db.reference('/CompaniesData/wevois/VehicleIssues/Issues')
        raw_data = ref.get()

        if not raw_data:
            return JsonResponse({'message': 'No IssueParts found.'}, status=404)

        all_data = []

        # Check structure type: dict or list
        if isinstance(raw_data, dict):
            iterable_data = raw_data.items()
        elif isinstance(raw_data, list):
            iterable_data = enumerate(raw_data)
        else:
            return JsonResponse({'error': 'Unexpected Firebase data structure'}, status=500)

        for issue_firebase_id, issue_data in iterable_data:
            if not isinstance(issue_data, dict):
                continue

            parts_data = issue_data.get('parts', {})
            if not isinstance(parts_data, dict):
                continue

            issue_obj = Issue.objects.filter(firebase_id=str(issue_firebase_id)).first()
            if not issue_obj:
                continue

            for part_id, stock_entries in parts_data.items():
                if not isinstance(stock_entries, dict):
                    continue

                for stock_id, details in stock_entries.items():
                    if not isinstance(details, dict):
                        continue

                    try:
                        print(type(part_id))
                        print(part_id, details)
                        amount = float(details.get('amount'))
                        qty = float(details.get('qty', 0))
                        price = float(details.get('price', 0))


                        if not  amount:
                            raise Exception('anomt nit f')

                        part_obj = Parts.objects.filter(part_id=part_id).first()
                        if not part_obj:
                            continue

                        # Create IssuePart entry
                        obj, created = IssuePart.objects.update_or_create(
                            part=part_obj.part_id,
                            defaults={
                                'issue': issue_obj,
                                'stock': stock_id,
                                'qty': qty,
                                'price': price,
                                'amount': amount * qty,
                                'purchase_id': details.get('purchaseId')
                            }
                        )

                        all_data.append(
                            {
                            'issue': issue_firebase_id,
                            'part': part_id,
                            'stock': stock_id,
                            'qty': qty,
                            'price': price,
                            'amount': amount,
                            'purchaseId': details.get('purchaseId'),
                        })

                    except Exception as part_error:
                        print(f"[ERROR] Firebase ID {issue_firebase_id}, Part {part_id}: {part_error}")

        return JsonResponse({'status': 'success', 'data': all_data}, status=200)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def fetch_parts_from_firebase(request):
    try:
        ref = db.reference('/CompaniesData/wevois/Parts')
        raw_data = ref.get()

        if not raw_data:
            return JsonResponse({'message': 'No parts found in Firebase.'}, status=404)

        created = 0
        updated = 0

        for firebase_id, part_data in raw_data.items():
            # Skip if value is not a dict (like "lastKey": 2)
            if not isinstance(part_data, dict):
                continue

            obj, created_flag = Parts.objects.update_or_create(
                part_id=firebase_id,
                defaults={
                    'code': part_data.get('code'),
                    'image': part_data.get('image'),
                    'isReturnRequiredValue': part_data.get('isReturnRequiredValue'),
                    'name': part_data.get('name'),
                    'unit': part_data.get('unit'),
                }
            )
            if created_flag:
                created += 1
            else:
                updated += 1

        return JsonResponse({
            'message': 'Parts import complete.',
            'created': created,
            'updated': updated
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_vendor_data(request):
    try:
        ref = db.reference('/CompaniesData/wevois/Vendors')
        raw_data = ref.get()
        if not raw_data:
            return JsonResponse({'message': 'No parts found in Firebase.'}, status=404)

        created = 0
        updated = 0

        for firebase_id, vendor_data in raw_data.items():
            if not isinstance(vendor_data, dict):
                continue

            obj, created_flag = Vendor.objects.update_or_create(
                firebase_id=firebase_id,
                defaults={
                    'name': vendor_data.get('name'),
                    'contact': vendor_data.get('contact'),
                    'address': vendor_data.get('address'),
                    'city': vendor_data.get('city'),

                    'account_name': vendor_data.get('Accountname'),
                    'account_number': vendor_data.get('Accountnumber'),
                    'bank_name': vendor_data.get('BankName'),
                    'branch_name': vendor_data.get('IfscCode'),
                    'ifsc_code': vendor_data.get('IfscCode'),
                    'upi_id': vendor_data.get('UpiId'),

                }
            )
            if created_flag:
                created += 1
            else:
                updated += 1

        return JsonResponse({
                'message': 'Parts import complete.',
                'created': created,
                'updated': updated
            }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_vehicles_data(request):
    try:
        ref = db.reference('/CompaniesData/wevois/VehicleData/Vehicle')
        raw_data = ref.get()
        if not raw_data:
            return JsonResponse({'message': 'No parts found in Firebase.'}, status=404)

        created = 0
        updated = 0

        for firebase_id, vendor_data in raw_data.items():
            if not isinstance(vendor_data, dict):
                continue

            raw_is_active = vendor_data.get('isActive')

            # normalize the value
            if isinstance(raw_is_active, str):
                raw_is_active = raw_is_active.lower() in ["true", "1", "yes"]

            obj, created_flag = Vehicle.objects.update_or_create(
                vehicle_no=vendor_data.get('vehicleNo'),
                defaults={
                    'is_active': raw_is_active,
                    'currentCity': vendor_data.get('currentCity'),
                }
            )

            if created_flag:
                created += 1
            else:
                updated += 1

        return JsonResponse({
                'message': 'Vehicles import complete.',
                'created': created,
                'updated': updated
            }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_cities_data(request):
    try:
        # 1. Fetch city data
        city_ref = db.reference('/CompaniesData/wevois/CityData/City')
        city_data = city_ref.get() or {}

        # 2. Fetch city incharge data
        incharge_ref = db.reference('/CompaniesData/wevois/CityData/CityIncharge/Citywise')
        incharge_data = incharge_ref.get() or {}

        created = 0
        updated = 0

        # 3. Sync cities into Django DB using 'name' as unique
        for city_key, city_info in city_data.items():
            if not isinstance(city_info, dict):
                continue

            raw_is_active = city_info.get('isActive')

            if isinstance(raw_is_active, str):
                raw_is_active = raw_is_active.lower() in ["true", "1", "yes"]

            city_incharge = incharge_data.get(city_key) or {}

            obj, created_flag = City.objects.update_or_create(
                name=city_info.get("name"),  # unique field
                defaults={
                    "isActive": raw_is_active,
                    "cityIncharge": city_incharge
                }
            )

            if created_flag:
                created += 1
            else:
                updated += 1

        return JsonResponse({
            "message": "Cities import complete.",
            "created": created,
            "updated": updated
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import db


@csrf_exempt
def get_transfer_history(request):
    try:
        # 1. Fetch vehicle data
        vehicle_ref = db.reference('/CompaniesData/wevois/VehicleData/Vehicle')
        vehicles = vehicle_ref.get() or {}

        # 2. Fetch transfer history data
        history_ref = db.reference('/CompaniesData/wevois/VehicleData/CityTransferHistory')
        transfers = history_ref.get() or {}

        created = 0
        updated = 0
        merged_results = []

        # 3. Loop vehicles and match with transfer history
        for vehicle_id, vehicle_info in vehicles.items():
            if not isinstance(vehicle_info, dict):
                continue

            vehicle_no = vehicle_info.get("vehicleNo")
            if not vehicle_no:
                continue

            # ✅ Ensure vehicle exists (create if missing)
            # vehicle_obj, _ = Vehicle.objects.get_or_create(
            #     vehicle_no=vehicle_no,
            #     defaults={
            #         "currentCity": vehicle_info.get("currentCity"),
            #         "is_active": vehicle_info.get("isActive") in ["true", "1", "yes", True],
            #     }
            # )

            try:
                vehicle_obj = Vehicle.objects.get(vehicle_no=vehicle_no)
            except Vehicle.DoesNotExist:
                # Vehicle not found, skip or handle as needed
                continue

            vehicle_transfers = transfers.get(vehicle_id, {})

            if isinstance(vehicle_transfers, dict):
                for _, record in vehicle_transfers.items():
                    if not isinstance(record, dict):
                        continue
                    # Parse Firebase _at
                    firebase_at = record.get("_at")
                    parsed_at = None
                    if firebase_at:
                        parsed_at = parse_datetime(firebase_at)
                        if parsed_at and timezone.is_naive(parsed_at):
                            parsed_at = timezone.make_aware(parsed_at)

                    # ✅ Create or update history record
                    obj, created_flag = CityTransferHistory.objects.update_or_create(
                        vehicle_id=vehicle_obj.id,
                        _at=parsed_at,
                        defaults={
                            "_by": record.get("_by"),
                            "newCity": record.get("newCity"),
                        }
                    )

                    if created_flag:
                        created += 1
                    else:
                        updated += 1



        return JsonResponse({
            "message": "Transfer history sync complete.",
            "vehicles_synced": len(vehicles),
            "created": created,
            "updated": updated,
            "count": len(merged_results),
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
