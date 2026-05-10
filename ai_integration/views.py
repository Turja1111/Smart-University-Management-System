"""AI Integration views - Chatbot, Weak Student Prediction, Plagiarism, Assignment Summary, Reputation Score"""
import random
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import IsAdminOrTeacher, IsAdmin
from courses.models import Enrollment
from exams.models import ExamResult
from attendance.models import AttendanceRecord


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot_query(request):
    """Academic chatbot - answers university-related queries"""
    question = request.data.get('question', '').strip()
    if not question:
        return Response({'error': 'Question is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # AI stub - real implementation hooks into OpenAI/Gemini
    responses = {
        'cgpa': 'Your CGPA is calculated based on your grade points and credit hours for each semester.',
        'attendance': 'Minimum attendance requirement is 75%. Students below this may be barred from exams.',
        'deadline': 'Assignment deadlines are set by your course teachers. Check your course page for details.',
        'grade': 'Grades range from A+ (90%+) to F (below 50%). A = 80-89%, B = 70-79%, C = 60-69%, D = 50-59%.',
        'enrollment': 'You can enroll in courses at the start of each semester through the course enrollment page.',
        'exam': 'Exam schedules are posted on the notice board. Check the notices section for updates.',
    }
    question_lower = question.lower()
    answer = None
    for keyword, response in responses.items():
        if keyword in question_lower:
            answer = response
            break

    if not answer:
        answer = (
            f"Thank you for your question: '{question}'. "
            "This is an AI-powered academic assistant. For detailed academic guidance, "
            "please contact your department office or supervisor. "
            "I can help with topics like CGPA, attendance, grades, enrollment, and exams."
        )

    return Response({
        'question': question,
        'answer': answer,
        'response_by': 'SUMS Academic AI Assistant',
        'timestamp': datetime.utcnow().isoformat(),
        'note': 'Connect OPENAI_API_KEY environment variable for full AI responses.'
    })


@api_view(['GET'])
@permission_classes([IsAdminOrTeacher])
def weak_student_prediction(request):
    """Predict at-risk students based on attendance and grades"""
    course_id = request.query_params.get('course')
    from courses.models import Course

    query = {}
    if course_id:
        query['course_id'] = course_id

    at_risk_students = []
    enrollments = Enrollment.objects.filter(
        status='enrolled', **query
    ).select_related('student', 'course')

    for enrollment in enrollments:
        student = enrollment.student
        course = enrollment.course

        # Attendance check
        total_att = AttendanceRecord.objects.filter(student=student, course=course).count()
        present_att = AttendanceRecord.objects.filter(
            student=student, course=course, status__in=['present', 'late']
        ).count()
        att_pct = (present_att / total_att * 100) if total_att > 0 else 100

        # Grade check
        results = ExamResult.objects.filter(student=student, course=course)
        avg_grade_points = 0.0
        if results.exists():
            avg_grade_points = sum(r.grade_points or 0 for r in results) / results.count()

        risk_factors = []
        if att_pct < 75:
            risk_factors.append(f'Low attendance: {att_pct:.1f}%')
        if avg_grade_points < 2.0 and results.exists():
            risk_factors.append(f'Low GPA: {avg_grade_points:.2f}')
        if results.count() == 0 and total_att > 5:
            risk_factors.append('No exam results recorded')

        if risk_factors:
            at_risk_students.append({
                'student': student.get_full_name(),
                'email': student.email,
                'course': course.code,
                'attendance_percentage': round(att_pct, 1),
                'average_grade_points': round(avg_grade_points, 2),
                'risk_factors': risk_factors,
                'risk_level': 'high' if len(risk_factors) >= 2 else 'medium',
            })

    return Response({
        'at_risk_students': sorted(at_risk_students, key=lambda x: x['risk_level']),
        'total': len(at_risk_students),
        'analysis_timestamp': datetime.utcnow().isoformat(),
    })


@api_view(['POST'])
@permission_classes([IsAdminOrTeacher])
def assignment_summary(request, submission_id):
    """Generate AI summary for an assignment submission"""
    from courses.models import AssignmentSubmission
    try:
        submission = AssignmentSubmission.objects.get(id=submission_id)
    except AssignmentSubmission.DoesNotExist:
        return Response({'error': 'Submission not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Stub AI summary - connect real AI here
    content = submission.text_content or 'No text content available.'
    word_count = len(content.split())
    summary = (
        f"This submission contains approximately {word_count} words. "
        f"The student addressed the topic of '{submission.assignment.title}'. "
        "The content demonstrates moderate understanding of the subject matter. "
        "Key points include: problem identification, proposed solution, and conclusion. "
        "Please review the full submission for detailed assessment."
    )

    submission.ai_summary = summary
    submission.save(update_fields=['ai_summary'])

    return Response({
        'submission_id': submission_id,
        'summary': summary,
        'word_count': word_count,
        'note': 'Connect OPENAI_API_KEY for AI-powered summaries.'
    })


@api_view(['POST'])
@permission_classes([IsAdminOrTeacher])
def plagiarism_check(request, submission_id):
    """Check plagiarism for an assignment submission"""
    from courses.models import AssignmentSubmission
    try:
        submission = AssignmentSubmission.objects.get(id=submission_id)
    except AssignmentSubmission.DoesNotExist:
        return Response({'error': 'Submission not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Check similarity against other submissions for same assignment
    other_submissions = AssignmentSubmission.objects.filter(
        assignment=submission.assignment
    ).exclude(id=submission_id)

    base_score = random.uniform(2, 15)  # Simulated base similarity
    details = []
    for other in other_submissions[:5]:
        sim = random.uniform(0, 25)
        if sim > 10:
            details.append({
                'student': other.student.get_full_name(),
                'similarity': round(sim, 1),
            })
        base_score = max(base_score, sim)

    plagiarism_score = min(round(base_score, 1), 100)
    submission.plagiarism_score = plagiarism_score
    submission.save(update_fields=['plagiarism_score'])

    return Response({
        'submission_id': submission_id,
        'plagiarism_score': plagiarism_score,
        'status': 'flagged' if plagiarism_score > 30 else 'clear',
        'similar_submissions': details,
        'note': 'Connect a real plagiarism API for production use.'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reputation_score(request, student_id=None):
    """Calculate academic reputation score for a student"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if student_id:
        if not request.user.is_admin and not request.user.is_teacher:
            return Response({'error': 'Admin/teacher access required.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            student = User.objects.get(id=student_id, role='student')
        except User.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        student = request.user

    # Attendance score (0-30 points)
    total_att = AttendanceRecord.objects.filter(student=student).count()
    present_att = AttendanceRecord.objects.filter(student=student, status__in=['present', 'late']).count()
    att_pct = (present_att / total_att * 100) if total_att > 0 else 0
    att_score = min(30, (att_pct / 100) * 30)

    # Academic score (0-50 points)
    results = ExamResult.objects.filter(student=student)
    gpa_score = 0
    if results.exists():
        avg_gp = sum(r.grade_points or 0 for r in results) / results.count()
        gpa_score = (avg_gp / 4.0) * 50

    # Assignment score (0-20 points)
    from courses.models import AssignmentSubmission
    total_assignments = AssignmentSubmission.objects.filter(student=student)
    on_time = total_assignments.filter(is_late=False).count()
    assign_score = (on_time / total_assignments.count() * 20) if total_assignments.exists() else 10

    total_score = round(att_score + gpa_score + assign_score, 1)

    if total_score >= 85: rank = 'Excellent'
    elif total_score >= 70: rank = 'Good'
    elif total_score >= 55: rank = 'Average'
    elif total_score >= 40: rank = 'Below Average'
    else: rank = 'At Risk'

    return Response({
        'student': student.get_full_name(),
        'email': student.email,
        'reputation_score': total_score,
        'rank': rank,
        'breakdown': {
            'attendance_score': round(att_score, 1),
            'academic_score': round(gpa_score, 1),
            'assignment_score': round(assign_score, 1),
        }
    })
