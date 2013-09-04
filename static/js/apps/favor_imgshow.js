jQuery(function(){
    // 图片轮播
    var liindex = 0;
    var licount = parseInt($(".carousel ul").attr("len"));
    $(".turnleft,.turnright").click(function(){
        move = true
        leftstr = $(".carousel ul").css("left");
        left = parseInt(leftstr.match(/^-?[0-9]+/)?leftstr.match(/^-?[0-9]+/):0);
        widthstr = $(".carousel ul").css("width");
        width = parseInt(widthstr.match(/^-?[0-9]+/)?widthstr.match(/^-?[0-9]+/):90);
        if(left%90){return};
        if($(this).attr("class")=="turnleft left"){
            if(liindex>0){
                liindex = liindex -1;
                $(".carousel ul li img:eq("+ liindex +")").click();
            }else{
                smallnote("没有图片了 ^ ^")
            }
            if(width>450){
                if(left < 0){
                    $(".carousel ul").animate({"left":left+90+"px"});
                }
            }
        }else{
            if(liindex+1<licount){
                liindex = liindex +1;
                $(".carousel ul li img:eq("+ liindex +")").click();
            }else{
                smallnote("没有图片了 ^ ^")
            }
            if(width>450){
                if(width + left - 450>0){
                    $(".carousel ul").animate({"left":left-90+"px"});
                }
            }
        }
    });
    
    $(".carousel ul li img").click(function(){
        $(".showbox div").html("");
        liindex = parseInt($(this).attr("index"))-1;
        $(".carousel ul li img[class]").attr("class","");
        $(this).attr("class","active");
        imgurl = $(this).attr("data");
        
        $(".showbox div").html("<img src="+ imgurl +" />");
        $(".showbox a").attr("href",imgurl);
        var title = $(this).attr("title");
        $("#imginfo").html(title);
    })
});

jQuery(function(){
    $("#comment").load("./comment/");
    
    //发表评论
    $("#sendcomment").click(function(){
        var comment = $(".comment textarea").val();
        if(comment.length == 0){
            smallnote('请输入评论');
            return
        }
        var reply_id = $("#replydiv input").val();
        jQuery.ajax({
            url: './sendcomment/',
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
    
    
    $("#favor_love").click(function(){
        loveicon = $(this).find('div');
        lovespan  = $(this).find('span');
        worksid = $(".send-img").attr("data");
        if(loveicon.attr("class")=="left fav_love_black"){
            jQuery.ajax({
                url: "/favor/taskimg/"+ worksid +"/dellove/",
                type: "POST",
                dataType: 'json',
                success: function(response) {
                    if(response.code=='0') {
                        loveicon.attr("class","left fav_love");
                        lovespan.html(Number(lovespan.html()) - 1);
                        smallnote('取消喜欢该图片作业');
                    }else{
                        smallnote('取消喜欢该图片作业失败');
                    }
                },
                error: function() {
                    smallnote('取消喜欢该图片作业失败');
                }
            });
        }else{
            jQuery.ajax({
                url: '/favor/taskimg/'+worksid+'/love/',
                type: "POST",
                dataType: 'json',
                success: function(response) {
                    if(response.code=='0') {
                        loveicon.attr("class","left fav_love_black");
                        lovespan.html(Number(lovespan.html()) + 1);
                        smallnote('喜欢该图片作业');
                    }else{
                        smallnote('喜欢该图片作业失败');
                    }
                },
                error: function() {
                    smallnote('喜欢该图片作业失败');
                }
            });
        }
    });
    
    
});
