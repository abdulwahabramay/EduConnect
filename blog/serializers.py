from rest_framework import serializers
from .models import Assignment,AssignmentSubmission, Announcement, Quiz, Question, Submission, DiscussionThread, DiscussionPost, DiscussionReply



class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'
        
class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'student', 'assignment', 'file', 'submitted_at']
        read_only_fields = ['submitted_at']

    def validate(self, data):
        # Ensure that the student is enrolled in the course of the assignment
        student = data['student']
        assignment = data['assignment']
        if assignment.course not in student.enrolled_courses.all():
            raise serializers.ValidationError("You are not enrolled in the course for this assignment.")
        return data

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'
        
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
        
class StudentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'question_type', 'options']


class QuizSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'course', 'due_date', 'time_limit', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(quiz=quiz, **question_data)
        return quiz

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)
        instance = super().update(instance, validated_data)
        if questions_data:
            instance.questions.all().delete() 
            for question_data in questions_data:
                Question.objects.create(quiz=instance, **question_data)
        return instance

    def get_questions(self, obj):
        user = self.context['request'].user
        if user.role == 'student':
            return StudentQuestionSerializer(obj.questions.all(), many=True).data
        return QuestionSerializer(obj.questions.all(), many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['questions'] = self.get_questions(instance)
        return representation


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'

class DiscussionThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionThread
        fields = '__all__'

class DiscussionPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionPost
        fields = '__all__'


class DiscussionReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionReply
        fields = '__all__'