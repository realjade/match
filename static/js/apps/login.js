$(function(){
    var mobileInput = $('#mobile'),
        passInput = $('#password'),
        message = $('#message');
    function error(str){
        message.html(str);
        message.show();
    }
    function success(){
        message.hide();
    }
    function verifyMobile(){
        var mobile = $.trim(mobileInput.val());
        if(!mobile){
            error("请输入手机号码");
            return false;
        }
        if(!tools.isMobile(mobile)){
            error("请输入正确的手机号码");
            return false;
        }
        success();
        mobileInput.val(mobile);
        return true;
    }
    function veriryPwd(){
        var pwd = passInput.val();
        if(!pwd){
            error("请输入密码");
            return false;
        }
        return true;
    }
    $('#loginForm').submit(function(){
        if(verifyMobile() && veriryPwd()){
            return true;
        }
        return false;
    });
});
