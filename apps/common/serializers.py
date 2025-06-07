from rest_framework import serializers
from rest_framework.fields import empty


class BaseSerializer(serializers.ModelSerializer):
    """序列化器基类"""
    
    def __init__(self, instance=None, data=empty, **kwargs):
        # 动态字段选择
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        
        super().__init__(instance, data, **kwargs)
        
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
        if exclude is not None:
            for field_name in exclude:
                self.fields.pop(field_name, None)


class TimestampSerializer(serializers.ModelSerializer):
    """时间戳序列化器"""
    created_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    
    class Meta:
        abstract = True 