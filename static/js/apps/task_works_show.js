jQuery(function(){
    $('.work-item .work-muticorrect').hide();
    $('.task_notreaded .work-item .avatar').each(function(){
        $('<div class="muticheckbox mutichecked"></div>').appendTo($(this));
    });
    $('.task_notreaded .muticheckbox').click(function(){
        $(this).toggleClass('mutichecked');
    });
    $('#task_notreaded .work-item').unbind('click');
    var notreadedpanel = $('.task_notreaded'),
        correctpanel = $('#correctall .work-correct-panel');
    correctpanel.find('.work-redo-checkbox').hide();
    correctpanel.show();
    //批改建议点击
    $('#correctall .work-correct-panel .comment-suggest').on('click','li',function(){
        var target = $(this).parents('#correctall'),
            ele = $(this),
            correctpanel = target.find('.work-correct-panel');
        correctpanel.find('.comment-content').val(ele.text());
        correctpanel.find('.comment-content').siblings('label').hide();
    });
    //点击清空按钮
    $('#correctall .work-correct-panel').on('click','.correct-clear',function(){
        var target = $(this).parents('#correctall');
        target.find('.comment-content').val('');
    });
    $('#correctall .correct-ok').click(function(){
        var works = [];
        $('.mutichecked',notreadedpanel).each(function(){
            works.push($(this).parents('.work-item').attr('data-words_id'));
        });
        star = correctpanel.find('.work_star').attr('data-star'),
        content = correctpanel.find('.comment-content').val();
        
        jQuery.ajax({
            url: '/correct/',
            data: {'works_id':works,'star':star,'comment':content},
            type: "POST",
            dataType: 'json',
            traditional:true,
            beforeSend: function(){
                smallnote('正在批量批改...');
                return true;
            },
            success: function(response) {
                if(response.code=='0') {
                    smallnote('批量批改成功');
                    window.location.reload();
                }
            },
            error: function() {
                smallnote('批量批改失败');
            }
        });
    });
});