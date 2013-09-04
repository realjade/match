//初始化视频
jQuery(function(){
    $('.beishuPlayer').each(function(){
        load_videoplayer($(this).attr('id'));
    });
});


jQuery(function(){
    worksid = $(".fav_video").attr("data");
    $("#comment").load("/favor/video/"+ worksid +"/comment/");
});



jQuery(function() {
    // 喜欢视频
    $("#favor_love").click(function(){
        loveicon = $(this).find('div');
        lovespan  = $(this).find('span');
        worksid = $(".fav_video").attr("data");
        if(loveicon.attr("class")=="left fav_love_black"){
            jQuery.ajax({
                url: "/favor/video/"+ worksid +"/dellove/",
                type: "POST",
                dataType: 'json',
                success: function(response) {
                    if(response.code=='0') {
                        loveicon.attr("class","left fav_love");
                        lovespan.html(Number(lovespan.html()) - 1);
                        smallnote('取消喜欢视频');
                    }else{
                        smallnote('取消喜欢视频失败');
                    }
                },
                error: function() {
                    smallnote('取消喜欢视频失败');
                }
            });
        }else{
            jQuery.ajax({
                url: '/favor/video/'+worksid+'/love/',
                type: "POST",
                dataType: 'json',
                success: function(response) {
                    if(response.code=='0') {
                        loveicon.attr("class","left fav_love_black");
                        lovespan.html(Number(lovespan.html()) + 1);
                        smallnote('喜欢该视频');
                    }else{
                        smallnote('喜欢该视频失败');
                    }
                },
                error: function() {
                    smallnote('喜欢该视频失败');
                }
            });
        }
    });
    
    //发表评论
    $("#sendcomment").click(function(){
        var worksid = $(".fav_video").attr("data");
        var comment = $(".comment textarea").val();
        if(comment.length == 0){
            smallnote('请输入评论');
            return
        }
        var reply_id = $("#replydiv input").val();
        jQuery.ajax({
            url: '/favor/video/'+worksid+'/sendcomment/',
            data:{"comment":comment,"reply_id":reply_id},
            type: "POST",
            dataType: 'json',
            success: function(response) {
                if(response.code=='0') {
                    $("#commentlist").append("<div class=clearfix><div class=left>我</div><div class=left style=margin-left:15px;>刚刚儿</div><div class=clearfix></div><div >"+comment+"</div><div class=right>回复</div></div>")
                    smallnote('评论成功');
                    $(".comment textarea").val("")
                }else{
                    smallnote('评论失败');
                }
            },
            error: function() {
                smallnote('评论失败');
            }
        });
    });
    
    
    
    
});
