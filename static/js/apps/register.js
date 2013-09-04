jQuery(function() {
    function checkReg(){
        var namereg = /[^\u4e00-\u9fa5]/,
            mobilereg = /^1[3|5|8][0-9]\d{8}$/,
            emailreg = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        var role = $(':input[name=role]').val();
        var result = {};
        result.role = role;
        if(role == 'teacher'){
            var teachername = jQuery(':input[name=teachername]'),
                teachermobile = jQuery(':input[name=teachermobile]'),
                teacheremail = jQuery(':input[name=teacheremail]');
                //teachermobilecode = jQuery(':input[name=mobilecode]');
            result.course = $('#course_opt').val();
            var name = jQuery.trim(teachername.val());
                mobile = jQuery.trim(teachermobile.val());
                email = jQuery.trim(teacheremail.val());
                //mobilecode = jQuery.trim(teachermobilecode.val());
                if(name.length<1){
                    teachername.siblings('.tips').find('.error').html('姓名不能为空').show();
                    return false;
                }
                else if(name.length<2||name.length>6||namereg.test(name)){
                    teachername.siblings('.tips').find('.error').html('请输入真实有效的姓名（2-4个汉字）').show();
                    return false;
                }
                else{
                    teachername.siblings('.tips').find('.error').hide();
                    result.nickname = name;
                }
                if(!mobile){
                    teachermobile.siblings('.tips').find('.error').html('请输入手机号').show();
                    return false;
                }else{
                    teachermobile.siblings('.tips').find('.error').hide();
                }
                if(mobile&&(!mobilereg.test(mobile))){
                    teachermobile.siblings('.tips').find('.error').html('请输入有效的手机号码').show();
                    return false;
                }
                else{
                    teachermobile.siblings('.tips').find('.error').hide();
                    result.mobile = mobile;
                }
                /**
                if(!mobilecode){
                    teachermobilecode.siblings('.tips').find('.error').html('请输入手机验证码').show();
                }else{
                    teachermobilecode.siblings('.tips').find('.error').hide();
                    result.mobilecode = mobilecode;
                }
                */
                
                if(email&&(!emailreg.test(email))){
                    teacheremail.siblings('.tips').find('.error').html('请输入有效的邮箱地址').show();
                    return false;
                }
                else{
                    teacheremail.siblings('.tips').find('.error').hide();
                    result.email = email;
                }
        }else if(role == 'student'){
            var parentname = jQuery(':input[name=parentname]'),
                parentmobile = jQuery(':input[name=parentmobile]'),
                studentname = jQuery(':input[name=studentname]'),
                studentemail = jQuery(':input[name=studentemail]');
                pname = jQuery.trim(parentname.val());
                mobile = jQuery.trim(parentmobile.val());
                sname = jQuery.trim(studentname.val());
                email = jQuery.trim(studentemail.val());

            if(pname.length<1){
                parentname.siblings('.tips').find('.error').html('姓名不能为空').show();
                return false;
            }
            else if(pname.length<2||pname.length>6||namereg.test(pname)){
                parentname.siblings('.tips').find('.error').html('请输入真实有效的姓名（2-4个汉字）').show();
                return false;
            }
            else{
                parentname.siblings('.tips').find('.error').hide();
                result.pname = pname;
            }
            if(!mobilereg.test(mobile)){
                parentmobile.siblings('.tips').find('.error').html('请输入有效的手机号码').show();
                return false;
            }
            else{
                parentmobile.siblings('.tips').find('.error').hide();
                result.mobile = mobile;
            }
            if(sname.length<1){
                studentname.siblings('.tips').find('.error').html('姓名不能为空').show();
                return false;
            }
            else if(sname.length<2||sname.length>6||namereg.test(sname)){
                studentname.siblings('.tips').find('.error').html('请输入真实有效的姓名（2-4个汉字）').show();
                return false;
            }
            else{
                studentname.siblings('.tips').find('.error').hide();
                result.sname = sname;
            }
            if(!emailreg.test(email)){
                studentemail.siblings('.tips').find('.error').html('请输入有效的邮箱地址').show();
                return false;
            }
            else{
                studentemail.siblings('.tips').find('.error').hide();
                result.email = email;
            }
        }

        var newpassword = jQuery(':input[name=newpassword]'),
            confirmpassword = jQuery(':input[name=confirmpassword]'),
            iagree = jQuery('#iagree');
        var password = jQuery.trim(newpassword.val());
            password2 = jQuery.trim(confirmpassword.val());

        if(password&&(password!=password2)){
            confirmpassword.siblings('.tips').find('.error').html('两次输入不一致').show();
            return false;
        }
        else{
            confirmpassword.siblings('.tips').find('.error').hide();
        }
        if(password.length<6||password.length>20){
            newpassword.siblings('.tips').find('.error').html('密码为6-20位').show();
            return false;
        }
        else{
            newpassword.siblings('.tips').find('.error').hide();
        }
        if(jQuery('input[name=iagree]:checked').length<1){
            iagree.siblings('.tips').find('.error').html('您需要同意我们的使用协议').show();
            return false;
        }
        else{
            iagree.siblings('.tips').find('.error').hide();
        }

        result.password = password;
        result.password2 = password2;
        return result;
    }
    
    /**
    $("#valimobile").click(function(){
        var mobilereg = /^1[3|5|8][0-9]\d{8}$/;
        var teachermobile = jQuery(':input[name=teachermobile]');
        var mobile = jQuery.trim(teachermobile.val());
        if(!mobile||(!mobilereg.test(mobile))){
            teachermobile.siblings('.tips').find('.error').html('请输入有效的手机号码').show();
            return false;
        }
        else{
            teachermobile.siblings('.tips').find('.error').hide();
        }
        jQuery.ajax({
            url: '/api/register/mobilecode/',
            data: {'mobile':mobile},
            type: "POST",
            dataType: 'json',
            success: function(response) {
                if(response.code=='0') {
                    smallnote('验证码发送成功');
                }else{
                    smallnote(response.message);
                }
            },
            error: function() {
                smallnote('验证码发送失败');
            }
        });
    })
    */
    //注册
    jQuery('.regbtn').on('click', function(){
        var result = checkReg();
        if(result){
            jQuery.ajax({
            url: '/api/register/',
            data: result,
            type: "POST",
            dataType: 'json',
            beforeSend: function(){
                smallnote('数据提交中...');
                return true;
            },
            success: function(response) {
                if(response.code=='0') {
                    smallnote('注册成功');
                    if(result.role){
                        window.location.href='/guide/';
                    }
                }else{
                    smallnote(response.message);
                }
            },
            error: function() {
                smallnote('注册失败');
            }
        });
        }
    });
});
