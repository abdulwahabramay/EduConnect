from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Forum, Comment
from .serializers import ForumSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters 

class ForumViewSet(viewsets.ModelViewSet):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]  
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'created_by']  
    search_fields = ['title', 'content', 'created_by__username']  
    ordering_fields = ['created_by', 'title', 'course']  
    ordering = ['title']  

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly] 
    
    queryset = Comment.objects.all()
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['forum', 'created_by']  
    search_fields = ['content', 'created_by__username']  
    ordering_fields = ['created_by', 'forum'] 
    ordering = ['forum']  

    def get_queryset(self):
        forum_id = self.request.query_params.get('forum_id')
        if forum_id:
            return Comment.objects.filter(forum__id=forum_id)
        
        return super().get_queryset()  
