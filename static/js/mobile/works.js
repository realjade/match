//初始化视频
jQuery(function(){
    $('.beishuPlayer').each(function(){
        load_videoplayer($(this).attr('id'));
    });
});
//初始化图片
jQuery(function(){
    $('.taskimage').live('click',function(){
        var self = $(this);
        var img = new ImageShow({
            works_id:$(this).parents('.work-item').attr('data-words_id'),
            child_id:$(this).parents('.work-item').attr('data-child_id'),
            thumbnails:JSON.parse($(this).attr('data-thumbnail_path')),
            pathes:JSON.parse($(this).attr('data-image_path')),
            removed:function(data){
                self.attr('data-thumbnail_path',JSON.stringify(data.thumbnail_path));
                self.attr('data-image_path',JSON.stringify(data.image_path));
            }
        });
    });
});
//作业推荐
jQuery(function() {
    $('.work-item').on('click','.work-favor',function(){
         var target = $(this).parents('.work-item');
         var works_id = target.attr('data-words_id');
         jQuery.ajax({
            url: '/favor/add/',
            data: {'works_id':works_id},
            type: "POST",
            dataType: 'json',
            beforeSend: function(){
                smallnote('正在推荐...');
                return true;
            },
            success: function(response) {
                if(response.code=='0') {
                    smallnote('推荐成功');
                    target.find('.task-result-favor').show();
                    target.find('.work-favor').hide();
                    target.shrink($('.nav-favor'));
                }
            },
            error: function() {
                smallnote('推荐失败');
            }
        });
    });
});
//作业批改
jQuery(function() {
    //点击批改作业按钮效果
    $('.work-item').on('click','.work-correct',function(){
        var target = $(this).parents('.work-item'),
            ele = $(this),
            correctpanel = target.find('.work-correct-panel');
        if(ele.hasClass('active')){
            ele.removeClass('active');
            ele.find('span').text('老师批改');
            correctpanel.slideUp();
        }else{
            ele.addClass('active');
            ele.find('span').text('正在批改');
            correctpanel.slideDown();
        }
    });
    //批改作业面板效果
    //批改建议点击
    $('.work-item .work-correct-panel .comment-suggest').on('click','li',function(){
        var target = $(this).parents('.work-item'),
            ele = $(this),
            correctpanel = target.find('.work-correct-panel');
        correctpanel.find('.comment-content').val(ele.text());
        correctpanel.find('.comment-content').siblings('label').hide();
    });
    //点击推荐按钮
    $('.work-item .work-correct-panel .correct-favor').on('click','span',function(){
        var checkedinput = $(this).siblings('input[name=correct-favor]');
        if(!checkedinput.attr('checked')){
            checkedinput.attr('checked','checked');
        }else{
            checkedinput.removeAttr('checked');
        }
    });
    //点击清空按钮
    $('.work-item .work-correct-panel').on('click','.correct-clear',function(){
        var target = $(this).parents('.work-item');
        target.find('.comment-content').val('');
    });
    //点击批改按钮
    $('.work-item .work-correct-panel').on('click','.correct-ok',function(){
        var target = $(this).parents('.work-item'),
            ele = $(this),
            correctpanel = target.find('.work-correct-panel'),
            works_id = target.attr('data-words_id'),
            star = correctpanel.find('.work_star').attr('data-star'),
            content = correctpanel.find('.comment-content').val(),
            redo = Boolean(correctpanel.find('input[name=redo]').attr("checked"))?1:0;
        
        jQuery.ajax({
            url: '/correct/',
            data: {'works_id':works_id,'star':star,'comment':content,'redo':redo},
            type: "POST",
            dataType: 'json',
            beforeSend: function(){
                smallnote('正在批改...');
                return true;
            },
            success: function(response) {
                if(response.code=='0') {
                    smallnote('批改成功');
                    target.fadeOut(function(){
                        target.remove();
                        var size = $('.work-item').size();
                        if(size == 0 || size == 1){
                            window.location.reload();
                        }
                    });
                }
            },
            error: function() {
                smallnote('批改失败');
            }
        });
    });
});

