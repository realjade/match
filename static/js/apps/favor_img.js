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

// 上传图片
jQuery(function() {
    var uploader = new plupload.Uploader({
        runtimes : 'html5,flash',
        browse_button : 'upbtn',
        max_file_size : '10mb',
        url : '/favor/img/upload/',
        multiple_queues : true,
        multi_selection : true,
        multipart_params:{},
        flash_swf_url : '/static/swf/plupload.flash.swf',
        filters : [{title : "图片文件", extensions : "png,jpg,jpeg,gif"}]
    });
    
    // 获取ID 上传进度
    uploader.bind('UploadProgress', function(up, file) {
        if(file.percent<100){
            $("#"+file.id).html("<div class=pro> "+file.percent+"%</div>");
        }
    });
    // 选中文件后 循环读取文件名称
    uploader.bind('FilesAdded', function(up, files) {
        for (var i in files) {
            var name = files[i].name;
            var divid = files[i].id;
            var size = plupload.formatSize(files[i].size);
            exhtml = "<div class='imgdivempty' id="+divid+" title='"+name+"("+size+"')></div>";
            $(exhtml).insertBefore(".example");
        }
    });
    
    // 队列改变 开始上传
    uploader.bind('QueueChanged', function(){
        uploader.start();
    });
    
    uploader.bind('FileUploaded', function(up, file, response) {
        if(response&&response.response){
            data = JSON.parse(response.response);
            if(data.code==0){
                smallnote('上传成功');
                $("#"+file.id).attr("class","imgdiv")
                html = "<div class=imgbox ><img src="+data.data.path+"></div><div class=delete data="+data.data.id+">X</div>"
                $("#"+file.id).html(html)
            }else{
                smallnote('上传失败');
            }
        }
    });
    
    // 上传失败
    uploader.bind("Error", function(up, err) {
        smallnote('上传失败');
        //alert(err)
        // 参考 modules/vselfuploader.js
    });
    
    uploader.init();
    
    // 删除
    $(".imgdiv .delete").live("click",function(){
        parent = $(this).parent();
        jQuery.ajax({
            url: '/favor/img/upload/delete/',
            data: {'ficid':$(this).attr("data")},
            type: "POST",
            dataType: 'json',
            success: function(response) {
                if(response.code=='0') {
                    parent.remove();
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
    
    // 发布相册
    $("#publish").click(function(){
        var name = $("input[name=name]").val();
        var reason = $("input[name=reason]").val();
        var classids = $('#selectclass').attr('classids');
        var imgcount = $(".imgdiv").length;
        
        /*if(uploader.files.length>0){
            smallnote('图片未上传完毕');
            return false;
        }*/
        
        if(!classids){
            smallnote('选择班级');
            return false;
        }
        
        if(imgcount<=1){
            smallnote('上传图片');
            return false;
        }
        
        
        jQuery.ajax({
            url: '/favor/img/publish/',
            data: {'name':name,'reason':reason,'classids':classids},
            type: "POST",
            dataType: 'json',
            success: function(response) {
                if(response.code=='0') {
                    smallnote('发布成功');
                    window.location.reload();
                    /** $("input[name=name]").val("");
                    $("input[name=reason]").val("");
                    $('#selectclass').attr('classids','');
                    $('#selectclass').attr('classnames','');
                    $('#selectclass').html("")
                    */
                    
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


