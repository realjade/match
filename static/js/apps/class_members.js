jQuery(function(){
    $('li .delete_icon').click(function(){
        var this_obj = $(this);
        var name = this_obj.attr('data3');
        if(confirm("删除<"+name+">？")){
            var member_id = this_obj.attr('data');
            var class_id = this_obj.attr('data2');
            jQuery.ajax({
                url : '/class/member/delete/',
                data: {'member_id':member_id,'class_id':class_id},
                type: "POST",
                dataType: 'json',
                success: function(res){
                    if(res.code == 0){
                        smallnote('删除成功');
                        this_obj.parent().hide();
                    }else{
                        smallnote(res.message);
                    }
                },
                error: function(){
                    smallnote('删除失败');
                }
            });
        }
        
    });
});