//作业点评
jQuery(function() {
    //点击点评作业按钮效果
    $('.work-item .work-approval').live('click',function(){
        var target = $(this).parents('.work-item'),
            ele = $(this),
            approvalpanel = target.find('.work-approval-panel');
        if(ele.hasClass('active')){
            ele.removeClass('active');
            approvalpanel.slideUp();
        }else{
            ele.addClass('active');
            approvalpanel.slideDown();
        }
    });
    //点评作业面板效果
    //点评建议点击
    $('.work-item .work-approval-panel .comment-suggest li').live('click',function(){
        var target = $(this).parents('.work-item'),
            ele = $(this),
            correctpanel = target.find('.work-approval-panel');
        correctpanel.find('.comment-content').val(ele.text());
        correctpanel.find('.comment-content').siblings('label').hide();
    });
    //点击清空按钮
    $('.work-item .work-approval-panel .approval-clear').live('click',function(){
        var target = $(this).parents('.work-item');
        target.find('.comment-content').val('');
    });
    //点击点评按钮
    $('.work-item .work-approval-panel .approval-ok').live('click',function(){
        var target = $(this).parents('.work-item'),
            ele = $(this),
            approvalpanel = target.find('.work-approval-panel'),
            works_id = target.attr('data-words_id'),
            comment = approvalpanel.find('.comment-content').val();
        jQuery.ajax({
            url: '/approval/',
            data: {'works_id':works_id,'comment':comment},
            type: "POST",
            dataType: 'json',
            beforeSend: function(){
                smallnote('正在点评...');
                return true;
            },
            success: function(response) {
                if(response.code=='0') {
                    smallnote('点评成功');
                    approvalpanel.slideUp();
                    var approvalresult = target.find('.task-result-approval'),
                        baseinfo = target.find('.task-deadline-info');
                    if(approvalresult.size()==0){
                        var temp = $('<div class="task-result-approval task-result">家长评语：'+comment+'</div>');
                        temp.insertAfter(baseinfo);
                    }else{
                        approvalresult.text('家长评语：'+comment);
                    }
                    target.find('.work-approval').removeClass('active');
                }
            },
            error: function() {
                smallnote('点评失败');
            }
        });
    });
});
//作业上传
jQuery(function() {
    var videoupload = $('#videoupload');
    videoupload.uploader({
        filters:[
                {
                    title : "视频文件", extensions : "avi,flv,f4v,mp4,m4v,mkv,mov,3gp,3gp,3g2,mpg,wmv,ts"
                }
            ],
        max_file_count:1,
        multi_selection:false,
        uploadsuccess:uploadsuccess});
    var imageupload = $('#imageupload');
    imageupload.uploader({
        filters:[
                {
                    title : "图片文件", extensions : "png,jpg,jpeg,gif"
                }
            ],
        multi_selection:true,
        uploadsuccess:uploadsuccess});
    //var videolibrary = $('#videolibrary');
    //点击作业上传按钮效果
    var beforeele = null;
    $('.work-item .work-upload').live('click',function(){
        var target = $(this).parents('.work-item'),
            ele = $(this);
        //隐藏从视频库提交
        //$('.work-item .work-videolibrary').removeClass('active');
        //videolibrary.hide();
        var isvideo = target.attr('data-task_type') == '1';
        if(!isvideo){
            //图片作业
            imageupload.find('input[name=task_id]').val(target.attr('data-task_id'));
            imageupload.find('input[name=child_id]').val(target.attr('data-child_id'));
            imageupload.uploadparams();
            imageupload.uploadrefresh();
        }
        if(isvideo){
            //视频作业
            videoupload.find('input[name=task_id]').val(target.attr('data-task_id'));
            videoupload.find('input[name=child_id]').val(target.attr('data-child_id'));
            videoupload.uploadparams();
            videoupload.uploadrefresh();
        }
        
        if(ele.hasClass('active')){
            ele.removeClass('active');
            videoupload.css('left','-10000px');
            imageupload.css('left','-10000px');
        }else{
            $('.work-item .work-upload').removeClass('active');
            ele.addClass('active');
            if(isvideo){
                videoupload.css({'top':ele.offset().top+15,'left':ele.offset().left-videoupload.width()+100});
                videoupload.show();
                imageupload.hide();
            }else{
                imageupload.css({'top':ele.offset().top+15,'left':ele.offset().left-imageupload.width()+100});
                imageupload.show();
                videoupload.hide();
            }
            
        }
        beforeele = ele;
    });
    function uploadsuccess(res){
        if(!res.data.video_id){
            if(imageupload.uploaderalldone()){
                window.location.reload();
            }
        }else{
            smallnote('请将视频旋转至正确的角度');
            videoupload.css('left','-10000px');
            $('.work-item .work-upload').removeClass('active');
            var imgrotate = new ImageRotate({
                imgpath:res.data.thumbnail_path,
                success:function(){
                    var self = this;
                    var rotate = (self.rotate%360+360)%360;
                    jQuery.ajax({
                        url: '/upload/video/transpose/',
                        data: {'rotate':rotate,'video_id':res.data.video_id,'thumbnail_path':res.data.thumbnail_path,'savepath':res.data.savepath},
                        type: "POST",
                        dataType: 'json',
                        success: function(response) {
                            if(response.code=='0') {
                                var timer = setInterval(function(){
                                    jQuery.ajax({
                                        url: '/video/get/',
                                        data: {'video_id':res.data.video_id},
                                        type: "POST",
                                        dataType: 'json',
                                        success: function(response) {
                                            if(response.code=='0'&&response.data.isfinished) {
                                                imgrotate.close();
                                                window.location.reload();
                                            }
                                        }
                                    });
                                },3000);
                            }
                        }
                    });
                }
            });
        }
        
    }
});