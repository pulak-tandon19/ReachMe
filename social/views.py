from django.shortcuts import render, redirect
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from .models import Post, Comment, UserProfile, Notification, ThreadModel, MessageModel, Image, Tag
from .forms import PostForm, CommentForm, CommentReplyForm, ThreadForm, MessageForm, ShareForm, ExploreForm
from django.views.generic.edit import UpdateView, DeleteView 
# from rest_framework.views import APIView


# Create your views here.

class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logged_in_user=request.user
        posts=Post.objects.filter(
            author__profile__followers__in=[logged_in_user.id]
        )
        form=PostForm()
        share_form= ShareForm()
        context={
            'post_list': posts,
            'form':form,
            'shareform': share_form,
        }

        return render(request, 'social/post_list.html', context)

    def post(self, request, *args, **kwargs):
        logged_in_user=request.user
        posts=Post.objects.filter(
            author__profile__followers__in=[logged_in_user.id]
        )
        # form=PostForm(request.POST, request.FILES)
        share_form= ShareForm()
        # files= request.FILES.getlist('image')
        body = self.request.POST.get('create-post')
        new_post = Post.objects.create(body= body, author= request.user)
        new_post.create_tags()

        # if form.is_valid:
        #     new_post = form.save(commit=False)
        #     new_post.author=request.user
        #     new_post.save()

        #     new_post.create_tags()

        #     for f in files:
        #         img=Image(image=f)
        #         img.save()
        #         new_post.image.add(img)

        #     new_post.save()
        
        context={
            'post_list': posts,
            # 'form':form,
            'shareform': share_form,
        }

        return render(request, 'social/post_list.html', context)


class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post=Post.objects.get(pk=pk)
        form= CommentForm()
        form1= CommentReplyForm()
        comments= Comment.objects.filter(post=post, comment_level=1)

        context={
            'post':post,
            'form':form,
            'comments':comments,
            'form1': form1,
        }

        return render(request, 'social/post_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        post=Post.objects.get(pk=pk)
        # form= CommentForm(request.POST)
        comment= request.POST.get('post-comment')

        # if form.is_valid():
        #     new_comment= form.save(commit=False)
        #     new_comment.author=request.user
        #     new_comment.post=post
        #     new_comment.comment_level=1
        #     new_comment.save()

        #     new_comment.create_tags()
        new_comment = Comment.objects.create(comment=comment, author= request.user, post= post, comment_level=1)

        comments= Comment.objects.filter(post=post, comment_level=1).order_by('-created_on')
        notification= Notification.objects.create(notification_type=2, from_user=request.user, to_user=post.author, post=post)


        context={
            'post':post,
            # 'form':form,
            'comments':comments,
        }

        return render(request, 'social/post_detail.html', context)



class PostEditView(LoginRequiredMixin,View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        context = {
            'post': post
        }
        return render(request, 'social/post_edit.html', context)

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        comments = Comment.objects.filter(post = post)
        if post.author == self.request.user:
            body= self.request.POST.get('body')
            post.body= body
            post.save()
            context= {
                'post': post,
                'commments' : comments,
            }
            return redirect('post-detail', pk= post.pk)
        return HttpResponse("Not Allowed")
    

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model= Post
    template_name='social/post_delete.html'
    success_url= reverse_lazy('post-list')

    def test_func(self):
        post= self.get_object()
        return self.request.user==post.author

class CommentEditView(LoginRequiredMixin, View):
    def get(self, request, post_pk,pk,cl=1,*args, **kwargs):
        post = Post.objects.get(pk=post_pk)
        comment = Comment.objects.get(post = post, pk=pk, comment_level=cl)
        context = {
            'post': post,
            'comment': comment,
        }
        return render(request, 'social/comment_edit.html', context)

    def post(self, request, post_pk,pk,cl=1, *args, **kwargs):
        post = Post.objects.get(pk=post_pk)
        comment = Comment.objects.get(post = post, comment_level=cl, pk=pk)
        if comment.author == self.request.user:
            body= self.request.POST.get('body')
            comment.comment= body
            comment.save()
            if cl==1:
                return redirect('post-detail', pk= post.pk)
            return redirect('comment-reply', post_pk=post_pk, pk=pk, comment_level=cl)
        return HttpResponse("Not Allowed")

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name='social/comment_delete.html'

    def get_success_url(self):
        pk=self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    def test_func(self):
        post= self.get_object()
        return self.request.user==post.author


class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile=UserProfile.objects.get(pk=pk)
        user=profile.user
        posts=Post.objects.filter(author=user)
        followers=profile.followers.all()
        number_of_followers=len(followers)

        if len(followers) == 0:
            is_following=False

        for follower in followers:
            if follower==request.user:
                is_following=True
            else:
                is_following=False
              

        context={
            'profile': profile,
            'user': user,
            'posts': posts,
            'number_of_followers':number_of_followers,
            'is_following': is_following,
        }

        return render(request, 'social/profile.html', context)

class CommentReplyView(LoginRequiredMixin, View): 
    def get(self, request, post_pk, pk, comment_level, *args, **kwargs):
        post=Post.objects.get(pk=post_pk)
        parent_comment=Comment.objects.get(comment_level=comment_level, pk=pk)
        replies= parent_comment.replies.filter(comment_level=comment_level+1).order_by('-created_on')
        form=CommentReplyForm()

        context={
            'post' : post,
            'parent_comment':parent_comment,
            'form': form,
            'replies': replies,
        }
        
        return render(request, 'social/comment_replies.html', context)

    def post(self, request, post_pk, pk, comment_level, *args, **kwargs):
        post=Post.objects.get(pk=post_pk)
        parent_comment=Comment.objects.get(comment_level=comment_level, pk=pk)
        # form=CommentReplyForm(request.POST)

        comment= self.request.POST.get('create-comment-reply')
        new_comment = Comment.objects.create(comment = comment,
        author=request.user,
        post=post,
        parent=parent_comment,
        comment_level=(comment_level+1))
    
        parent_comment.replies.add(new_comment)

        notification= Notification.objects.create(notification_type=2, from_user=request.user, to_user=parent_comment.author, comment=new_comment)
 
        return redirect('comment-reply', post_pk=post_pk, comment_level=comment_level, pk=pk)



class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model=UserProfile
    fields=['name', 'bio', 'birth_date', 'location', 'picture']
    template_name='social/profile_edit.html'

    def get_success_url(self):
        pk=self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})
    
    def test_func(self):
        profile= self.get_object()
        return self.request.user==profile.user

