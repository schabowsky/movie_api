from rest_framework import serializers

from .models import Movie, Comment


class MovieRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('title', 'data')


class CommentRequestSerializer(serializers.Serializer):
    movie_id = serializers.CharField(max_length=200)
    body = serializers.CharField(max_length=500)


class CommentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ('body', 'movie')
