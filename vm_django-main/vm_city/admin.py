from django.contrib import admin

from .models import City, Parts, Vehicle, Issue, IssuePart, CityTransferHistory, Vendor, RootCause


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cityIncharge', 'isActive')
    list_filter = ('isActive',)
    search_fields = ('name', 'cityIncharge')

@admin.register(RootCause)
class RootCauseAdmin(admin.ModelAdmin):
    list_display = ('firebase_id', 'name')



@admin.register(Parts)
class PartsAdmin(admin.ModelAdmin):
    list_display = ('id','part_id', 'name', 'code', 'unit', 'isReturnRequiredValue')
    search_fields = ('name', 'code')
    list_filter = ('isReturnRequiredValue',)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle_no', 'currentCity', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('vehicle_no', 'currentCity')


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (       # Assuming this is a field you added or have
    'canRunInWard',
    'canRunInWardResolved',
    'city',
    'confirmBy',
    'confirmDate',
    'createdBy',
    'createdTime',
    'creationDate',
    'date',
    'description',
    'driverId',
    'driverName',
    'firebase_id',
    'id',
    'isBillAvailable',
    'jobCardId',
    'mechanicName',
    'reopenKey',
    'repairCost',    # Assuming this is a field you added or have
    'resolvedDate',
    'resolvedDescription',
    'rootCauses',
    'status',
    'unpaidBills',
    'updateKey',
    'vehicle',
    'vehicleIssue',
    'workingHrs',
)
    list_filter = ('status', 'city', 'resolvedDate', 'created_at', 'canRunInWard','vehicle')
    search_fields = ('vehicle__vehicle_no', 'driverName', 'mechanicName', 'vehicleIssue', 'jobCardId')
    date_hierarchy = 'created_at'


@admin.register(IssuePart)
class IssuePartAdmin(admin.ModelAdmin):
    list_display = ('id', 'issue', 'stock','part','qty', 'price', 'amount', 'purchase_id')
    search_fields = ('issue__id',)
    list_filter = ('issue',)


@admin.register(CityTransferHistory)
class CityTransferHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'newCity', '_at', '_by')
    search_fields = ('vehicle__vehicle_no', 'newCity', '_by')
    date_hierarchy = '_at'


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('firebase_id', 'name', 'contact', 'city', 'account_name', 'bank_name', 'upi_id', 'ifsc_code')
    search_fields = ('name', 'contact', 'city', 'account_name', 'upi_id')
    list_filter = ('city', 'bank_name')
