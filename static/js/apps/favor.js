jQuery(function() {
    $(".favor_div").click(function(){
        icon_obj = $(this).find("div");
        span_obj = $(this).find("span");
        classval = icon_obj.attr("class");
        var works_id = icon_obj.attr("data");
        if(classval == "left favor2_icon"){
            jQuery.ajax({
                url: '/favor/del/',
                data: {'works_id':works_id},
                type: "POST",
                dataType: 'json',
                beforeSend: function(){
                    smallnote('正在取消推荐...');
                    return true;
                },
                success: function(response) {
                    if(response.code=='0') {
                        smallnote('取消推荐成功');
                        icon_obj.attr("class","left favor2_icon_gray");
                        icon_obj.attr("title","推荐");
                        span_obj.html("推荐")
                    }else{
                        smallnote('取消推荐失败');
                    }
                },
                error: function() {
                    smallnote('取消推荐失败');
                }
            });
        }else{
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
                        icon_obj.attr("class","left favor2_icon");
                        icon_obj.attr("title","取消推荐");
                        span_obj.html("取消推荐")
                    }else{
                        smallnote('推荐失败');
                    }
                },
                error: function() {
                    smallnote('推荐失败');
                }
            });
        }

    });
});
