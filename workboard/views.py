from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import WorkBoard, TaskList, Task, Comment
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework.decorators import action, api_view
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from django.core.mail import send_mail
from django.conf import settings
from .models import Task
from rest_framework import filters
from rest_framework.exceptions import PermissionDenied





class WorkBoardViewSet(viewsets.ModelViewSet):
    queryset = WorkBoard.objects.all()
    serializer_class = WorkBoardSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'description')  
    

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='tasklists')
    def add_tasklist(self, request, pk=None):
        """Thêm danh sách công việc vào bảng công việc."""
        try:
            workboard = self.get_object()  # Lấy bảng công việc theo ID
        except WorkBoard.DoesNotExist:
            return Response({"error": "WorkBoard not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(workboard=workboard)  # Gắn TaskList với WorkBoard
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        search_query = request.query_params.get('search', None)
        if search_query:
            workboards = WorkBoard.objects.filter(name__icontains=search_query)
            serializer = WorkBoardSerializer(workboards, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "No search query provided"}, status=400)

class TaskListViewSet(viewsets.ModelViewSet):
    queryset = TaskList.objects.all()
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='tasks')
    def add_task(self, request, pk=None):
        """Thêm thẻ công việc vào danh sách."""
        try:
            tasklist = self.get_object()  
        except TaskList.DoesNotExist:
            return Response({"error": "TaskList not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(tasklist=tasklist)  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]  

    


    def update(self, request, *args, **kwargs):
        task = self.get_object()

        # Kiểm tra quyền truy cập, chỉ cho phép cập nhật nếu người dùng là người được giao công việc
        if task.assigned_to != request.user:
            raise PermissionDenied("You do not have permission to update this task.")

        return super().update(request, *args, **kwargs)
    def destroy(self, request, *args, **kwargs):
        """Xóa một công việc."""
        try:
            instance = self.get_object()
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        # Kiểm tra quyền: chỉ người được gán hoặc người tạo công việc mới được xóa
        if request.user != instance.assigned_to and request.user != instance.tasklist.workboard.created_by:
            return Response(
                {"error": "You do not have permission to delete this task."},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_destroy(instance)
        return Response({"message": "Task deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']  
        try:
            task = Task.objects.get(id=task_id)  
        except Task.DoesNotExist:
            raise NotFound(detail="Task not found.")  
        # Lưu bình luận với người dùng và công việc
        serializer.save(author=self.request.user, task=task)

@api_view(['POST'])
def attach_file_to_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

    # Kiểm tra xem tệp tin có được gửi kèm theo yêu cầu hay không
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    attachment = Attachment.objects.create(task=task, file=file)

    # Serialize the attachment object
    serializer = AttachmentSerializer(attachment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def send_task_notification_email(request, task_id):
    task = Task.objects.get(id=task_id)  # Tìm công việc theo ID

    subject = f"Task Created: {task.description}"
    message = f"A new task '{task.description}' has been created. Please check your task list."

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Địa chỉ email người gửi
        [task.assigned_to.email],  # Người được giao công việc
        fail_silently=False,
    )

    return Response({"message": "Notification email sent."}, status=200)