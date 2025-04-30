from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET' , 'HEAD' , 'OPTIONS']:
            return True
        return obj.user == request.user
    

class IsReviewOwner(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True
    
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET' , 'HEAD' , 'OPTIONS']:
            return True
        return obj.user == request.user
    
class IsProductOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user