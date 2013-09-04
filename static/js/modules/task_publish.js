// 显示班级
jQuery(function() {
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
        changebtnstate();
        tools.cancelBubble(event);
    });
/**
 * 日历
 */
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
            changebtnstate();
            calcircle();
        },
        onSuccess:function(){
            changebtnstate();
            calcircle();
        }
    });
//附件
    var uploadpanel = $('#attachmentuploader'),
        addattachment = $('#addattachment'),
        attachmentpanel = $('#attachmentpanel'),
        task_typeoption = $('.task-type'),
        multi_task = $('#multitask');
    //类型切换
    task_typeoption.on('click',function(){
        $(this).parent().find('.active').removeClass('active');
        $(this).addClass('active');
    });
    //批量切换
    multi_task.on('click',function(){
        var ele =$(this).parent().find('input[name=multitask]');
        showmulti(ele,false);
    });
    $('input[name=multitask]').click(function(){
        showmulti($(this),true);
    });
    function showmulti(ele,ischeckedbox){
        if(ele.attr('checked')&&ele.attr('checked') == 'checked'){
            if(!ischeckedbox){
                ele.removeAttr('checked');
                $('.single-task-time').show();
                $('.sendmailpanel').show();
                $('.multi-task-time').hide();
            }else{
                $('.single-task-time').hide();
                $('.sendmailpanel').hide();
                $('.multi-task-time').show();
            }
        }else{
            if(!ischeckedbox){
                ele.attr('checked','checked');
                $('.single-task-time').hide();
                $('.sendmailpanel').hide();
                $('.multi-task-time').show();
            }else{
                $('.single-task-time').show();
                $('.sendmailpanel').show();
                $('.multi-task-time').hide();
            }
        }
        calcircle();
    }
    $('input[name=daycount]').keyup(function(event){
        if(event.which == 38){
            //往上加1
            calday(1)
        }
        if(event.which == 40){
            //往下减1
            calday(-1)
        }
        calcircle();
    });
    function calday(tag){
        var dayinput = $('input[name=daycount]'),
            day = dayinput.val();
        try{
            day = day?parseInt(day,10):'';
            day += tag;
        }catch(e){
            day = 1;
        }
        if(day!=''&&day<1){
            day = 1;
        }
        dayinput.val(day);
    }
    function calcircle(){
        var start = new Date($('#multitask_start').val()),
            end = new Date($('#multitask_end').val()),
            daycountinput = $('input[name=daycount]'),
            daycount = 1;
        if(end - start < 0){
            smallnote('结束时间不能小于开始时间');
            return false;
        }
        daycount = parseInt(daycountinput.val(),10);
        var totalcount = parseInt(((end - start)/86400000+1)/daycount,10);
        if(!totalcount){
            if(daycount)
                smallnote('设置的天数不正确');
            $('#totalcount').text(0);
            return false;
        }else{
            $('#totalcount').text(totalcount);
        }
    }
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

