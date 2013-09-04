(function($) {
    var options={
        datas:[]
    };
    var root = null;
    var roothtml = null;
    jQuery(function() {
        if(!Template)
            Template = jQuery('#emacleTempl').html();
    });
    var comment = null;
    var commentform = null;
    var mini = null;
    var selection = null;
    var range = null;
    var comments = options.datas;
    var focuscomment = null;
    $.fn.annotator=function(o){
        jQuery.extend(options,o);
        root = this;
        roothtml = this.html();
        init();
        bindEvents();
    };
    function init(){
        for(var i=0;len=options.datas.length,i<len;i++){
            var data = options.datas[i];
            addcomment(data);
        }
        comment = jQuery(Mustache.render(Template, {"annotator":{'comment':true}}));
        comment.appendTo(DOMPanel.getPanel());
        comment.hide();
        
        commentform = comment.find('form[name=comment]')
        mini = jQuery(Mustache.render(Template, {"annotator":{'mini':true}}));
        mini.appendTo(DOMPanel.getPanel());
        mini.hide();
        commentform.submit(function() {
            commentsubmit();
            return false;
        });
    }
    function bindEvents(){
        if(root[0]){
            root.on('mousedown','p',function(){
                selection = rangy.getSelection();
                if(selection){
                    selection.removeAllRanges();
                    selection.refresh();
                }
                selection = null;
                hidemini();
                hidecomment();
                commentblur();
            });
            root.on('mouseup','p',function(event){
                selection = rangy.getSelection();
                range = selection.getRangeAt(0);
                if(selection.toString().length>0){
                    showmini({top:event.pageY,left:event.pageX});
                }
            });
            mini.on('click',function(event){
                hidemini();
                showcomment();
                var position = getpostion();
                var cm = checkcomment(position);
                if(cm){
                    comment.find('textarea[name=comment]').val(cm.comment);
                    comment.find('input[name=annotator_id]').val(cm.id);
                }else{
                    comment.find('input[name=annotator_id]').val('');
                }
                comment.find('input[name=startele]').val(position.startele);
                comment.find('input[name=endele]').val(position.endele);
                comment.find('input[name=startindex]').val(position.startindex);
                comment.find('input[name=endindex]').val(position.endindex);
                comment.find('input[name=content]').val(selection.toString());
            });
            comment.find("input[type=button]").on('click',function(){
                hidecomment();
            });
        }
    }
    function showmini(offset){
        mini.css({'top':offset.top-mini.height()-10,'left':offset.left});
        mini.show();
    }
    function hidemini(){
        mini.hide();
    }
    function showcomment(){
        comment.css({'top':mini.css('top'),'left':mini.css('left')});
        comment.show();
    }
    function hidecomment(){
        comment.hide();
    }
    function commentsubmit(){
        if(!validcomment()){
            return false;
        }
        jQuery.ajax({
            url: '/teacher/annotator/',
            data: commentform.serialize(),
            type: 'post',
            dataType: 'json',
            beforeSend: function() {
                comment.find('input[type=submit]').attr('disabled', 'disabled').val('加载中...');
            },
            success: function(response) {
                if(response.code == 0) {
                    smallnote('评论成功');
                    hidecomment();
                    var data = response.data;
                    if(data){
                        data.start = comment.find('input[name=start]').val();
                        data.end = comment.find('input[name=end]').val();
                        if(jQuery.trim(comment.find('input[name=annotator_id]').val())){
                            updatecomment(data);
                        }else{
                            addcomment(data);
                        }                        
                    }
                    comment.find('textarea[name=comment]').val('');
                    comment.find(':input[type=radio]:checked').removeAttr('checked');
                    selection.setSingleRange(range);
                }
                else {
                    smallnote(response.message || '服务器异常，请稍后再试！');
                }
            },
            error: function() {
                smallnote('服务器异常，请稍后再试！');
            },
            complete: function() {
                comment.find('input[type=submit]').removeAttr('disabled').val('确定');
            }
        });
    }
    function getpostion(){
        if(selection&&selection._ranges[0]){
            var range = selection._ranges[0];
            var startcontainer = range.startContainer.parentElement;
            var endcontainer = range.endContainer.parentElement;
            var startindex = range.startOffset;
            var endindex = range.endOffset;
            var startp = 0;
            var endp = 0;
            var alls = root.find('*');
            var len = alls.length;
            for(var i=0;i<len;i++){
                if(alls[i] == startcontainer ){
                    break;
                }
                startp++;
            }
            for(var i=0;i<len;i++){
                if(alls[i] == endcontainer ){
                    break;
                }
                endp++;
            }
            return {'startele':startp,'startindex':startindex,'endele':endp,'endindex':endindex};
        }
        return false;
    }
    function validcomment(){
        var contentarea = comment.find('textarea[name=comment]'),
            errordiv = comment.find('.alert-error');
        errordiv.hide();
        var commentstr = jQuery.trim(contentarea.val());
        if(!commentstr){
            errordiv.html('请输入评论内容');
            errordiv.show();
            return false;
        }
        contentarea.val(commentstr);
        if(!comment.find(':input[type=radio]:checked').length){
            errordiv.html('请选择评论的类型');
            errordiv.show();
            return false;
        }
        return true;
    }
    function checkcomment(position){
        for(var i=0;len = comments.length,i<len;i++){
            var cm = comments[i];
            if(cm.startele == position.startele&&cm.startindex == position.startindex &&cm.endele == position.endele&&cm.endindex == position.endindex){
                commentfocus(cm);
                return cm;
            }
        }
        return false;
    }
    function addcomment(data){
        var ele = jQuery(Mustache.render(Template, {annotator: {content:{comment:data.comment,type:data.type}}})).appendTo(DOMPanel.getPanel());
        ele = $(ele);
        data.ele = ele;
        ele.on('mouseover',function(){
            commentfocus(data);
        });
        ele.on('mouseout',function(){
            commentblur(data);
        });
        var index = -1;
        var len = comments.length;
        for(var i=0;i<len;i++){
            var cm = comments[i];
            if((cm.startele>data.startele)||(cm.startele==data.startele&&cm.startindex>data.startindex)){
                ele.css('top',cm.ele.css('top'));
                index = i;
                comments.splice(i,0,data);
                break;
            }
        }
        if(index == -1){
            if(len!=0){
                ele.css('top',comments[len-1].ele.offset().top+comments[len-1].ele.height()+5);
            }else{
                ele.css('top',root.offset().top);
            }
            comments.push(data);
        }else{
            for(var i=index;i<len;i++){
                var before = comments[i];
                var cm = comments[i+1];
                cm.ele.css('top',before.ele.offset().top+before.ele.height()+5);
            }
        }
    }
    function updatecomment(data){
        if(data){
            var cm = getcommentbyid(data.id);
            cm.comment = data.comment;
            cm.ele.find('.describe').html(data.comment);
            cm.ele.find('.type').html(data.type);
        }
    }
    function commentfocus(cm){
        var ele = cm.ele;
        if(ele){
            ele.addClass('focus')
        }
        focuscomment = cm;
        var alls = root.find('*');
        var startele = alls[cm.startele].childNodes[0];
        var endele = alls[cm.endele].childNodes[0];
        var range = rangy.createRange();
        range.setStart(startele,cm.startindex);
        range.setEnd(endele,cm.endindex);
        //var sel = rangy.getSelection();
        //sel.setSingleRange(range);
        rangy.init();
        cssApplier = rangy.createCssClassApplier('annotator-'+cm.type, {normalize: true});
        cssApplier.applyToRange(range);
        tools.log(root.html());
    }
    function commentblur(cm){
        var ele = cm?cm.ele:(focuscomment?focuscomment.ele:null);
        if(ele){
            ele.removeClass('focus');
            root.html(roothtml);
        }
    }
    function getcommentbyid(id){
        for(var i=0;len=comments.length,i<len;i++){
            var cm = comments[i];
            if(cm.id == id){
                return cm;
            }
        }
        return null;
    }
})(jQuery);
jQuery(function(){
    $('#annotator').annotator({datas:annotators});
});