class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile=UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)

        notification= Notification.objects.create(notification_type=3, from_user=request.user, to_user=profile.user)

        return redirect('profile', pk=pk)

class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile=UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)

        return redirect('profile', pk=pk)


class AddLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post=Post.objects.get(pk=pk)

        is_dislike=False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike=True
                break

        if is_dislike:
            post.dislikes.remove(request.user)

        is_like= False

        for like in post.likes.all():
            if like == request.user:
                is_like=True
                break
        
        if not is_like:
            post.likes.add(request.user)
            notification= Notification.objects.create(notification_type=1, from_user=request.user, to_user=post.author, post=post)
        else:
            post.likes.remove(request.user)

        next=request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddDislike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post=Post.objects.get(pk=pk)

        is_like= False

        for like in post.likes.all():
            if like == request.user:
                is_like=True
                break

        if is_like:
            post.likes.remove(request.user)

        is_dislike=False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike=True
                break
        
        if not is_dislike:
            post.dislikes.add(request.user)
        else:
            post.dislikes.remove(request.user)

        next=request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddCommentLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        comment=Comment.objects.get(pk=pk)

        is_dislike=False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike=True
                break

        if is_dislike:
            comment.dislikes.remove(request.user)

        is_like= False

        for like in comment.likes.all():
            if like == request.user:
                is_like=True
                break
        
        if not is_like:
            comment.likes.add(request.user)
            notification= Notification.objects.create(notification_type=1, from_user=request.user, to_user=comment.author, comment=comment)
        else:
            comment.likes.remove(request.user)

        next=request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddCommentDislike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        comment=Comment.objects.get(pk=pk)

        is_like= False

        for like in comment.likes.all():
            if like == request.user:
                is_like=True
                break

        if is_like:
            comment.likes.remove(request.user)

        is_dislike=False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike=True
                break
        
        if not is_dislike:
            comment.dislikes.add(request.user)
        else:
            comment.dislikes.remove(request.user)

        next=request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class SharedPostView(View):
    def post(self, request, pk, *args, **kwargs):
        original_post= Post.objects.get(pk=pk)
        form = ShareForm(request.POST)

        if form.is_valid():
            new_post= Post(
                shared_body= self.request.POST.get('body'),
                author= original_post.author,
                body=original_post.body,
                created_on= original_post.created_on,
                shared_user= request.user,
                shared_on= timezone.now()
                
            )

            new_post.save()

            for img in original_post.image.all():
                new_post.image.add(img)
            new_post.save()
        
        return redirect('post-list')

class UserSearch(View):
    def get(self, request, *args, **kwargs):
        query=self.request.GET.get('query')
        profile_list=UserProfile.objects.filter(Q(user__username__icontains=query))

        context={
            'profile_list': profile_list
        }

        return render(request, 'social/search.html', context)

