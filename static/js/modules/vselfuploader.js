(function($) {
    var uploaders = {};
    $.fn.uploadrefresh = function(){
        var target = $(this);
        var id = target.attr('id');
        var uploader = uploaders[id];
        uploader.splice();
    };
    $.fn.uploadparams = function(){
        var target = $(this);
        var id = target.attr('id');
        var uploader = uploaders[id];
        target.find('.upload_params').each(function(){
            var key = $(this).attr('name');
            var value = $(this).val();
            if(key&&value){
                uploader.settings.multipart_params[key] = value;
            }
        });
    };
    $.fn.uploaderalldone = function(){
        var target = $(this);
        var id = target.attr('id');
        var uploader = uploaders[id];
        var tag = true;
        $.each(uploader.files, function(i, file) {
            if(file.status != plupload.DONE&&file.status != plupload.FAILED){
                tag = false;
            }
        });
        return tag;
    }
    $.fn.uploader = function(settings) {
        if (settings) {
            this.each(function() {
                var options={
                    // General settings
                    runtimes: 'flash,html5',
                    url : '/task/upload/',
                    max_file_size: '200mb',
                    max_file_count: 20, // user can add no more then 20 files at a time
                    unique_names : false,
                    multiple_queues : true,
                    multi_selection : true,
                    multipart_params:{},
                    // Specify what files to browse for
                    filters: [
                        {
                            title : "视频文件", extensions : "avi,flv,f4v,mp4,m4v,mkv,mov,3gp,3gp,3g2,mpg,wmv,ts"
                        },
                        {
                            title : "图片文件", extensions : "png,jpg,jpeg,gif"
                        }
                    ],
                    uploadsuccess:null,
                    // Flash/Silverlight paths
                    flash_swf_url : '/static/swf/plupload.flash.swf'
                };
                var uploader, target, id;

                target = $(this);
                id = target.attr('id');
                
                if (!id) {
                    id = plupload.guid();
                    target.attr('id', id);
                }
                $.extend(options, settings);
                settings = $.extend({
                    dragdrop : true,
                    container : id
                }, options);
                $('a.upload_add', target).attr('id', id + '_browse');
                settings.browse_button = id + '_browse';
                target.find('.upload_params').each(function(){
                    var key = $(this).attr('name');
                    var value = $(this).val();
                    if(key&&value)
                        settings.multipart_params[key] = value;
                });
                
                uploader = new plupload.Uploader(settings);

                uploaders[id] = uploader;

                function updateList() {
                    var fileList = $('ul.upload_filelist', target).html(''), inputCount = 0, inputHTML;

                    $.each(uploader.files, function(i, file) {
                        inputHTML = '';
                        var status = file.percent+'%';
                        if(file.status == plupload.DONE){
                            status = '完成';
                        }
                        if(file.status == plupload.FAILED){
                            status = '失败';
                        }
                        fileList.append(
                            '<li id="' + file.id + '" class="upload_file_item">' +
                                '<div class="upload_file_name">' + file.name + '</div>' +
                                '<div class="upload_file_status">' + status + '</div>' +
                                '<div class="upload_file_size">' + plupload.formatSize(file.size) + '</div>' +
                                '<div class="upload_delete"><a>删除</a></div>' +
                                '<div class="upload_clearer"></div>' +
                                inputHTML +
                            '</li>'
                        );
                        $('#' + file.id).attr('data-uploader',file['data-uploader']);

                        $('#' + file.id + ' .upload_delete a').click(function(e) {
                            if(file.status == plupload.DONE){
                                if(settings.uploadeddelete){
                                    settings.uploadeddelete.call(this,file);
                                }
                            }else{
                                if(settings.uploaddelete){
                                    settings.uploaddelete.call(this,file);
                                }
                            }
                            $('#' + file.id).remove();
                            uploader.removeFile(file);
                            e.preventDefault();
                        });
                    });

                    $('a.upload_start', target).toggleClass('disable', uploader.files.length == (uploader.total.uploaded + uploader.total.failed));

                    // Scroll to end of file list
                    fileList[0].scrollTop = fileList[0].scrollHeight;

                    // Re-add drag message if there is no files
                    if (!uploader.files.length && uploader.features.dragdrop && uploader.settings.dragdrop) {
                        $('#' + id + '_filelist').append('<li class="upload_droptext">把本地文件托到这儿上传</li>');
                    }
                }

                uploader.bind('Init', function(up, res) {
                    $('ul.upload_filelist', target).attr('id', id + '_filelist');
                    // Enable drag/drop
                    if (up.features.dragdrop && up.settings.dragdrop) {
                        up.settings.drop_element = id + '_filelist';
                        $('#' + id + '_filelist').append('<li class="upload_droptext">把本地文件托到这儿上传</li>');
                    }

                    target.attr('title', 'Using runtime: ' + res.runtime);

                    $('a.upload_start', target).click(function(e) {
                        if (!$(this).hasClass('disable')) {
                            uploader.start();
                        }
                        e.preventDefault();
                    });
                    $('a.upload_start', target).addClass('disable');
                });

                uploader.init();
                uploader.bind('FilesAdded', function(up, files) {
                    if(settings.max_file_count==1){
                        if(uploader.files.length>1){
                            uploader.splice(0,1);
                        }
                    }
                });
                uploader.bind("UploadFile", function(up, file) {
                    $('#' + file.id).addClass('upload_current_file');
                });

                uploader.bind('QueueChanged', function(){
                    updateList()
                });

                uploader.bind("UploadProgress", function(up, file) {
                    // Set file specific progress
                    if(file.percent >= 100){
                        $('#' + file.id + ' div.upload_file_status', target).html('正处理');
                    }else{
                        $('#' + file.id + ' div.upload_file_status', target).html(file.percent + '%');
                    }

                    if (settings.multiple_queues && uploader.total.uploaded + uploader.total.failed == uploader.files.length) {
                        $(".upload_start", target).addClass("disable");
                        $('span.upload_total_status,span.upload_total_file_size', target).hide();
                    }
                });
                
                uploader.bind('FileUploaded', function(up, file, response) {
                    if(response&&response.response){
                        data = JSON.parse(response.response);
                        if(data.code==0){
                            smallnote('上传成功');
                            $('#' + file.id + ' div.upload_file_status', target).html('完成');
                            if(settings.uploadsuccess){
                                settings.uploadsuccess.call(this,data);
                            }
                            if(data.data){
                                $('#' + file.id).attr('data-uploader',JSON.stringify(data.data));
                                file['data-uploader'] = JSON.stringify(data.data);
                            }
                            
                        }else{
                            smallnote(data.message);
                            $('#' + file.id + ' div.upload_file_status', target).html('失败');
                            file.status = plupload.FAILED;
                        }
                    }
                });
                
                uploader.bind("Error", function(up, err) {
                    var file = err.file, message;

                    if (file) {
                        message = err.message;

                        if (err.details) {
                            message += " (" + err.details + ")";
                        }

                        if (err.code == plupload.FILE_SIZE_ERROR) {
                            smallnote("该文件大于" + settings.max_file_size);
                        }

                        if (err.code == plupload.FILE_EXTENSION_ERROR) {
                            smallnote("不支持的文件格式");
                        }
                        
                        file.hint = message;
                        $('#' + file.id).attr('class', 'plupload_failed').find('a').css('display', 'block').attr('title', message);
                    }
                });
            });

            return uploaders;
        } else {
            // Get uploader instance for specified element
            return uploaders[$(this[0]).attr('id')];
        }
    };
})(jQuery);
