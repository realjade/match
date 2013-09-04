jQuery(function() {
    jQuery('.regbtn').on('click', function(){
        var namereg = /[^\u4e00-\u9fa5]/;
        var emailreg = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        name_node = jQuery("input[name=studentname]");
        email_node = jQuery("input[name=studentemail]");
        pwd_node = jQuery("input[name=newpassword]");
        cpwd_node = jQuery("input[name=confirmpassword]");
        iagree_node = jQuery("input[name=iagree]");
        name = jQuery.trim(name_node.val());
        email = jQuery.trim(email_node.val());
        pwd = jQuery.trim(pwd_node.val());
        cpwd = jQuery.trim(cpwd_node.val());
        
        if(name.length<2||name.length>6||namereg.test(name)){
            name_node.siblings('.tips').find('.error').html('请输入真实有效的姓名（2-4个汉字）').show();
            return false;
        }else{
            name_node.siblings('.tips').find('.error').hide();
        }
        
        if(!email||!emailreg.test(email)){
            email_node.siblings('.tips').find('.error').html('请输入有效的邮箱地址').show();
            return false;
        }else{
            email_node.siblings('.tips').find('.error').hide();
        }
        
        if(pwd&&(pwd!=cpwd)){
            pwd_node.siblings('.tips').find('.error').html('两次输入不一致').show();
            return false;
        }else if(pwd.length<6||pwd.length>20){
            pwd_node.siblings('.tips').find('.error').html('密码为6-20位').show();
            return false;
        }
        else{
            pwd_node.siblings('.tips').find('.error').hide();
        }
        
        if(jQuery('input[name=iagree]:checked').length<1){
            iagree_node.siblings('.tips').find('.error').html('您需要同意我们的使用协议').show();
            return false;
        }
        else{
            iagree_node.siblings('.tips').find('.error').hide();
        }
        
        jQuery.ajax({
            url: '/parent/addchild/',
            data: {'name':name,'email':email,'pwd':pwd,'cpwd':cpwd},
            type: "POST",
            dataType: 'json',
            beforeSend: function(){
                smallnote('数据提交中...');
                return true;
            },
            success: function(response) {
                if(response.code=='0') {
                    smallnote('注册成功');
                    window.location.href="/parent/addchild/"+response.data.child_id+"/info/";
                }else{
                    smallnote(response.message);
                }
            },
            error: function() {
                smallnote('注册失败');
            }
        });
    })
})
