import json
from math import atan2, cos, radians, sin, sqrt
from os.path import defpath

import bcrypt
from django.db import IntegrityError
from django.db.models import CharField, Value
from django.http import QueryDict
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_decode_handler
from .customIsAuth import AllowAny, IsAuthenticated, IsAdminUser

from .models import *
from .serializers import *

class PermissionsPerMethodMixin(object):
    def get_permissions(self):
        """
        Allows overriding default permissions with @permission_classes
        """
        view = getattr(self, self.action)
        if hasattr(view, 'permission_classes'):
            return [permission_class() for permission_class in view.permission_classes]
        return super().get_permissions()

#######################
###   PERSONS API   ###

class personsViewSet(PermissionsPerMethodMixin, viewsets.GenericViewSet):

    @permission_classes([AllowAny])
    def create_token(self,user):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return token

    # GET 127.0.0.1:8000/api/persons/
    @permission_classes([IsAdminUser])
    def list(self, request, *args, **kwargs):
        """" list all users """
        queryset = Persons.objects.all().order_by('lastName')
        serializer = personsSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # GET 127.0.0.1:8000/api/persons/1
    @permission_classes([IsAuthenticated])
    def retrieve(self, request,pk=None, *args, **kwargs):
        """" get a user profile by it's id """
        queryset = Persons.objects.filter(id_person=pk)
        serializer = personsSerializer(queryset, many=True)
        return Response(serializer.data)

    # POST 127.0.0.1:8000/api/persons/
    @permission_classes([AllowAny])
    def create(self, request, *args, **kwargs):
        """" create a new user """
        data = request.data.copy()
        data['password']= bcrypt.hashpw(data['password'].encode('utf8'), bcrypt.gensalt())
        data['password'] = data['password'].decode('utf8')
        serializer = personsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            queryset = Persons.objects.filter(email=data['email'])
            user = queryset.get()
            user.token = self.create_token(user)
            queryset = set()
            queryset.add(user)
            serializer = personsLoginGetTokenSerializer(queryset,many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError as exception:
            if "unique_alias" in str(exception):
                error = "alias already exists"
            elif "unique_email" in str(exception):
                error = "email already exists"
            return Response({'error': error}, status=status.HTTP_409_CONFLICT)

    # GET 127.0.0.1:8000/api/persons/aliases/
    @action(detail=False, methods=['get'])
    @permission_classes([IsAdminUser])
    def aliases(self, request, *args, **kwargs):
        """" get all used aliases"""
        queryset = Persons.objects.all()
        serializer = aliasesSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # GET 127.0.0.1:8000/api/persons/login/?email=john.doe@gmail.com&pwd=testpwd1
    @action(detail=False, methods=['get'])
    @permission_classes([AllowAny])
    def login(self, request, *args, **kwargs):
        """" authenticate user w/o token"""
        email = request.query_params.get('email')
        pwd = request.query_params.get('pwd')
        queryset = Persons.objects.filter(email=email)
        if queryset:
            user = queryset.get()
            if bcrypt.checkpw(pwd.encode('utf8'), user.password.encode('utf8')):
                user.token = self.create_token(user)
                queryset = set()
                queryset.add(user)
                serializer = personsLoginGetTokenSerializer(queryset,many=True)
                return Response(serializer.data)
            else:
                error = "wrong sign-in information for: %s"%(email)
                return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
        else:
            error = "wrong sign-in information for: %s"%(email)
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
    
    # GET 127.0.0.1:8000/api/persons/login_token/?token=dghffgnndsklskjskff
    @action(detail=False, methods=['get'])
    @permission_classes([AllowAny])
    def login_token(self, request, *args, **kwargs):
        """" authenticate user w/ token"""
        token = request.query_params.get('token')
        try:
            decoded_payload = jwt_decode_handler(token) #TODO signature expired? 
            id_person = decoded_payload['user_id']
            queryset = Persons.objects.filter(id_person=id_person)
            if queryset:
                serializer = personsLoginSerializer(queryset,many=True)
                return Response(serializer.data)
            else:
                error = "Invalid token"
                return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
        except:
            error = "Invalid token"
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)

    # GET,POST 127.0.0.1:8000/api/persons/1/towns/
    @action(detail=True, methods=['get','post'])
    @permission_classes([IsAuthenticated])
    def towns(self, request, pk=None, *args, **kwargs):
        if request.method == 'GET':
            """" get all towns of a user"""
            queryset = PersonsTowns.objects.filter(id_person=pk)
            serializer = personsTownsDetailSerializer(queryset, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            """" add a new town to the user """
            data = request.data.copy()
            data['id_person']=pk
            serializer = personsTownsSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET,POST 127.0.0.1:8000/api/persons/1/tools/
    @action(detail=True, methods=['get','post'])
    @permission_classes([IsAuthenticated])
    def tools(self, request, pk=None, *args, **kwargs):
        if request.method == 'GET':
            """" get all tools belonging to a user"""
            queryset = Tools.objects.filter(id_person=pk)
            serializer = toolsDetailSerializer(queryset, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            """" add a new tool to the user """
            data = request.data.copy()
            data['id_person']=pk
            serializer = toolsSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # GET,POST 127.0.0.1:8000/api/persons/1/reviews/
    @action(detail=True, methods=['get','post'])
    @permission_classes([IsAuthenticated])
    def reviews(self, request, pk=None, *args, **kwargs):
        if request.method == 'GET':
            """" get all reviews belonging to a user"""
            queryset = PersonReviews.objects.filter(id_person=pk)
            serializer = personReviewsSerializer(queryset, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            """" add a new review to the user """
            data = request.data.copy()
            data['id_person']=pk
            serializer = personReviewsSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET 127.0.0.1:8000/api/persons/1/groups/
    @action(detail=True, methods=['get'])
    @permission_classes([IsAuthenticated])
    def groups(self, request, pk=None, *args, **kwargs):
        """" get all groups in which the user is """
        queryset = GroupsMembers.objects.filter(id_person=pk).order_by('id_groupName')
        serializer = membersGroupsDetailSerializer(queryset, many=True)
        return Response(serializer.data)


######################
###   TOOLS  API   ###

class toolsViewSet(PermissionsPerMethodMixin, viewsets.GenericViewSet):

    # GET 127.0.0.1:8000/api/tools/
    @permission_classes([AllowAny])
    def list(self, request, *args, **kwargs):
        """" list all tools """
        queryset = Tools.objects.all()
        serializer = toolsBasicSerializer(queryset, many=True)
        return Response(serializer.data)

    # GET 127.0.0.1:8000/api/tools/1
    @permission_classes([AllowAny])
    def retrieve(self, request,pk=None, *args, **kwargs):
        """" get a tool by it's id """
        queryset = Tools.objects.filter(id_tool=pk)
        serializer = toolsDetailWithOwnerSerializer(queryset, many=True)
        return Response(serializer.data)

    # GET,POST 127.0.0.1:8000/api/tools/1/images/
    @action(detail=True, methods=['get','post'])
    @permission_classes([AllowAny])
    def images(self, request, pk=None, *args, **kwargs):
        if request.method == 'GET':
            """" get all images belonging to a tool"""
            queryset = ToolImages.objects.filter(id_tool=pk)
            serializer = toolImagesSerializer(queryset, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            """" add a new image to the tool """
            data = request.data.copy()
            data['id_tool']=pk
            serializer = toolImagesSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # GET,POST 127.0.0.1:8000/api/tools/1/reviews/
    @action(detail=True, methods=['get','post'])
    @permission_classes([IsAuthenticated])
    def reviews(self, request, pk=None, *args, **kwargs):
        if request.method == 'GET':
            """" get all reviews made on a tool"""
            queryset = ToolReviews.objects.filter(id_tool=pk)
            serializer = toolReviewsSerializer(queryset, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            """" add a new review on the tool """
            data = request.data.copy()
            data['id_tool']=pk
            serializer = toolReviewsSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # GET 127.0.0.1:8000/api/tools/1/groups/
    @permission_classes([IsAuthenticated])
    @action(detail=True, methods=['get'])
    def groups(self, request, pk=None, *args, **kwargs):
        """" get all groups in which a tool is """
        queryset = ToolsGroups.objects.filter(id_tool=pk)
        serializer = toolsGroupsDetailSerializer(queryset, many=True)
        return Response(serializer.data)



######################
###   GROUPS API   ###

class groupsViewSet(PermissionsPerMethodMixin, viewsets.GenericViewSet):

    # GET 127.0.0.1:8000/api/groups/
    @permission_classes([AllowAny])
    def list(self, request, *args, **kwargs):
        """" list all groups (public & private) """
        queryset = Groups.objects.all()
        serializer = groupsSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # POST 127.0.0.1:8000/api/groups/
    @permission_classes([IsAuthenticated])
    def create(self, request, *args, **kwargs):
        """" create a new group """
        serializer = groupsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET 127.0.0.1:8000/api/groups/public/
    @action(detail=False, methods=['get'])
    @permission_classes([AllowAny])
    def public(self, request, *args, **kwargs):
        country = request.query_params.get('countryCode')
        town = request.query_params.get('id_town')
        if country:
            # GET 127.0.0.1:8000/api/groups/public/?countryCode=BE
            """" list all public groups of a certain country"""
            queryset = Groups.objects.raw( 
                '''
                SELECT * 
                FROM "Groups"
                JOIN "Towns" ON ("Groups".id_town = "Towns".id_town)
                WHERE "Groups"."groupType" = 'public' AND "Towns"."id_countryCode" = '%s';
                '''%(country)
            )
        elif town:
            # GET 127.0.0.1:8000/api/groups/public/?id_town=1
            """" list all public groups of a certain town"""
            queryset = Groups.objects.filter(groupType='public',id_town=town)
        else:
            """" list all public groups """
            queryset = Groups.objects.filter(groupType='public')

        serializer = groupsDetailSerializer(queryset, many=True)
        return Response(serializer.data)



    # GET 127.0.0.1:8000/api/groups/private/
    @action(detail=False, methods=['get'])
    @permission_classes([IsAuthenticated])
    def private(self, request, *args, **kwargs):
        country = request.query_params.get('countryCode')
        town = request.query_params.get('id_town')
        if country:
            # GET 127.0.0.1:8000/api/groups/private/?countryCode=BE
            """" list all private groups of a certain country"""
            queryset = Groups.objects.raw( 
                '''
                SELECT * 
                FROM "Groups"
                JOIN "Towns" ON ("Groups".id_town = "Towns".id_town)
                WHERE "Groups"."groupType" = 'private' AND "Towns"."id_countryCode" = '%s';
                '''%(country)
            )
        elif town:
            # GET 127.0.0.1:8000/api/groups/private/?id_town=1
            """" list all private groups of a certain town"""
            queryset = Groups.objects.filter(groupType='private',id_town=town)
        else:
            """" list all private groups """
            queryset = Groups.objects.filter(groupType='private')

        serializer = groupsDetailSerializer(queryset, many=True)
        return Response(serializer.data)



    # GET,POST,DELETE 127.0.0.1:8000/api/groups/members/
    @action(detail=False, methods=['get','post','delete'])
    @permission_classes([IsAuthenticated])
    def members(self, request, *args, **kwargs):
        if request.method == 'GET':
            # GET 127.0.0.1:8000/api/groups/members/?groupName=TestGroup1
            """" list all members of a group """
            groupName = request.query_params.get('groupName')
            queryset = GroupsMembers.objects.filter(id_groupName=groupName)
            serializer = groupsMembersDetailSerializer(queryset, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            """" add a new member to a group """
            serializer = groupsMembersSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            """" delete a member from a group """
            # GET 127.0.0.1:8000/api/groups/members/?groupName=TestGroup1&id_person=1
            groupName = request.query_params.get('groupName')
            id_person = request.query_params.get('id_person')
            queryset = GroupsMembers.objects.filter(id_groupName=groupName,id_person=id_person)
            if queryset:
                queryset.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                error = "The member with id: %s does not exist in group: %s"%(id_person,groupName)
                return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)


    # GET 127.0.0.1:8000/api/groups/admins/
    @action(detail=False, methods=['get'])
    @permission_classes([AllowAny])
    def admins(self, request, *args, **kwargs):
        # GET 127.0.0.1:8000/api/groups/admins/?groupName=TestGroup1
        """" list all admins of a group """
        groupName = request.query_params.get('groupName')
        queryset = GroupsMembers.objects.filter(id_groupName=groupName,groupAdmin=True)
        serializer = groupsMembersDetailSerializer(queryset, many=True)
        return Response(serializer.data)

    # GET 127.0.0.1:8000/api/groups/tools/
    @action(detail=False, methods=['get','post','delete'])
    @permission_classes([AllowAny])
    def tools(self, request, *args, **kwargs):
        if request.method == 'GET':
            # GET 127.0.0.1:8000/api/groups/tools/?groupName=TestGroup1
            """" list all tools of a group """
            groupName = request.query_params.get('groupName')
            queryset = ToolsGroups.objects.filter(id_groupName=groupName)
            serializer = groupsToolsDetailSerializer(queryset, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            """" add a new tool to a group """
            serializer = groupsToolsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            """" delete a tool from a group """
            # GET 127.0.0.1:8000/api/groups/tools/?groupName=TestGroup1&id_tool=1
            groupName = request.query_params.get('groupName')
            id_tool = request.query_params.get('id_tool')
            queryset = ToolsGroups.objects.filter(id_groupName=groupName,id_tool=id_tool)
            if queryset:
                queryset.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                error = "The tool with id: %s does not exist in group: %s"%(id_tool,groupName)
                return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
            

######################
###   TOWNS  API   ###

class townsViewSet(PermissionsPerMethodMixin, viewsets.GenericViewSet):

    # GET 127.0.0.1:8000/api/towns/
    @permission_classes([AllowAny])
    def list(self, request, *args, **kwargs):
        country = request.query_params.get('countryCode')
        if country:
            # GET 127.0.0.1:8000/api/towns/?countryCode=BE
            """" list all towns of a country """
            queryset = Towns.objects.filter(id_countryCode=country).order_by('townName')
        else:
            """" list all towns """
            queryset = Towns.objects.all().order_by('townName')

        serializer = townsSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # POST 127.0.0.1:8000/api/towns/
    @permission_classes([IsAuthenticated])
    def create(self, request, *args, **kwargs):
        """" add a new town """
        serializer = townsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



#######################
###  COUNTRIES API  ###

class countriesViewSet(PermissionsPerMethodMixin, viewsets.GenericViewSet):

    # GET 127.0.0.1:8000/api/countries/
    @permission_classes([AllowAny])
    def list(self, request, *args, **kwargs):
        """" list all countries """
        queryset = Countries.objects.all().order_by('countryName')
        serializer = countriesSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # POST 127.0.0.1:8000/api/countries/
    @permission_classes([IsAuthenticated])
    def create(self, request, *args, **kwargs):
        """" add a new country """
        serializer = countriesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


#######################
###   SEARCH  API   ###

class searchViewSet(PermissionsPerMethodMixin, viewsets.GenericViewSet):

    def distCalc(self,town_Search, group):
        R = 6373.0 # approximate radius of earth in km

        lat1 = radians(abs(town_Search['lat']))
        lon1 = radians(abs(town_Search['lng']))
        lat2 = radians(abs(group['town']['lat']))
        lon2 = radians(abs(group['town']['lng']))

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c 

        if (distance <= group['groupRange']):
            return True
        return False

    # GET 127.0.0.1:8000/api/search/?what=xxxx&where=yyyyy
    @permission_classes([AllowAny])
    def list(self, request, *args, **kwargs):
        """" list all users """
        what = "'%%{}%%'".format(request.query_params.get('what').replace("'", ""))
        where = request.query_params.get('where')
        townSearchQuery =   '''
                            SELECT *
                            FROM "Towns"
                            WHERE LOWER("Towns"."townName") LIKE LOWER(%s) ;
                            ''' %(where)
        townSearchQuerySet = Towns.objects.raw(townSearchQuery)
        townSearch = townsSerializer(townSearchQuerySet, many=True).data

        allGroupsWToolQuery =   '''
                                SELECT *
                                FROM "Groups"
                                JOIN "Towns" ON ("Groups".id_town = "Towns".id_town)
                                JOIN "ToolsGroups" ON ("Groups"."id_groupName" = "ToolsGroups"."id_groupName")
                                JOIN "Tools" ON ("ToolsGroups".id_tool = "Tools".id_tool)
                                WHERE "Groups"."groupType" = 'public' 
                                AND LOWER("Tools"."toolName") LIKE LOWER(%s);
                                ''' % (what)
        allGroupsWToolQuerySet = Groups.objects.raw(allGroupsWToolQuery)
        allGroupsWTool = groupsDetailSerializer(allGroupsWToolQuerySet, many=True).data
        
        groups = []
        if(len(townSearch) != 0):
            for group in allGroupsWTool:
                if(self.distCalc(townSearch[0],group)):
                    groups.append(group)
                else:
                    pass
        
        return Response(groups)
