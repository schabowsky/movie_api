from django.shortcuts import render
from urllib.request import urlopen
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status
from rest_framework.parsers import JSONParser

from .models import Movie, Comment
from .serializers import MovieSerializer, CommentSerializer

API_KEY = 'd2bd0434'

class Movies(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        """
        Return a list of all movies.
        """
        movies = Movie.objects.all()
        movies_list = [movie.title for movie in movies]
        # serializer = MovieSerializer(movies, many=True)
        return Response(movies_list)

    def post(self, request, format=None):
        """
        Add new movie to database.
        """
        title = request.data['title'].split()
        title = '+'.join(title)
        data = urlopen('http://www.omdbapi.com/?t={}&apikey={}'.format(title, API_KEY))
        json_data = JSONParser().parse(data)
        ms = Movie()
        ms.title, ms.data = json_data['Title'], json_data
        ms.save()
        return Response(request.data)


class Comments(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        """
        Return a list of all comments.
        """
        criterium = ''
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
        movie_id = request.data.get('movie_id')
        if movie_id:
            if Movie.objects.filter(id=int(movie_id)):
                try:
                    comment = Comment(body=request.data['body'], movie_id=int(movie_id))
                    comment.save()
                    return Response(request.data)
                except Exception as inst:
                    pass
        error = {'Error': 'Wrong movie_id'}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


class Top(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        """
        Return a list of top movies.
        """
        comments = Comment.objects.all().values('movie_id').annotate(comment_count=Count('movie_id')).order_by('-comment_count')

        rank = 0
        count = -1
        for c in comments:
            if count != c['comment_count']:
                rank += 1
            c['rank'] = rank
            count = c['comment_count']

        return Response(comments)
