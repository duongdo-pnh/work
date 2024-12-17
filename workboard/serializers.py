from rest_framework import serializers
from .models import WorkBoard, TaskList,Task, Comment, Attachment
from django.contrib.auth.models import User

class WorkBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkBoard
        fields = ['id', 'name', 'description', 'created_by', 'created_at']
class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskList
        fields = ['id', 'workboard', 'name', 'description']
    
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'tasklist', 'name', 'description', 'deadline', 'completed', 'assigned_to', 'created_at']
        read_only_fields = ['id', 'created_at','tasklist']
    
    def update(self, instance, validated_data):
        instance.completed = validated_data.get('completed', instance.completed)
        instance.save()  
        return instance

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'created_at']
        read_only_fields = ['author', 'created_at', 'task']  

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'task', 'user', 'file', 'uploaded_at']
        read_only_fields = ['user', 'uploaded_at', 'task']  
