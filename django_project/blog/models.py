from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from users.models import CustomUser
from courses.models import Course


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    course = models.ForeignKey(Course, related_name='assignments', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
class AssignmentSubmission(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='submissions')
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='assignment_submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    
    class Meta:
        unique_together = ('student', 'assignment')

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    course = models.ForeignKey(Course, related_name='announcements', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey(Course, related_name='quizzes', on_delete=models.CASCADE)
    due_date = models.DateTimeField()
    time_limit = models.IntegerField(help_text="Time limit in minutes")
    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=100, choices=[('multiple_choice', 'Multiple Choice'), ('true_false', 'True/False')])
    correct_answer = models.TextField() 
    options = models.JSONField(default=list) 

    def __str__(self):
        return self.text

class Submission(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='submissions', on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='quiz_submissions', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(null=True, blank=True)
    answers = models.JSONField(default=dict)  

    def __str__(self):
        return f"{self.student.username} submitted {self.quiz.title}"

    def calculate_score(self):
        correct_answers = 0
        for question_id, answer in self.answers.items():
            try:
                question = Question.objects.get(id=question_id)
                print(f"Question ID: {question_id}, Submitted Answer: {answer}, Correct Answer: {question.correct_answer}")

                if question.correct_answer.lower() == answer.lower():
                    correct_answers += 1
                    print("Correct answer!")
                else:
                    print("Incorrect answer.")

            except Question.DoesNotExist:
                print(f"Question with ID {question_id} does not exist.")

        self.score = correct_answers
        print(f"Final score for {self.student.username}: {self.score}")
        self.save()
        
class DiscussionThread(models.Model):
    course = models.ForeignKey(Course, related_name='discussion_threads', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='threads', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class DiscussionPost(models.Model):
    thread = models.ForeignKey(DiscussionThread, related_name='posts', on_delete=models.CASCADE)
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.created_by.username} in {self.thread.title}"


class DiscussionReply(models.Model):
    post = models.ForeignKey('DiscussionPost', related_name='replies', on_delete=models.CASCADE)
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.created_by.username} on {self.post}"