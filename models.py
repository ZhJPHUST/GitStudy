#coding:utf-8
from __future__ import unicode_literals

#导入django api
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.core.urlresolvers import reverse  ##为模型对象生成URL,直接使用urls.py中的name配置
from uuslug import uuslug

# 导入python api
import datetime, random, time, os, uuid, json

# 导入自定义模型
from aiuser.models import Auser
from classify.models import Subject, Domain, Appcolumn, Acacolumn, Hotcolumn

# 导入自定义设置
from studyai.utils import FlatUUID

# Create your models here.


# 博客模型
@python_2_unicode_compatible
class Ablog(models.Model):
	#基本信息
	uid = models.CharField(u'主键', primary_key=True, auto_created=True, default=FlatUUID, editable=False, max_length=50)
	slug = models.SlugField(u'Slug', unique=True, default=None, max_length=30)
	user = models.OneToOneField(Auser, related_name='myblog', verbose_name=u'用户')
	avatar = models.CharField(u'形象', default='',max_length=200)
	profile = models.CharField(u'简介', null=True, max_length=100)	# 空间简介
	create_date = models.DateField(u'创建时间', auto_now=True)

	#交互信息
	level = models.IntegerField(u'等级', default=1)					# 0:无有  1:小白  2:不错  3:推荐  4:精华
	read_num = models.IntegerField(u'阅读量', default=0)
	comment_num = models.IntegerField(u'评论数', default=0)
	keep_num = models.IntegerField(u'收藏数', default=0)
	poll_num = models.IntegerField(u'点赞数', default=0)
	income 	 = models.FloatField(u'收入', default=0)
	
	#管理信息
	iclassify = models.CharField(u'自定义分类', max_length=1000)
	keep_artical = models.ManyToManyField('Artical',blank=True,verbose_name='收藏博文')

	def __str__(self):
		return self.user.nickname

	def get_absolute_url(self):
		return reverse('xxx',args=self.slug)

	def save(self,*args,**kwargs):
		if self.slug==None: 			#注意，chafield未设default时,会被默认为'',而不是None
			# self.slug = uuslug(self.user.nickname, instance=self, separator='')
			self.slug = self.user.username
		super(Ablog, self).save(*args, **kwargs)

	class Meta:
		verbose_name = u'博客'
		verbose_name_plural = u'博客'
		ordering = ['-read_num']	

# 博客存档表
# 可用于返回某作者博文存档:日期-数量
# 创建更新：创建或删除博文时，调用
# BArchieves.get(blog|pubdate).(delete|update|save).(update_fileds=['pub_date,pub_nums']) 
# 获取：使用串口嵌入博客串口中
@python_2_unicode_compatible
class BArchives(models.Model):
	uid = models.CharField(u'主键', primary_key=True, auto_created=True, default=FlatUUID, editable=False, max_length=50)
	blog = models.ForeignKey(Ablog, null=True, verbose_name=u'博客',related_name='my_archives')	
	pub_date = models.CharField(u'存档日期', null=True, max_length=7) #2016-06
	pub_nums = models.IntegerField(u'存档数量', null=True)
	create_date = models.DateTimeField(u'更新日期', auto_now=True)

	def __str__(self):
		return '{"pub_date":%s,"pub_nums":%d}'%(self.pub_date, self.pub_nums)

	class Meta:
		verbose_name = u'存档'
		verbose_name_plural = u'存档'
		ordering=['-create_date']


# 分类模型
# 通过反向关系挂载到博客下面
# 个人文章也通过反向关系挂载到博客下面
# blog has-a category 关系不一定要写为blog的属性,可以使用反向关联
# unique=True 每个博客只能保存一份自定义分类
@python_2_unicode_compatible
class Category(models.Model):
	uid = models.CharField(u'主键', primary_key=True, auto_created=True, default=FlatUUID, editable=False, max_length=50)
	blog = models.ForeignKey(Ablog, null=True, verbose_name=u'博客',related_name='my_category')
	cats = models.CharField(u'分类', null=True, blank=True, max_length=20) 	
	nums = models.IntegerField(u'数量', null=True, default=0)
	indx = models.IntegerField(u'排序', null=True, default=0)
	show = models.BooleanField(u'显示', default=True) #隐藏则只作者可见
	
	def __str__(self):
		return self.cats

	class Meta:
		verbose_name = u'自定义分类'
		verbose_name_plural = u'自定义分类'
		ordering = ['indx']


# 博文管理器
# 返回全部博文归档日期和数量
class ArticleManager(models.Manager):  
    def distinct_date(self):  
        distinct_date_dict = {}  
        date_lst = self.values('pub_date')  
        for date in date_lst:  
            date = date['pub_date'].strftime("%Y-%m") 
            if date not in distinct_date_dict.keys():
                distinct_date_dict.setdefault(date,1)
            else:
            	distinct_date_dict[date] += 1
        return distinct_date_dict  



