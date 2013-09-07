# -*- coding: utf-8 -*-

VIDEO_PROCESS_ERROR = (1000, u'视频在处理过程中出错，请重新上传后者重新编码后上传')

INVALID_GET = (2000,u'不支持GET方法')
INVALID_POST = (2001,u'不支持GPOST方法')
INVALID_PARAMS = (2002,u'参数不正确')
INVALID_PASSWORD = (2003,u'密码不正确')
INVALID_TWICEPASS = (2004,u'两次密码不一样')
INVALID_EMAIL = (2005,u'邮箱不合法')
INVALID_MOBILE = (2006,u'手机号不合法')
INVALID_MOBILE_CODE = (2007,u'手机验证码错误或者失效')
INVALID_MOBILE_SEND = (2008,u'手机验证码发送失败')
INVALID_Failed = (2009,u'操作失败')


ACCOUNT_EXIST = (3000,u'该账户已经存在')
ACCOUNT_NOT_EXIST = (3001,u'该账户不存在')
ACCOUNT_EMAIL_EXIST = (3002,u'邮箱已经存在')
ACCOUNT_MOBILE_EXIST = (3003,u'手机号已经存在')
ACCOUNT_NOT_STUDENT = (3004,u'该账户不是学生账户')
ACCOUNT_NOT_PARENT = (3005,u'该账户不是家长账户')
ACCOUNT_NOT_TEACHER = (3006,u'该账户不是老师账户')
ACCOUNT_HAS_PARENT = (3007,u'该账户已经有其他家长')

SCHOOL_EXIST = (4000,u'学校名称已经存在')
SCHOOL_NOT_EXIST = (4001,u'学校不存在')

HANDIN_EXIST = (5000,u'该作业已经提交')
HANDIN_NOT_EXIST = (5001,u'没有该作业的提交信息')
HANDIN_NOT_YOURCHILD = (5002,u'不能给其他孩子交作业')
HANDIN_NOT_YOURS = (5002,u'你不能批改该作业')

HOMEWORK_EXIST = (6000,u'该作业已经存在')
HOMEWORK_NOT_EXIST = (6001,u'该作业不存在')
HOMEWORK_OUTDAY = (6002,u'该作业已过期')
HOMEWORK_HASAPPROVAL = (6003,u'该作业家长已经点评过')
HOMEWORK_HASCORRECT = (6003,u'该作业老师已经批改过')

VIDEO_NOT_SUPPORT = (7000,u'不支持的视频格式')
AVATAR_NOT_SUPPORT = (7001,u'不支持的图片格式')
VIDEO_NOT_EXIST = (7002,u'视频不存在')
VIDEO_CAN_NOT_REMOVE = (7003,u'视频已经在使用中，不能被删除')
VIDEO_UPLOAD_FAIL = (7004,u'视频上传失败')
UPLOAD_FAIL = (7005,u'上传失败')
FILE_EXIST = (7006,U'文件不存在')
IMAGE_NOT_SUPPORT = (7007,u'不支持的图片格式')

APPROVAL_EXIST = (8000,u'该作业已经提交')
APPROVAL_NOT_EXIST = (8001,u'没有该作业的提交信息')
APPROVAL_NOT_YOURCHILD = (8002,u'不能给其他孩子审批')

