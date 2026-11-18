from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Enrollment, Choice, Submission

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.first()
    submission = Submission.objects.create(enrollment=enrollment)
    
    question_ids = request.POST.getlist('question_ids')
    for q_id in question_ids:
        choice_ids = request.POST.getlist(f'choices_{q_id}')
        for c_id in choice_ids:
            choice = Choice.objects.get(pk=c_id)
            submission.choices.add(choice)
            
    return HttpResponseRedirect(reverse('djangoapp:show_exam_result', args=[course.id, submission.id]))

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    choices = submission.choices.all()
    
    total_score = 0
    questions = course.question_set.all()
    max_score = sum(q.grade for q in questions)
    
    grade_results = {}
    for q in questions:
        q_choices = q.choice_set.all()
        correct_choices = set(c.id for c in q_choices if c.is_correct)
        user_choices = set(c.id for c in choices if c.question == q)
        if correct_choices == user_choices:
            total_score += q.grade
            grade_results[q] = True
        else:
            grade_results[q] = False
            
    context = {
        'course': course,
        'grade_results': grade_results,
        'score': total_score,
        'max_score': max_score
    }
    return render(request, 'djangoapp/exam_result_bootstrap.html', context)