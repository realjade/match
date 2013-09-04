# -*- coding: utf-8 -*-
from models.admin import Admin, Notice, UserNotice
from models.settings import Feedback, IreadCount
from models.user import User, Passwordreset, MobileCode, UserClass
from models.upload_img import FavImgCreate, FavImg, FavImgUser, FavImgBox, FavImgItem, FavImgComment
from models.upload_video import FavVideoCreate, FavVideo, FavVideoUser, FavVideoBox, FavVideoItem, FavVideoComment
from models.video import Video, IndexVideo
from models.works import Works
from models.task import Task, Taskbox, MultiTask
from models.classgrade import Classgrade, ClassTask, ClassDemand, Demand
from models.school import School
from models.reportcard import ReportCard
from models.favor_img import TeacherFavorImg, TeacherFavorImgLove, TeacherFavorImgComment
from models.favor_video import TeacherFavor, TeacherFavorLove, TeacherFavorComment
#TODO delete start ireadcount 暂时保留
from models.settings import TimeLine, TimeLineEvent
#TODO delete end
