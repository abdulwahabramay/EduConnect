from rest_framework import serializers
from .models import Profile, Follow, Connection, FriendRequest
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'role') 

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'user','bio', 'interests', 'skills']

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['follower', 'followed', 'created_at']
        
    def create(self, validated_data):
        if validated_data['follower'] == validated_data['followed']:
            raise serializers.ValidationError("You cannot follow yourself.")
        return super().create(validated_data)
    
class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['from_user', 'to_user', 'created_at', 'accepted']
        read_only_fields = ['from_user', 'created_at', 'accepted']

    def create(self, validated_data):
        from_user = self.context['request'].user
        to_user = validated_data['to_user']
        
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError("Friend request already sent.")

        if Connection.objects.filter(user1=from_user, user2=to_user).exists():
            raise serializers.ValidationError("You are already friends.")

        return FriendRequest.objects.create(from_user=from_user, to_user=to_user)
    
    def update(self, instance, validated_data):
        accepted = validated_data.get('accepted', instance.accepted)
        instance.accepted = accepted
        instance.save()

        if accepted:
            Connection.objects.create(user1=instance.from_user, user2=instance.to_user)
            Connection.objects.create(user1=instance.to_user, user2=instance.from_user)

        return instance
    
class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ['user1', 'user2']