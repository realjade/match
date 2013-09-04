$(function(){
    //task type
    $('.task-type').click(function(){
        $('.task-type').removeClass('active');
        $(this).addClass('active');
    });
    //task deadline
    $(".deadline").datepicker({
        dateFormat:"yy/mm/dd",
        dayNames:["周日","周一","周二","周三","周四","周五","周六"],
        dayNamesMin:["周日","周一","周二","周三","周四","周五","周六"],
        monthNames:["一月","二月","三月","四月","五月","六月","七月","八月","九月","十月","十一月","十二月"],
        minDate:+1,
        nextText:"下一月",
        prevText:"上一月",
        onSelect: function(){
            $(this).trigger('blur');
        }
    });
    var myclasses = $('#myclasses'),
        selectclass = $("#selectclass");
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
    //task attachment
    var uploadpanel = $('#attachmentuploader'),
        addattachment = $('#addattachment');
    addattachment.click(function(event){
        if(addattachment.hasClass('active')){
            addattachment.removeClass('active');
            uploadpanel.css('left','-10000px');
        }else{
            addattachment.addClass('active');
            uploadpanel.css('top',addattachment.offset().top+addattachment.height()+8).css('left',addattachment.offset().left-149);
            tools.cancelBubble(event);
        }
        $(document).one('click', function(){
            addattachment.removeClass('active');
            uploadpanel.css('left','-10000px');
        });
    });
    uploadpanel.click(function(event){
        tools.cancelBubble(event);
    });
    
    uploadpanel.uploader({url:'/upload/attachment/',uploadeddelete:uploadeddelete,filters:[]});
    function uploadeddelete(file){
        var data = JSON.parse($('#'+file.id).attr('data-uploader'));
        jQuery.ajax({
            url: '/attachment/delete/',
            data: data,
            type: "POST",
            dataType: 'json',
            success: function(response) {
                if(response.code=='0') {
                    smallnote('删除成功');
                }
                else {
                    smallnote('删除失败');
                }
            },
            error: function() {
                smallnote('删除失败');
            }
        });
    }
    function varifyDate(show){
        var task_type = $('.task-type.active').attr('data-type'),
            task_content = $('#task_content').val(),
            classids = $('#selectclass').attr('classids'),
            task_deadline = $('#task_deadline').val();
        var result = {
            'type':task_type
        };
        if(task_content){
            result.content = task_content;
        }else{
            if(show)
                smallnote('输入内容');
            return false;
        }
        if(classids){
            result.class_ids = classids;
        }else{
            if(show)
                smallnote('选择班级');
            return false;
        }
        if(task_deadline){
            result.deadline = new Date(task_deadline).getTime();
            result.multi = 0;
        }else{
            if(show)
                smallnote('选择截止日期');
            return false;
        }
        result.filepath = [];
        result.filename = [];
        $('#attachmentuploader .upload_file_item').each(function(){
            var filepath = JSON.parse($(this).attr('data-uploader')).filepath;
            var filename = $(this).find(".upload_file_name").text();
            if(filepath){
                result.filepath.push(filepath);
                result.filename.push(filename);
            }
        });
        return result;
    }
    $('#publishbtn').click(function(){
        var task_datas = varifyDate(true);
        if(task_datas && confirm("确认发布作业")){
           jQuery.ajax({
            url: '/teacher/task/publish/',
            data: task_datas,
            type: "POST",
            dataType: 'json',
            traditional:true,
            beforeSend: function(){
                $('.previewpanel').unbind('click');
                return true;
            },
            success: function(response) {
                if(response.code=='0') {
                    window.location.reload();
                }
            }
        }); 
        }
    });
});