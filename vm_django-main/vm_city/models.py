from django.db import models

# Create your models here.
class City(models.Model):
    name = models.CharField(max_length=155)
    isActive = models.BooleanField(default=True)
    cityIncharge = models.CharField(max_length=255)


class Parts(models.Model):
    part_id = models.CharField(max_length=255, unique=True, null=True)  # Firebase unique key
    code = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    isReturnRequiredValue = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.part_id



class Vehicle(models.Model):
    vehicle_no = models.CharField(max_length=255)
    currentCity = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.vehicle_no



class Issue(models.Model):
    firebase_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    vehicle = models.CharField(max_length=255,  null=True, blank=True)
    vehicleIssue = models.TextField(blank=True, null=True)
    canRunInWard = models.CharField(max_length=255, blank=True, null=True)
    canRunInWardResolved = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    driverId = models.CharField(max_length=255, blank=True, null=True)
    driverName = models.CharField(max_length=255, blank=True, null=True)
    mechanicName = models.CharField(max_length=255, blank=True, null=True)
    jobCardId = models.CharField(max_length=255, blank=True, null=True)
    repairCost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    resolvedDate = models.DateTimeField(blank=True, null=True)
    resolvedDescription = models.TextField(blank=True, null=True)
    rootCauses = models.TextField(blank=True, null=True)
    workingHrs = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    isBillAvailable = models.CharField(max_length=255, blank=True, null=True)
    unpaidBills = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=255, null=True, blank=True)
    reopenKey = models.CharField(max_length=255, blank=True, null=True)
    updateKey = models.CharField(max_length=255, blank=True, null=True)
    confirmBy = models.CharField(max_length=255, blank=True, null=True)
    confirmDate = models.DateTimeField(blank=True, null=True)
    createdBy = models.CharField(max_length=255, blank=True, null=True)
    createdTime = models.TimeField(blank=True, null=True)
    creationDate = models.DateField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.firebase_id}"


class IssuePart(models.Model):
    issue = models.ForeignKey(
        Issue,
        to_field='firebase_id',
        db_column='firebase_id',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issue_parts'
    )
    part = models.ForeignKey(Parts, on_delete=models.CASCADE,null=True)
    stock = models.CharField(max_length=255,null=True, blank=True)
    qty = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    purchase_id = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return f"Issue Firebase ID: {self.issue.firebase_id if self.issue else 'N/A'}"


class RootCause(models.Model):
    firebase_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    CreatedById = models.CharField(max_length=25)

class CityTransferHistory(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='transfer_history')
    newCity = models.CharField(max_length=255)
    _at = models.DateTimeField()
    _by = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.vehicle.vehicle_no} from {self.from_city} to {self.to_city} on {self.transfer_date.strftime('%Y-%m-%d')}"


class Vendor(models.Model):
    firebase_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    account_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    ifsc_code = models.CharField(max_length=50, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name




