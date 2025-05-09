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
        return obj.customer == request.user
    

class IsOrderOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return super().has_permission(request, view)
    
    
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
    


    
class IsProductOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.seller == request.user
    

    def has_object_pemission(self , request , view , obj):
        return obj.seller == request.user
    


    


class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    

class IsCartOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user