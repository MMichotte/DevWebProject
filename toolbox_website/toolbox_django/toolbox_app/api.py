import json
from idlelib import query
from os.path import defpath

from django.http import QueryDict
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import *
from .serializers import *

#######################
###   PERSONS API   ###

class personsViewSet(viewsets.GenericViewSet):

    # GET 127.0.0.1:8000/api/persons/
    def list(self, request, *args, **kwargs):
        """" list all users """
        queryset = Persons.objects.all().order_by('lastName')
        serializer = personsSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # GET 127.0.0.1:8000/api/persons/1
    def retrieve(self, request,pk=None, *args, **kwargs):
        """" get a user profile by it's id """
        queryset = Persons.objects.filter(id_person=pk)
        serializer = personsSerializer(queryset, many=True)
        return Response(serializer.data)

    # POST 127.0.0.1:8000/api/persons/
    def create(self, request, *args, **kwargs):
        """" create a new user """
        serializer = personsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET 127.0.0.1:8000/api/persons/aliases/
    @action(detail=False, methods=['get'])
    def aliases(self, request, *args, **kwargs):
        """" get all used aliases"""
        queryset = Persons.objects.all()
        serializer = aliasesSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # GET 127.0.0.1:8000/api/persons/login/?email=john.doe@gmail.com
    @action(detail=False, methods=['get'])
    def login(self, request, *args, **kwargs):
        """" get user login info by its email"""
        email = request.query_params.get('email')
        queryset = Persons.objects.filter(email=email)
        if queryset:
            serializer = personsLoginSerializer(queryset,many=True)
            return Response(serializer.data)
        else:
            error = "no user with this email: %s"%(email)
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)

    # GET,POST 127.0.0.1:8000/api/persons/1/towns/
    @action(detail=True, methods=['get','post'])
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
    def groups(self, request, pk=None, *args, **kwargs):
        """" get all groups in which the user is """
        queryset = GroupsMembers.objects.filter(id_person=pk)
        serializer = membersGroupsDetailSerializer(queryset, many=True)
        return Response(serializer.data)


######################
###   TOOLS  API   ###

class toolsViewSet(viewsets.GenericViewSet):

    # GET 127.0.0.1:8000/api/tools/
    def list(self, request, *args, **kwargs):
        """" list all tools """
        queryset = Tools.objects.all()
        serializer = toolsDetailSerializer(queryset, many=True)
        return Response(serializer.data)

    # GET,POST 127.0.0.1:8000/api/tools/1/images/
    @action(detail=True, methods=['get','post'])
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
    @action(detail=True, methods=['get'])
    def groups(self, request, pk=None, *args, **kwargs):
        """" get all groups in which a tool is """
        queryset = ToolsGroups.objects.filter(id_tool=pk)
        serializer = toolsGroupsDetailSerializer(queryset, many=True)
        return Response(serializer.data)



######################
###   GROUPS API   ###

class groupsViewSet(viewsets.GenericViewSet):

    # GET 127.0.0.1:8000/api/groups/
    def list(self, request, *args, **kwargs):
        """" list all groups (public & private) """
        queryset = Groups.objects.all()
        serializer = groupsSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # POST 127.0.0.1:8000/api/towns/
    def create(self, request, *args, **kwargs):
        """" create a new group """
        serializer = groupsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET 127.0.0.1:8000/api/groups/public/
    @action(detail=False, methods=['get'])
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



    # GET,POST 127.0.0.1:8000/api/groups/members/
    @action(detail=False, methods=['get','post','delete'])
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
    def admins(self, request, *args, **kwargs):
        # GET 127.0.0.1:8000/api/groups/admin/?groupName=TestGroup1
        """" list all admins of a group """
        groupName = request.query_params.get('groupName')
        queryset = GroupsMembers.objects.filter(id_groupName=groupName,groupAdmin=True)
        serializer = groupsMembersDetailSerializer(queryset, many=True)
        return Response(serializer.data)

    # GET 127.0.0.1:8000/api/groups/tools/
    @action(detail=False, methods=['get','post','delete'])
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

class townsViewSet(viewsets.GenericViewSet):

    # GET 127.0.0.1:8000/api/towns/
    def list(self, request, *args, **kwargs):
        country = request.query_params.get('countryCode')
        if country:
            # GET 127.0.0.1:8000/api/towns/?countryCode=BE
            """" list all towns of a country """
            queryset = Towns.objects.filter(id_countryCode=country)
        else:
            """" list all towns """
            queryset = Towns.objects.all()

        serializer = townsSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # POST 127.0.0.1:8000/api/towns/
    def create(self, request, *args, **kwargs):
        """" add a new town """
        serializer = townsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



#######################
###  COUNTRIES API  ###

class countriesViewSet(viewsets.GenericViewSet):

    # GET 127.0.0.1:8000/api/countries/
    def list(self, request, *args, **kwargs):
        """" list all countries """
        queryset = Countries.objects.all()
        serializer = countriesSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # POST 127.0.0.1:8000/api/countries/
    def create(self, request, *args, **kwargs):
        """" add a new country """
        serializer = countriesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)