# 博文分类
ArticalType = (
	('YC','原创'),
	('ZZ','转载'),
	('FY','翻译'),
	)

# 博文模型
@python_2_unicode_compatible
class Artical(models.Model):
	ArticalTypeChoices=(
		('YC','原创'),
		('ZZ','转载'),
		('FY','翻译'),
		)
	#基本信息
	uid = models.CharField(u'主键', primary_key=True, auto_created=True, default=FlatUUID, editable=False, max_length=50)
	slug = models.SlugField(u'Slug', unique=True, default=None, max_length=30)
	author = models.ForeignKey(Auser, null=True, verbose_name=u'作者')
	blog = models.ForeignKey(Ablog, null=True,verbose_name=u'博客',related_name='my_artical')	
	title = models.CharField(u'标题', max_length=30)
	content = models.TextField(u'内容')
	atype = models.CharField(u'类型', max_length=4, choices=ArticalTypeChoices)   #原创 转载 翻译
	create_date  = models.DateTimeField(u'创建时间', auto_now=True, editable=True)
	pub_date  = models.DateTimeField(u'发布时间', auto_now=True)
	
	iclassify = models.CharField(u'博文归档', max_length=30)  
	# category = models.CharField(u'自定义分类', default=None, max_length=20)  
	# category = models.ForeignKey('Category',verbose_name=u'自定义分类')
	category = models.ManyToManyField('category',verbose_name=u'个人分类')
	totop = models.BooleanField(u'置顶',default=False)

	#交互信息
	level = models.IntegerField(u'等级', default=1)		# 0:草稿 1:待审核 2:已发布  3:推荐  4:精华
	read_num = models.IntegerField(u'阅读量', default=0)
	comment_num = models.IntegerField(u'评论数', default=0)
	keep_num = models.IntegerField(u'收藏数', default=0)
	poll_num = models.IntegerField(u'点赞数', default=0)
	income 	 = models.FloatField(u'收入', default=0)

	#管理信息
	subject = models.ForeignKey(Subject, verbose_name=u'学科')  
	domain  = models.ForeignKey(Domain, verbose_name=u'领域')   
	appcolumn = models.ForeignKey(Appcolumn, verbose_name=u'应用')
	customtags = models.CharField(u'添加标签', max_length=30)	

	objects = ArticleManager()

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('artical_detail',args=[self.slug])		

	def save(self,*args,**kwargs):
		if self.slug==None: 			#注意，chafield未设default时,会被默认为'',而不是None
			self.slug = uuslug(self.title, instance=self, separator='')
		super(Artical, self).save(*args, **kwargs)

	class Meta:
		verbose_name = u'博文'
		verbose_name_plural = u'博文'
		ordering = ['-pub_date']	


# 评论模型
@python_2_unicode_compatible
class BComment(models.Model):
	#基本信息
	uid = models.CharField(u'主键', primary_key=True, auto_created=True, default=FlatUUID, editable=False, max_length=50)
	user  = models.ForeignKey(Auser, verbose_name='评论者')
	artical   = models.ForeignKey(Artical, verbose_name='博文',related_name='comment')
	content = models.TextField(u'评论内容')           
	pub_date= models.DateTimeField(u'评论时间',auto_now=True)

	#交互信息
	reply_num = models.IntegerField(u'回复数',default=0)
	poll_num = models.IntegerField(u'点赞数',default=0)

	#管理信息
	level = models.IntegerField(u'等级',default=1,blank=True,null=True)    

	def __str__(self):
		return self.content.encode('utf-8')

	class Meta:
		verbose_name = u'评论'
		verbose_name_plural = u'评论'
		ordering = ['poll_num']


# 回复模型
@python_2_unicode_compatible
class BReply(models.Model):
	#基本信息	
	uid = models.CharField(u'主键', primary_key=True, auto_created=True, default=FlatUUID, editable=False, max_length=50)
	user = models.ForeignKey(Auser,verbose_name='回复者')       									#关联到用户
	pcomment = models.ForeignKey(BComment, related_name='reply',verbose_name='父评论') 	#关联到评论 回复评论
	preply   = models.ForeignKey('self',related_name='parent_reply',blank=True,null=True,verbose_name='父回复') 	#关联到回复 回复回复

	content = models.CharField(u'R回复内容',max_length=512)
	pub_date= models.DateTimeField(u'回复时间',default = timezone.now)	

	#交互信息
	poll_num = models.IntegerField(u'点赞数',default=0)
	doll_num = models.IntegerField(u'点差数',default=0)

	#管理信息
	level = models.IntegerField(u'等级',default=1,blank=True,null=True)

	def __str__(self):
		return self.content		

	class Meta:
		verbose_name = u'回复'
		verbose_name_plural = u'回复'
		ordering = ['-pub_date']



