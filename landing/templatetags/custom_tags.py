from django import template
from social.models import Notification, Post, Comment

register= template.Library()

@register.inclusion_tag('social/show_notifications.html', takes_context=True)
def show_notifications(context):
    request_user=context['request'].user
    notifications= Notification.objects.filter(to_user=request_user).exclude(user_has_seen=True).order_by('-date')
    return {'notifications': notifications}

@register.inclusion_tag('social/comment_modal.html', takes_context=True)
def comment_modal(context):
    post = Post.objects.get(pk=context['post'].pk)
    comments= Comment.objects.filter(post=post)
    return {'post': post,
            'comments': comments,
           }