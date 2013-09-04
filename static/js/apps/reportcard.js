jQuery(function(){
    var current = 0;
    var tag = true;
    $('#ol-users tr').each(function(index,item){
        if(!$(this).hasClass('current')&&tag){
            current++;
        }else{
            tag = false;
        }
    });
    $('#ol-results tr').each(function(index,item){
        if(index == current){
            $(this).addClass('current');
        }
    });
});
jQuery(function(){
    $('#classgrade').change(function(){
        var class_id = $(this).val();
        var url = window.location.href;
        if(url.indexOf('child')){
            if(url.substring(url.indexOf('child')).split('/').length==4){
                var tmp = url.split('/');
                tmp.pop();
                tmp.pop();
                window.location.href = tmp.join('/')+'/'+class_id+'/';
            }else{
                window.location.href += class_id+'/';
            }
        }else{
            window.location.href = '/reportcard/online/'+class_id+'/';
        }
        
    });
    $('.export').click(function(){
        var class_id = $('#classgrade').val()
        window.open('/reportcard/online/'+class_id+'/export/');
    });
});
//导入成绩单
jQuery(function(){
    var vselfupload = $('#vselfupload');
    if(vselfupload['uploader']){
        vselfupload.uploader({
                url:'/reportcard/classroom/import/',
                filters: [
                            {title : "excel文件", extensions : "xls,xlsx"}
                        ],
                max_file_count:1,
                multi_selection:false,
                uploadsuccess:function(){
                    window.location.reload();
                    }
            });
       $('.update').click(function(e){
           var ele = $(this);
           $('input[name=reportcard_id]').val(ele.attr('data-reportcard_id'));
           vselfupload.uploadparams();
           vselfupload.css({'top':ele.offset().top+15,'left':ele.offset().left-vselfupload.width()+100});
           $(document).one('click',function(){
               vselfupload.css({'left':'-1000px'});
           });
           tools.cancelBubble(e);
       });
       vselfupload.click(function(e){
           tools.cancelBubble(e);
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
            myclasses.find('input').each(function(){
                $(this).parents('li').removeAttr('date-checked');
                $(this)[0].checked='';
            });
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
            $('input[name="class_id"]').val(classid);
        });
    }
});
