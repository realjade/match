//初始化视频播放
jQuery(function() {
    var loop = 1;
    $('.beishuPlayer').each(function(){
        $(this).attr('id','beishuPlayer'+loop);
        load_videoplayer($(this).attr('id'));
        loop++;
    });
});

//获得新的timeline个数
jQuery(function() {
    if(timeline_starttime){
        var timer = setInterval("getTimelineNewCount()", 60*1000);
    }
    function getTimelineNewCount(){
        jQuery.ajax({
            url: '/timeline/update/'+timeline_starttime+'/',
            type: "POST",
            dataType: 'json',
            success: function(response) {
                if(response.code=='0') {
                    if(response.data.count>0){
                        $('#timeline_newcount').find('.newcount').html(response.data.count);
                        $('#timeline_newcount').show();
                    }else{
                        $('#timeline_newcount').hide();
                    }
                }
            }
        });
    }
    window.getTimelineNewCount=getTimelineNewCount;
});

//批改作业
jQuery(function() {
    $('.pubinfo').on('click','.correct',function(){
        var correctinfo =$(this).parents('.pubinfo').siblings('.correctinfo');
        correctinfo.slideDown('fast');
    });
    $('.comment-suggest').on('click','li',function(){
        $(this).parents('.workcomment').find('textarea[name=comment]').val($(this).text());
    });
    if(jQuery('.correctinfo').attr('data-type')=='correct'){
        $('.correctbtn').click(correct);
    }else{
        $('.correctbtn').click(approval);
    }
    function correct(){
        var correctinfo = $(this).parents('.correctinfo');
        var star = correctinfo.find('.star').attr('data-star');
        var works_id = correctinfo.attr('data-hdid');
        var comment = correctinfo.find('textarea[name=comment]').val();
        jQuery.ajax({
            url: '/correct/',
            data: {'works_id':works_id,'star':star,'comment':comment},
            type: "POST",
            dataType: 'json',
            beforeSend: function(){
                smallnote('正在批改...');
                correctinfo.slideUp('fast');
                return true;
            },
            success: function(response) {
                if(response.code=='0') {
                    smallnote('批改成功');
                }
                else {
                    
                }
            },
            error: function() {
                smallnote('批改失败');
            }
        });
    }
    function approval(){
        var correctinfo = $(this).parents('.correctinfo');
        var star = correctinfo.find('.star').attr('data-star');
        var works_id = correctinfo.attr('data-hdid');
        var comment = correctinfo.find('textarea[name=comment]').val();
        jQuery.ajax({
            url: '/approval/',
            data: {'works_id':works_id,'comment':comment},
            type: "POST",
            dataType: 'json',
            beforeSend: function(){
                smallnote('正在审批...');
                correctinfo.slideUp('fast');
                return true;
            },
            success: function(response) {
                if(response.code=='0') {
                    smallnote('审批成功');
                }
            },
            error: function() {
                smallnote('审批失败');
            }
        });
    }
});
//推荐作业
jQuery(function() {
     $('.pubinfo').on('click','.favor',function(){
         var works_id = $(this).attr('data-wid');
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
                }
            },
            error: function() {
                smallnote('推荐失败');
            }
        });
    });
});
//察看未确认的作业
jQuery(function() {
     $('.unconcount').mouseover(function(){
         $(this).siblings('.unconmem').show();
     });
     $('.unconcount').mouseout(function(){
         $(this).siblings('.unconmem').hide();
     });
});
//确认笔头作业已经完成
jQuery(function() {
     $('.writingconfirmbtn').click(function(){
         var ele = $(this);
         var task_id = $(this).attr('data-taskid');
         jQuery.ajax({
            url: '/writing/confirm/',
            data: {'task_id':task_id},
            type: "POST",
            dataType: 'json',
            beforeSend: function(){
                smallnote('正在确认...');
                return true;
            },
            success: function(response) {
                if(response.code=='0') {
                    smallnote('确认成功');
                    ele.siblings('span').show();
                    ele.remove();
                    //$('#unwritingcount').html((parseInt($('#unwritingcount').text())-1));
                }
            },
            error: function() {
                smallnote('确认失败');
            }
        });
     });
});