# 赞踩表 博文点赞 | 评论点赞 | 回复点赞 |举报  
class BPoll(models.Model):
	uid = models.CharField(u'主键', primary_key=True, auto_created=True, default=FlatUUID, editable=False, max_length=50)	
	user = models.ForeignKey(Auser,verbose_name='用户')
	artical = models.ForeignKey(Artical,verbose_name='被点赞博文',blank=True,null=True, on_delete=models.CASCADE)  
	comment = models.ForeignKey(BComment,verbose_name='被点赞评论',blank=True,null=True, on_delete=models.CASCADE)  
	reply  = models.ForeignKey(BReply,verbose_name='被点赞回复',blank=True,null=True, on_delete=models.CASCADE)  
	ptype = models.CharField(u'好评|差评|无感',max_length=64,null=True)  #好评|差评|无感 poll type 	

	def __str__(self):
		return self.user.nickname

	class Meta:
		verbose_name = u'赞踩'
		verbose_name_plural = u'赞踩'


# 收藏表 收藏博文
# 无用了 直接以M2M的方式挂载到blog表下面
class KeepArtical(models.Model):
	uid = models.CharField(u'主键', primary_key=True, auto_created=True, default=FlatUUID, editable=False, max_length=50)	
	user = models.ForeignKey(Auser,verbose_name='用户')
	artical = models.ManyToManyField(Artical,verbose_name='收藏博文',blank=True)

	class Meta:
		verbose_name = u'收藏的博文'
		verbose_name_plural = u'收藏的博文'


# # 计划表 计划科研流程
class MyPlan(models.Model):
	PlanStateChoices = (
		('GKS','刚开始'),
		('JXZ','进行中'),
		('YJS','已结束'),
		('YZZ','已中止'),
		)
	uid = models.CharField(u'主键', primary_key=True, auto_created=True, default=FlatUUID, editable=False, max_length=50)	
	user = models.ForeignKey(Auser, null=True, verbose_name=u'用户')
	blog = models.ForeignKey(Ablog, null=True,verbose_name=u'博客',related_name='my_plan',on_delete=models.CASCADE)	
	title = models.CharField(u'标题', null=True, max_length=30)
	abstract = models.CharField(u'说明', null=True, blank=True, max_length=300)
	start_date  = models.DateField(u'开始时间', default=timezone.now, editable=True)	
	end_date  = models.DateField(u'结束时间', default=timezone.now, editable=True)	
	state = models.CharField(u'状态', max_length=4, choices=PlanStateChoices, default='刚开始')
	isshow = models.BooleanField(u'是否公开', default=False)
	order = models.IntegerField(u'顺序', null=True,default=1)	

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = u'计划'
		verbose_name_plural = u'计划'
		ordering = ['-order','-start_date']


# # 卡片表
class MyCard(models.Model):
	CardStateChoices = (
		('GKS','刚开始'),
		('JXZ','进行中'),
		('YJS','已结束'),
		('YZZ','已中止'),
		)
	uid = models.CharField(u'主键', primary_key=True, auto_created=True, default=FlatUUID, editable=False, max_length=50)
	plan = models.ForeignKey(MyPlan, null=True,verbose_name=u'计划',related_name='my_card',on_delete=models.CASCADE)	
	title = models.CharField(u'标题', null=True, max_length=30)
	abstract = models.CharField(u'说明', null=True, blank=True, max_length=300)
	start_date  = models.DateField(u'开始时间', default=timezone.now, editable=True)	
	end_date  = models.DateField(u'结束时间', default=timezone.now, editable=True)
	state = models.CharField(u'状态', max_length=4, choices=CardStateChoices,default='刚开始')
	order = models.IntegerField(u'顺序', null=True,default=1)	

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = u'计划卡片'
		verbose_name_plural = u'计划卡片'
		ordering = ['order']	

# 条目表
class MyItem(models.Model):
	ItemStateChoices = (
		('GKS','刚开始'),
		('JXZ','进行中'),
		('YJS','已结束'),
		('YZZ','已中止'),
		)
	uid = models.CharField(u'主键', primary_key=True, auto_created=True, default=FlatUUID, editable=False, max_length=50)
	card = models.ForeignKey(MyCard, null=True,verbose_name=u'卡片',related_name='my_item',on_delete=models.CASCADE)	
	title = models.CharField(u'标题', null=True,max_length=500)
	content = models.CharField(u'内容',null=True, blank=True, max_length=300)  #下拉toggle显示
	order = models.IntegerField(u'顺序', null=True, default=1)	
	state = models.CharField(u'状态', max_length=4, choices=ItemStateChoices,default='刚开始')

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = u'卡片明细'
		verbose_name_plural = u'卡片明细'
		ordering = ['order']


# # 知识树 构建知识体系
# class KnowledgeTree(models.Model):
# 	pass


# # 配置表 构建个人博客风格
# class IClassify(models.Model):
# 	pass


# # 配置表 构建个人博客风格
# class Configure(models.Model):
# 	pass