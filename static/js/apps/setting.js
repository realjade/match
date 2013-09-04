//孩子账户相关
jQuery(function() {
    var childaccountform = jQuery('form[name=childaccount]'),
        childemailInput = childaccountform.find('input[name=username]'),
        childpwdInput = childaccountform.find('input[name=password]');
    var checkusername = function(){
        var username = jQuery.trim(childemailInput.val());
        childemailInput.val(username);
        var usernamepanel = jQuery('#childusernamediv'),
            pwdpanel = jQuery('#childpwddiv'),
            nicknamepanel = jQuery('#childnicknamediv');
        usernamepanel.removeClass('error');
        jQuery.ajax({
            url: '/account/exist/student/',
            data: childaccountform.serialize(),
            type: 'post',
            dataType: 'json',
            success: function(response) {
                //存在的学生账户
                if(response.code == 0) {
                    pwdpanel.find('.alert').show(); 
                    nicknamepanel.find('#nickname').val(response.data.nickname);
                    nicknamepanel.find('#nickname').attr('disabled', 'disabled').addClass('disabled');          
                    usernamepanel.find('.help-inline').hide();
                    jQuery('.childaccountsubmit').removeAttr('disabled', 'disabled').removeClass('disabled');
                }
                //不存在的账户
                if(response.code == 3001) {
                    pwdpanel.find('.alert').hide();                 
                    usernamepanel.find('.help-inline').hide();
                    nicknamepanel.find('#nickname').val('').removeAttr('disabled', 'disabled').removeClass('disabled');
                    jQuery('.childaccountsubmit').removeAttr('disabled', 'disabled').removeClass('disabled');
                }
                //存在的其他类型账户
                if(response.code == 3004 || response.code == 3005) {
                    pwdpanel.find('.alert').hide();                 
                    usernamepanel.addClass('error');
                    usernamepanel.find('.help-inline').html("该账户不是学生身份的账户").show();
                    jQuery('.childaccountsubmit').attr('disabled', 'disabled').addClass('disabled');
                    nicknamepanel.find('#nickname').val('').removeAttr('disabled', 'disabled').removeClass('disabled');                 
                }
            }
        });
    };
    childemailInput.on('change',checkusername);
    childaccountform.submit(function() {
        jQuery.ajax({
            url: '/home/settings/addstudent/',
            data: childaccountform.serialize(),
            type: 'post',
            dataType: 'json',
            beforeSend: function() {
                jQuery('.childaccountsubmit').attr('disabled', 'disabled').val('加载中...');
            },
            success: function(response) {
                if(response.code == 0) {
                    smallnote('添加孩子账户成功');
                    jQuery(Mustache.render(Template, {child: response.data})).prependTo(jQuery('#childrentable'));
                }
                else {
                    smallnote(response.message || '服务器异常，请稍后再试！');
                }
            },
            error: function() {
                smallnote('服务器异常，请稍后再试！');
            },
            complete: function() {
                jQuery('.childaccountsubmit').removeAttr('disabled').val('确定');
            }
        }); 
        return false;
    });
    //删除相关
    var deleteStd = jQuery('#deleteStd'),
        childrentable = jQuery('#childrentable');
    childrentable.on('click','.deletebtn',function(){
        deleteStd.data('child',jQuery(this).attr('data-userid'));
    });
    deleteStd.on('click','.ok',function(){
        var userid = deleteStd.data('child');
        deleteStd.modal('hide');
        smallnote("删除中...");
        if(userid){
            jQuery.ajax({
                url: '/home/settings/deletestudent/',
                data: {'child':userid},
                type: 'post',
                dataType: 'json',               
                success: function(response) {
                    if(response.code == 0) {
                        smallnote('删除孩子账户成功');
                        childrentable.find('a[data-userid='+userid+']').parents('tr').remove();
                    }
                    else {
                        smallnote(response.message || '服务器异常，请稍后再试！');
                    }
                },
                error: function() {
                    smallnote('服务器异常，请稍后再试！');
                }
            });
        }
    });
});

