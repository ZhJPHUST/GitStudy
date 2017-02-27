# -*- coding: utf-8 -*-
__author__ = 'ooo'
__date__ = '2017/1/22 22:22'


import xadmin

from .models import Article, Ablog, BlogUpDown, BComment, BReply, Category, \
                    MyPlan, MyCard, MyItem


class AblogAdmin(object):
    list_display = ['user','slug','avatar','intro']
    filter_fields = ['user','slug','avatar','intro']
    search_fields = ['user','slug','avatar','intro']
    model_icon = 'fa fa-github-alt'
    exclude = ('read_num','poll_num','keep_num','income')


class CategoryAdmin(object):
    list_display = ['blog','cats','nums','indx','show']
    filter_fields = ['blog','cats','nums','indx','show']
    search_fields = ['blog','cats','nums','indx','show']


class ArticalAdmin(object):
    list_display = ['title','user','pub_date']
    filter_fields = ['title','user']
    search_fields = ['title','user']
    exclude = ('read_num','poll_num','comment_num','keep_num','income')


class BCommentAdmin(object):
    list_display = ['user','article','content']
    filter_fields = ['user','article','content']
    search_fields = ['user','article','content']


class BReplyAdmin(object):
    list_display = ['user','pcomment','preply','content']
    filter_fields = ['user','pcomment','preply','content']
    search_fields = ['user','pcomment','preply','content']


class BlogUpDownAdmin(object):
    list_display = ['user','ptype','article','comment','reply']
    filter_fields = ['user''ptype','article','comment','reply']
    search_fields = ['user''ptype','article','comment','reply']


xadmin.site.register(Ablog, AblogAdmin)
xadmin.site.register(Article, ArticalAdmin)
xadmin.site.register(Category, CategoryAdmin)
xadmin.site.register(BComment, BCommentAdmin)
xadmin.site.register(BReply, BReplyAdmin)
xadmin.site.register(BlogUpDown, BlogUpDownAdmin)

class MyPlanAdmin(object):
    list_display = ['user','blog','title','state','order']
    filter_fields = ['user','blog','title','state','order']
    search_fields = ['user','blog','title','state','order']


class MyCardAdmin(object):
    list_display = ['plan','title','order']
    filter_fields = ['plan','title','order']
    search_fields = ['plan','title','order']


class MyItemAdmin(object):
    list_display = ['card','title','order']
    filter_fields = ['card','title','order']
    search_fields = ['card','title','order']


xadmin.site.register(MyPlan, MyPlanAdmin)
xadmin.site.register(MyCard, MyCardAdmin)
xadmin.site.register(MyItem, MyItemAdmin)