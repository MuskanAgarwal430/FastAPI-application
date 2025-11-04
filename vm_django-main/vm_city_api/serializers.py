from rest_framework import serializers
from vm_city.models import IssuePart, Issue

class IssuePartSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssuePart
        field = '__all__'


class IssueSerializer(serializers.ModelSerializer):
    issue_parts = IssuePartSerializer(many=True, required=False)

    class Meta:
        model = Issue
        fields = '__all__'

    def create(self, validated_data):
        issue_part_data = validated_data.pop('issue_parts',[])
        issue = Issue.objects.create(**validated_data)
        for part_data in issue_part_data:
            IssuePart.objects.create(issue=issue, **part_data)
        return issue