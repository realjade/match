// 显示班级
jQuery(function() {
    var myclasses = $('#myclasses');
    var selectclass = $("#selectclass");
    selectclass.click(function(event){
        $('#myclasses').css('top',$(this).offset().top+$(this).height()).css('left',$(this).offset().left).show();
        tools.cancelBubble(event);
        $(document).one('click', function(){
            myclasses.hide();
        });
    });
    myclasses.on('click','li',function(event){
        var classid = '';
        var classname = '';
        var checked = $(this).find('input');
        if($(this).attr('date-checked')){
            $(this).removeAttr('date-checked');
            checked[0].checked='';
        }else{
            $(this).attr('date-checked','checked');
            checked[0].checked='checked';
        }
        myclasses.find('input:checked').each(function(){
            classid+=(classid?',':'')+$(this).parents('li').attr('classid');
            classname+='@'+$(this).parents('li').find('span').text();
        });
        selectclass.html(classname);
        selectclass.attr('classids',classid);
        selectclass.attr('classnames',classname);
        tools.cancelBubble(event);
    });
});

// 上传视频
jQuery(function() {
    var uploader = new plupload.Uploader({
        runtimes : 'html5,flash',
        browse_button : 'upbtn',
        max_file_size : '200mb',
        url : '/favor/goodvideo/upload/',
        multiple_queues : false,
        multi_selection : false,
        multipart_params:{},
        uploadsuccess:null,
        flash_swf_url : '/static/swf/plupload.flash.swf',
        filters : [{title : "视频文件", extensions : "avi,flv,f4v,mp4,m4v,mkv,mov,3gp,3gp,3g2,mpg,wmv,ts"}]
    });
    // 获取ID 上传进度
    uploader.bind('UploadProgress', function(up, file) {
        if(file.status == 5){
            return false;
        }
        if(file.percent >= 100){
            $("#"+file.id).html("<div class=pro>正处理</div>");
        }else{
            $("#"+file.id).html("<div class=pro> "+file.percent+"%</div>");
        }
    });
    // 选中文件后 循环读取文件名称
    uploader.bind('FilesAdded', function(up, files) {
        var name = files[0].name;
        var divid = files[0].id;
        var size = plupload.formatSize(files[0].size);
        if($(".upimgmodule .imgdivempty").length == 0){
            
            $(".upimgmodule .imgdiv:first").attr("id", divid);
            $(".upimgmodule .imgdiv:first").attr("title",name+"("+size+")");
            $(".upimgmodule .imgdiv:first").attr("class","imgdivempty");
        }else{
            $(".upimgmodule .imgdivempty").attr("class","imgdivempty");
            $(".upimgmodule .imgdivempty").attr("id", divid);
            $(".upimgmodule .imgdivempty").attr("title",name+"("+size+")");
        }
        
    });
    
    // 队列改变 开始上传
    uploader.bind('QueueChanged', function(){
        uploader.start();
    });
    
    uploader.bind('FileUploaded', function(up, file, response) {
        if(response&&response.response){
            var data = JSON.parse(response.response);
            if(data.code==0){
                smallnote('请将视频旋转至正确的角度');
                data = data.data;
                var imgrotate = new ImageRotate({
                    imgpath:data.thumbnail_path,
                    success:function(){
                        var self = this;
                        var rotate = (self.rotate%360+360)%360;
                        jQuery.ajax({
                            url: '/fav/goodvideo/transpose/',
                            data: {'rotate':rotate,'video_id':data.video_id,'thumbnail_path':data.thumbnail_path,'savepath':data.savepath,'fvcid':data.fvcid},
                            type: "POST",
                            dataType: 'json',
                            beforeSend:function(){
                                smallnote('正在处理，请休息一下吧。');
                            },
                            success: function(response) {
                                if(response.code=='0') {
                                    window.location.reload();
                                }
                            }
                        });
                    }
                });
                //$("#"+file.id).attr("class","imgdiv");
                //html = "<div class=imgbox ><img src="+data.data.path+"></div><div class=delete data="+data.data.id+">X</div>";
                //$("#"+file.id).html(html);
                //$('#upbtn span').html('重新上传');
            }else{
                smallnote('上传失败');
            }
        }
    });
    
    // 上传失败
    uploader.bind("Error", function(up, err) {
        smallnote('上传失败');
    });
    
    uploader.init();
    
    // 删除
    $(".imgdiv .delete").live("click",function(){
        parent = $(this).parent();
        jQuery.ajax({
            url: '/favor/goodvideo/upload/delete/',
            data: {'fvcid':$(this).attr("data")},
            type: "POST",
            dataType: 'json',
            success: function(response) {
                if(response.code=='0') {
                    parent.html("");
                    parent.attr("class","imgdivempty");
                    smallnote('删除成功');
                }else{
                    smallnote('删除失败');
                }
            },
            error: function() {
                smallnote('删除失败');
            }
        });
    })
    
    // 发布GOOD VIDEO
    $("#publish").click(function(){
        var name = $("input[name=name]").val();
        var reason = $("input[name=reason]").val();
        var classids = $('#selectclass').attr('classids');
        var videocount = $(".imgdiv .delete").length;
        
        if(!name){
            smallnote('输入上传的视频名称');
            return false;
        }
        if(!classids){
            smallnote('选择班级');
            return false;
        }
        
        if(videocount != 1){
            smallnote('上传视频');
            return false;
        }
        jQuery.ajax({
            url: '/favor/goodvideo/publish/',
            data: {'name':name,'reason':reason,'classids':classids},
            type: "POST",
            dataType: 'json',
            success: function(response) {
                if(response.code=='0') {
                    smallnote('发布成功');
                    window.location.reload();
                    
                }else{
                    smallnote('发布失败');
                }
            },
            error: function() {
                smallnote('发布失败');
            }
        });
        
    });
});
