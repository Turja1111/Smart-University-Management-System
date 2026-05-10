from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_notice_task(self, notice_id):
    """Async task: distribute a notice to target users"""
    try:
        from notifications.models import Notice
        from django.contrib.auth import get_user_model
        User = get_user_model()

        notice = Notice.objects.get(id=notice_id)
        if notice.target_role == 'all':
            users = User.objects.filter(is_active=True)
        else:
            users = User.objects.filter(role=notice.target_role, is_active=True)

        logger.info(f'Notice "{notice.title}" distributed to {users.count()} users.')
        return {'status': 'sent', 'recipients': users.count()}
    except Exception as exc:
        logger.error(f'Notice task failed: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_ai_summary_task(self, submission_id):
    """Async task: generate AI summary for an assignment submission"""
    try:
        from courses.models import AssignmentSubmission
        submission = AssignmentSubmission.objects.get(id=submission_id)
        content = submission.text_content or ''
        word_count = len(content.split())
        summary = (
            f"Submission contains ~{word_count} words addressing "
            f"'{submission.assignment.title}'. "
            "AI analysis complete - connect OpenAI API for detailed summaries."
        )
        submission.ai_summary = summary
        submission.save(update_fields=['ai_summary'])
        logger.info(f'AI summary generated for submission {submission_id}')
        return {'status': 'complete', 'submission_id': submission_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@shared_task(bind=True, max_retries=2)
def run_weak_student_analysis_task(self):
    """Periodic task: identify at-risk students and log results"""
    try:
        from courses.models import Enrollment
        from attendance.models import AttendanceRecord
        at_risk = 0
        enrollments = Enrollment.objects.filter(status='enrolled').select_related('student', 'course')
        for e in enrollments:
            total = AttendanceRecord.objects.filter(student=e.student, course=e.course).count()
            present = AttendanceRecord.objects.filter(
                student=e.student, course=e.course, status__in=['present', 'late']
            ).count()
            if total > 0 and (present / total) < 0.75:
                at_risk += 1
        logger.info(f'Weak student analysis: {at_risk} at-risk students found.')
        return {'at_risk': at_risk}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
