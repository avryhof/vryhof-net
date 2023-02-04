from huey.contrib.djhuey import task

from utilities.email_helpers import send_multipart_email


@task()
def email_user(user, subject, message, from_email=None, **kwargs):
    """Send an email to user."""
    return send_multipart_email(subject, message, from_email, [user.email], **kwargs)