// 提交数据
    function varifyDate(show){
        var task_type = $('.task-type.active').attr('data-type'),
            task_content = $('#task_content').val(),
            task_desc = $('#task_desc').val(),
            classids = $('#selectclass').attr('classids'),
            task_deadline = $('#task_deadline').val(),
            task_multi = $('input[name=multitask]').attr('checked') == 'checked',
            task_start = $('#multitask_start').val(),
            task_end = $('#multitask_end').val(),
            task_rate = $('input[name=daycount]').val(),
            task_sendemail = $('input[name=sendmail]').attr('checked') == 'checked';
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
        if(task_desc){
            result.description = task_desc;
        }
        if(classids){
            result.class_ids = classids;
        }else{
            if(show)
                smallnote('选择班级');
            return false;
        }
        if(task_multi){
            if(task_end&&task_start){
                task_end = new Date(task_end).getTime();
                task_start = new Date(task_start).getTime();
                if(task_end >= task_start){
                    result.start = task_start;
                    result.end = task_end;
                }else{
                    if(show)
                        smallnote('开始时间不能大于结束时间');
                    return false;
                }
            }else{
                if(show)
                    smallnote('选择开始时间和结束时间');
                return false;
            }
            var totalcount = $('#totalcount').text();
            if(task_rate&&$('#totalcount').text() != '0'){
                result.rate = task_rate;
                result.totalcount = totalcount;
            }else{
                if(show)
                    smallnote('请输入正确的天数');
                return false;
            }
            result.multi = 1;
        }else{
            if(task_deadline){
                result.deadline = new Date(task_deadline).getTime();
                result.multi = 0;
            }else{
                if(show)
                    smallnote('选择截止日期');
                return false;
            }
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
        result.sendemail = task_sendemail?1:0;
        return result;
    }
    jQuery('#task_content').live('keyup',function(){
        changebtnstate();
    });
    function changebtnstate(){
        if(varifyDate()){
            jQuery('#publishbtn').removeClass('disable');
        }
        else{
            jQuery('#publishbtn').addClass('disable');
        }
    }
    jQuery('#publishbtn').click(preivew);
    var task_datas = null;
    function preivew(){
        var previewpanel = $('.previewpanel');
        previewpanel.remove();
        var datas = varifyDate(true);
        if(datas){
            // 验证班级邮箱存在
            function yulan(){
                task_datas = datas;
                var classgrades =[],
                    selectclass = $("#selectclass");
                var classids = selectclass.attr('classids').split(',');
                var classnames = selectclass.attr('classnames').split('@');
                for(var i=0;i<classids.length;i++){
                    classgrades.push({'class_id':classids[i],'class_name':classnames[i+1]});
                }
                var attachments = null;
                if(datas.filename){
                    attachments = [];
                    for(var i=0;i<datas.filename.length;i++){
                        var filename = datas.filename[i];
                        attachments.push({'filename':filename});
                    }
                }
                templdatas = {'task':{
                    'ispreview':true,
                    'teacher':{
                        'nickname':vself.visitor.nickname,
                        'smallavatar':vself.visitor.smallavatar,
                        //'isteacher':vself.visitor.isteacher,
                        },
                    'task_content':datas.content,
                    'description':datas.description,
                    'isvideo':datas.type == 1,
                    'iswriting':datas.type == 2,
                    'task_type_text':["视频","笔头","通知","图片","文字"][datas.type-1],
                    'multi':datas.multi == 1,
                    'start':tools.dateformat(datas.start),
                    'end':tools.dateformat(datas.end+86399*1000),
                    'rate':datas.rate,
                    'totalcount':datas.totalcount,
                    'deadline':tools.dateformat(datas.deadline),
                    'classgrades':classgrades,
                    'updatetime':tools.dateformat(new Date().getTime()),
                    'attachments':attachments
                }};
                var previewpanel = $('<div class="previewpanel"></div>');
                previewpanel.append(jQuery(Mustache.render(Template,templdatas)));
                previewpanel.prependTo($('.task-main'));
                previewpanel.hide();
                previewpanel.slideDown();
                previewpanel.scroll();
                previewpanel.on('click','.task-preview-cancel',function(){
                    previewpanel.slideUp(function(){
                        previewpanel.remove();
                    });
                });
                previewpanel.on('click','.task-preview-ok',function(){
                    publish();
                });
            }
            
            
            if($('input[name=sendmail]').attr("checked")){
                jQuery.ajax({
                    url: '/api/task/checkclassmail/',
                    data: {'class_ids':datas['class_ids']},
                    type: "POST",
                    dataType: 'json',
                    traditional:true,
                    success: function(response) {
                        if(response.code==0){
                            yulan()
                        }
                        if(response.code==4005){
                            smallnote(response.message)
                        }
                    },
                    error: function() {
                        smallnote('网络异常');
                    }
                });
            }else{
                yulan()
            }
            
        }
    }
    function publish(){
        if(!task_datas) return false;
        uploadpanel.css('left','-10000px');
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
                    if(task_datas.multi == 0){
                        smallnote('恭喜你，发布成功');
                        var previewpanel = $('.previewpanel');
                        $('.task-preview',previewpanel).remove();
                        $('.task-container',previewpanel).removeClass('preview');
                        var data = response.data;
                        var index = 0;
                        previewpanel.find('.task-attachment a').each(function(){
                            var attach = data.attachments[index];
                            $(this).attr('href',attach.path).html(attach.filename);
                            index++;
                        });
                        previewpanel.removeClass('previewpanel');
                        uploadpanel.uploadrefresh();
                    }else{
                        $('.previewpanel').remove();
                        smallnote('恭喜你，发布成功，请等待系统自动发布，谢谢');
                    }
                }
            },
            error: function() {
                smallnote('对不起，发布失败');
            }
        });
    }
});
