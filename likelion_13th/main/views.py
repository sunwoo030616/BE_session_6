from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
import re
from .models import *

# Create your views here.

def mainpage(request):
    context = {
        'generation': 13,
        'info': {'weather': '좋음', 'feeling': '배고픔(?)', 'note': '아기사자 화이팅!'},
        'shortKeys': [
        '들여쓰기: Tab',
        '내어쓰기: Shift + Tab',
        '주석 처리: 윈도우- Ctrl + /, 맥- command + /',
        '자동 정렬: Shift + Alt + F or Ctrl + K + F',
        '한 줄 이동: Alt + 방향키(위/아래)',
        '한 줄 삭제: Ctrl + Shift + k or Ctrl + x',
        '같은 단어 전체 선택: Ctrl + Shift + L'
        ]
    }
    return render(request, 'main/mainpage.html', context)

def secondpage(request):
    blogs = Blog.objects.all()
    return render(request, 'main/secondpage.html', {'blogs': blogs})

def new_blog(request):
    return render(request, 'main/new-blog.html')

def detail(request, id):
    blog = get_object_or_404(Blog, pk=id)
    if request.method == 'GET':
        comments = Comment.objects.filter(blog=blog)
        return render(request, 'main/detail.html', {'blog':blog, 'comments': comments})

    elif request.method == 'POST':
        new_comment = Comment()
        new_comment.blog = blog
        new_comment.writer=request.user
        new_comment.content = request.POST['content']
        new_comment.pub_date = timezone.now()
        new_comment.save()
        return redirect('main:detail', id)
    
def edit(request, id):
    edit_blog=Blog.objects.get(pk=id)
    return render(request, 'main/edit.html', {"blog": edit_blog})

def create(request):
    if request.user.is_authenticated:
        new_blog = Blog()

        new_blog.title = request.POST['title']
        new_blog.writer = request.user
        new_blog.content = request.POST['content']
        new_blog.pub_date = timezone.now()
        new_blog.image = request.FILES.get('image')
        new_blog.save()

        #본문을 띄어쓰기 기준으로 나누기
        words = new_blog.content.split(' ')
        tag_list = []

        # 나눈 단어가 '#'으로 시작한다면 tag_list에 저장
        for w in words:
            if len(w)>0:
                if w[0] == '#':
                    tag_list.append(w[1:])
        
        #tag_list에 있는 Tag들을 new_blog의 tags에 추가
        for t in tag_list:
            tag, boolean = Tag.objects.get_or_create(name=t)
            new_blog.tags.add(tag.id)

        return redirect('main:detail', new_blog.id)
    else:
        return redirect('accounts:login')

def update(request, id):
    update_blog = Blog.objects.get(pk=id)
    if request.user.is_authenticated and request.user == update_blog.writer:
        update_blog.title = request.POST['title']
        update_blog.content = request.POST['content']
        update_blog.pub_date = timezone.now()
        if request.FILES.get('image'):
            update_blog.image = request.FILES['image']

        update_blog.save()
        return redirect('main:detail', update_blog.id)
    return redirect('accounts:login', update_blog.id)

def delete(request, id):
    delete_blog = Blog.objects.get(pk=id)
    delete_blog.delete()
    return redirect('main:secondpage')

def tag_list(request): #모든 태그 목록을 볼 수 있는 페이지
    tags = Tag.objects.all()
    return render(request, 'main/tag-list.html', {'tags': tags})

def tag_blogs(request, tag_id): #특정 태그를 가진 게시글의 목록을 볼 수 있는 페이지
    tag=get_object_or_404(Tag, id=tag_id)
    blogs=tag.blogs.all()
    return render(request, 'main/tag-blog.html', {
        'tag' : tag,
        'blogs' : blogs
    })

def likes(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.user in blog.like.all():
        blog.like.remove(request.user)
        blog.like_count-=1
        blog.save()
    else:
        blog.like.add(request.user)
        blog.like_count+=1
        blog.save()
    return redirect('main:detail', blog.id)