class ListFollowers(View):
    def get(self, request, pk, *args, **kwargs):
        profile=UserProfile.objects.get(pk=pk)
        followers=profile.followers.all()

        context={
            'profile': profile,
            'followers': followers,
        }

        return render(request, 'social/followers_list.html', context)

class PostNotification(View):
    #also handles comment related request
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notification= Notification.objects.get(pk=notification_pk)
        post=Post.objects.get(pk=post_pk)

        notification.user_has_seen= True
        notification.save()

        return redirect('post-detail', pk=post_pk)

class FollowNotification(View):
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notification= Notification.objects.get(pk=notification_pk)
        profile=UserProfile.objects.get(pk=profile_pk)

        notification.user_has_seen= True
        notification.save()

        return redirect('profile', pk=profile_pk)

class ThreadNotification(View):
    def get(self, request, notification_pk, object_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        thread= ThreadModel.objects.get(pk=object_pk)
        
        notification.user_has_seen = True
        notification.save()

        return redirect('thread', pk=object_pk)

class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        notification= Notification.objects.get(pk=notification_pk)
        notification.user_has_seen= True
        notification.save()

        return HttpResponse('Success', content_type='text/plain')

class ClearNotifications(View):
    def delete(self, request, *args,**kwargs):
        notifications= Notification.objects.filter(to_user= request.user)
        for i in notifications:
            i.user_has_seen= True
            i.save()

        return HttpResponse('Success', content_type='text/plain')

        

class ListThreads(View):
    def get(self, request, *args, **kwargs):
        threads= ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))

        context={
            'threads' : threads
        }

        return render(request, 'social/inbox.html', context)


class CreateThread(View):
    def get(self, request, *args, **kwargs):
        form= ThreadForm()

        context= {
            'form':form
        }

        return render(request, 'social/create_thread.html', context)

    def post(self, request, *args, **kwargs):
        # form=ThreadForm(request.POST)
        username= request.POST.get('username')

        try:
            receiver=User.objects.get(username=username)
            if ThreadModel.objects.filter(user=request.user, receiver=receiver).exists():
                thread= ThreadModel.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('thread', pk=thread.pk)
            elif ThreadModel.objects.filter(user=receiver, receiver=request.user).exists():
                thread= ThreadModel.objects.filter(user=receiver, receiver=request.user)[0]
                return redirect('thread', pk=thread.pk)

            # if form.is_valid():
            thread= ThreadModel(user=request.user, receiver=receiver)
            thread.save()
            return redirect('thread', thread.pk)
        except:
            messages.error(request, 'Invalid Username')
            return redirect('create-thread')

class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form=MessageForm()
        thread= ThreadModel.objects.get(pk=pk)
        message_list= MessageModel.objects.filter(thread__pk__contains=pk)
        context={
            'thread': thread,
            'form': form,
            'message_list': message_list,
        }

        return render(request, 'social/thread1.html', context)

class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        # form= MessageForm(request.POST, request.FILES)
        body = self.request.POST.get('create-message')
        thread= ThreadModel.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver=thread.user
        else:
            receiver=thread.receiver

        message = MessageModel.objects.create(body=body)
        message.thread=thread
        message.sender_user=request.user
        message.receiver_user=receiver
        message.save()


        

        notification = Notification.objects.create(
            notification_type= 4, 
            from_user= request.user,
            to_user= receiver, 
            thread= thread,
        )

        return redirect('thread', pk=pk)


class Explore(View):
    def get(self, request, *args, **kwargs):
        # explore_form= ExploreForm()
        query= self.request.GET.get('query')
        tag= Tag.objects.filter(name= query).first()

        if tag:
            posts= Post.objects.filter(tags__in=[tag])
        else:
            posts= Post.objects.all()
            # posts = None

        context={
            'tag': tag,
            'posts': posts,
            # 'explore_form': explore_form,
        }

        return render(request, 'social/explore.html', context)


    def post(self, request, *args, **kwargs):
        # explore_form = ExploreForm(request.POST)
        # if explore_form.is_valid():
        query= self.request.POST.get('query')
        tag = Tag.objects.filter(name= query).first()

        posts= None

        if tag:
            posts= Post.objects.filter(tags__in=[tag])

        if posts:
            context={
                    'tag': tag,
                    'posts': posts,
                }
        else:
            context={
                    'tag': tag,
                }
        
        # return render(request, 'social/explore.html', context)
        return HttpResponseRedirect(f'/social/explore?query={query}')
        # return HttpResponseRedirect('/social/explore')






        



        
