//家长引导
jQuery(function(){
    $('#searchclass').click(function(){
        var class_id = $.trim($('input[name=classcode]').val());
        if(!class_id){
            return false;
        }
        jQuery.ajax({
            url : '/api/class/getclassbyid/',
            data: { 'class_id' : class_id },
            dataType: 'json',
            success: function(res){
                $('.classgrade').remove();
                $('#joinclass').unbind('click');
                if(res.code == 0) {
                    if(res.data){
                        $('.body .classinfo').append((Mustache.render(Template,{classgrade:res.data})));
                    }
                    $('#joinclass').removeClass('disabled');
                    $('#joinclass').removeClass('hide');
                    $('#joinclass').click(joinClass);
                }else{
                    smallnote(res.message);
                    $('#joinclass').addClass('disabled');
                }
            },
            error:function(){
                $('.classgrade').remove();
                $('#joinclass').addClass('disabled');
            }
        });
    });
    function joinClass(){
        var class_id = $('.classgrade').attr('data-class_id');
        if(!class_id){
            return false;
        }
        jQuery.ajax({
            url : '/api/class/join/',
            data: { 'class_id' : class_id ,'firstjoin':true},
            dataType: 'json',
            success: function(res){
                if(res.code == 0) {
                    $('#nextform').submit();
                }else{
                    smallnote(res.message);
                }
            },
            error:function(){
            }
        });
    }
});
