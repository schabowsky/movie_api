from django.shortcuts import render
from urllib.request import urlopen
from django.db.models import Count
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status
from rest_framework.parsers import JSONParser

from .models import Movie, Comment
from .serializers import (MovieRequestSerializer, MovieSerializer,
    CommentRequestSerializer, CommentSerializer)
from settings.secret_settings import API_KEY


class Movies(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        """
        Return a list of all movies.
        """
        movies = Movie.objects.all()
        movies_list = [movie.title for movie in movies]
        return Response(movies_list)

    def post(self, request, format=None):
        """
        Add new movie to database.
        """
        movie = MovieRequestSerializer(data=request.data)
        if movie.is_valid():
            title = movie.validated_data['title'].split()
            title = '+'.join(title)
            if not Movie.objects.filter(title__iexact=title):
                try:
                    data = urlopen('http://www.omdbapi.com/?t={}&apikey={}'.format(title, API_KEY))
                    json_data = JSONParser().parse(data)
                except Exception as inst:
                    pass
                if json_data['Response'] == 'True':
                    ms = Movie()
                    try:
                        ms.title, ms.data = json_data['Title'], json_data
                        ms.save()
                        return Response(MovieSerializer(ms).data)
                    except Exception as inst:
                        pass
        error = {'Error': 'Wrong title or movie already in database'}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


class Comments(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        """
        Return a list of all comments.
        """
        criterium = request.query_params.get('movie_id')
        if criterium:
            comments = Comment.objects.filter(movie_id=criterium)
        else:
            comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Add new comment to database.
        """
        comment = CommentRequestSerializer(data=request.data)
        if comment.is_valid():
            try:
                movie_id = int(comment.validated_data['movie_id'])
                if Movie.objects.filter(id=movie_id):
                        comment = Comment(body=comment.validated_data['body'], movie_id=movie_id)
                        comment.save()
                        return Response(comment)
            except ValueError:
                error = {'Error': 'Wrong movie_id'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class Top(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        """
        Return a list of top movies.
        """
        start_date = request.query_params.get('start_date')
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime(1970, 1, 1)
        end_date = request.query_params.get('end_date')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date = datetime.now()

        comments = Comment.objects.filter(ts__range=(start_date, end_date)).values('movie_id').annotate(comment_count=Count('movie_id')).order_by('-comment_count')

        rank = 0
        count = -1
        for c in comments:
            if count != c['comment_count']:
                rank += 1
            c['rank'] = rank
            count = c['comment_count']

        return Response(comments)