// 账户相关
jQuery(function() { 
    //修改账户信息
    var accountform = jQuery('form[name=account]'),
        nicknameInput = accountform.find('input[name=nickname]'),
        emailInput = accountform.find('input[name=email]'),
        mobileInput = accountform.find('input[name=mobile]');
    
    accountform.submit(function() { 
        // 获取用户填写的账户信息
        var nickname = jQuery.trim(nicknameInput.val()),
            email = jQuery.trim(emailInput.val()),
            mobile= jQuery.trim(mobileInput.val());
        
        // 检查真实姓名
        if(nickname.length <= 0) {
            nicknameInput.parent().parent().addClass('error');
            nicknameInput.siblings().text('姓名不能为空');
            return false;
        }
        else {
            nicknameInput.parent().parent().removeClass('error');
            nicknameInput.siblings().text('');
            // jQuery('.password .tips').show().filter('.error').hide();
        }
        
        //检查邮箱
        if(email != '') {
            var res = /^[0-9a-zA-Z_\-\.]+@[0-9a-zA-Z_\-]+(\.[0-9a-zA-Z_\-]+)*$/; 
            if(!res.test(email)){
                emailInput.parent().parent().addClass('error');
                emailInput.siblings().text('请输入有效的邮箱地址').show();
                return false;
            }
            else{
                emailInput.parent().parent().removeClass('error');
                emailInput.siblings().text('');
            }
        }
        else{
            emailInput.parent().parent().removeClass('error');
            emailInput.siblings().text('');
        }
        
        //检查mobile
        if(mobile != '') {
            var res2 = /^(1(3|5|8))\d{9}$/;
            if(!res2.test(mobile)){
                mobileInput.parent().parent().addClass('error');
                mobileInput.siblings().text('请输入有效的手机号码').show();
                return false;
            }
            else{
                mobileInput.parent().parent().removeClass('error');
                mobileInput.siblings().text('');
            }
        }
        else{
            mobileInput.parent().parent().removeClass('error');
            mobileInput.siblings().text('');
        }
        
        jQuery.ajax({
            url: '/home/settings/account/',
            data: accountform.serialize(),
            type: 'post',
            dataType: 'json',
            beforeSend: function() {
                jQuery('.accountsubmit').attr('disabled', 'disabled').val('加载中...');
            },
            success: function(response) {
                if(response.code == 0) {
                    smallnote('修改账户信息成功');
                }
                else {
                    smallnote(response.message || '服务器异常，请稍后再试！');
                }
            },
            error: function() {
                smallnote('服务器异常，请稍后再试！');
            },
            complete: function() {
                jQuery('.accountsubmit').removeAttr('disabled').val('确定');
            }
        }); 
        return false;
    });
    
    //修改密码
    var passform = jQuery('form[name=password]'),
        passwordInput = passform.find('input[name=oldpwd]'),
        newpwdInput = passform.find('input[name=newpwd]'),
        repeatInput = passform.find('input[name=newpwd2]');
    
    passform.submit(function() {    
        // 获取用户填写的账户信息
        var password = jQuery.trim(passwordInput.val()),
            newpwd = jQuery.trim(newpwdInput.val()),
            repeat = jQuery.trim(repeatInput.val());
        
        // 检查密码
        if(password.length <= 0) {
            jQuery('.password .tips').hide().filter('.error').show();
            passwordInput.focus();
            return false;
        }
        else {
            jQuery('.password .tips').show().filter('.error').hide();
        }
        
        //判断是否重设密码
        if(newpwd != '') {
            if(newpwd.length < 6) {
                jQuery('.newpwd .tips').hide().filter('.error').show();
                newpwdInput.focus();
                return false;
            }
            else if(newpwd != repeat) {
                jQuery('.repeat .tips').hide().filter('.error').show();
                repeatInput.focus();
                return false;
            }
        }
        jQuery.ajax({
            url: '/home/settings/modifypass/',
            data: passform.serialize(),
            type: 'post',
            dataType: 'json',
            beforeSend: function() {
                jQuery('.modifypwd').attr('disabled', 'disabled').val('加载中...');
            },
            success: function(response) {
                if(response.code == 0) {
                    smallnote('修改账户信息成功');
                }
                else {
                    smallnote(response.message || '服务器异常，请稍后再试！');
                }
            },
            error: function() {
                smallnote('服务器异常，请稍后再试！');
            },
            complete: function() {
                jQuery('.modifypwd').removeAttr('disabled').val('修改');
            }
        }); 
        return false;
    });
});
