from rest_framework import serializers


class CalendarAllDayEventSerializer(serializers.Serializer):
    summary = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)


class CalendarAllDayEventSetSerializer(serializers.Serializer):
    count = serializers.IntegerField(read_only=True)
    set = CalendarAllDayEventSerializer(read_only=True, many=True)


class CalendarHourlyEventSerializer(serializers.Serializer):
    start = serializers.DateTimeField(read_only=True, allow_null=True, default=None)
    start_spoken = serializers.CharField(read_only=True, allow_null=True, default=None)    # e.g. 10:00 AM
    summary = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)


class CalendarHourlyEventSetSerializer(serializers.Serializer):
    count = serializers.IntegerField(read_only=True)
    set = CalendarHourlyEventSerializer(read_only=True, many=True)


class CalendarEventsSerializer(serializers.Serializer):
    count = serializers.IntegerField(read_only=True)
    all_day = CalendarAllDayEventSetSerializer()
    hourly_events = CalendarHourlyEventSetSerializer()


class CalendarDateSerializer(serializers.Serializer):
    date = serializers.CharField(read_only=True)
    events = CalendarEventsSerializer(read_only=True)
