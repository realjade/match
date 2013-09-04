// 上传图片
jQuery(function() {
    var ias = NaN;
    var data = NaN;
    var uploader = new plupload.Uploader({
        runtimes : 'gears,flash,html5,html4,silverlight,browserplus',
        browse_button : 'avatar',
        max_file_size : '10mb',
        url : '/settings/avatar/upload/',
        multiple_queues : false,
        multi_selection : false,
        multipart_params:{},
        flash_swf_url : '/static/swf/plupload.flash.swf',
        filters : [{title : "图片文件", extensions : "png,jpg,jpeg,gif,PNG,JPG,JPEG,GIF"}]
    });
    
    // 获取ID 上传进度
    uploader.bind('UploadProgress', function(up, file) {
        if(file.percent<100){
            $("#avatarper").html(file.percent+"%");
        }else{
            $("#avatarper").hide();
        }
    });
    
    uploader.bind('QueueChanged', function(){
        $("#avatarper").show();
        $("#avatarper").html("0%");
        uploader.start();
        $("#submit").css({"display":"none"})
        if(ias){
            ias.cancelSelection();
            ias.setOptions({disable:true});
        }
    });
    
    uploader.bind('FileUploaded', function(up, file, response) {
        if(response&&response.response){
            data = JSON.parse(response.response);
            if(data.code==0){
                smallnote('上传成功');
                $("#photo").attr("src",data.data.path);
                
                var img = new Image();
                img.src = data.data.path;
                img.onload = function(){
                    // 剪切图片
                    ias = $('img#photo').imgAreaSelect({
                        handles: true,
                        aspectRatio: '1:1',
                        enable:true,
                        instance: true,
                        hide:true,
                        imageHeight:data.data.height,
                        imageWidth:data.data.width,
                        show:true,
                        onSelectEnd: function (img, selection) {
                            data = selection;
                            $("#submit").css({"display":"block"})
                        }
                    });
                    ias.setOptions({show:true})
                    ias.setSelection(0, 0, 150, 150, true);
                    ias.update()
                }
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
    
    $("#submit").one("click",function(){
        jQuery.ajax({
            url: '/settings/avatar/cut/',
            data: data,
            type: "POST",
            dataType: 'json',
            success: function(response) {
                if(response.code=='0') {
                    smallnote('保存成功,5秒后刷新网页。');
                    setTimeout("window.location.reload()",5000)
                }else{
                    smallnote('保存失败');
                }
            },
            error: function() {
                smallnote('保存失败');
            }
        });
        
    })
    
    
    
    
})
