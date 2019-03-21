from django.core.mail import send_mail


def send_emails_to_recipients(notification, subscribed_users):
    to_list = []
    for user in subscribed_users:
        to_list.append(user.user.email)

    subject = notification.title
    body = notification.body
    send_mail(subject, body, 'grootauthors@gmail.com',
              to_list, fail_silently=False)
