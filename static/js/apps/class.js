jQuery(function(){
    //邀请信
    $('.class-invitation-btn').click(function(){
        $(this).siblings('.class-invitation-panel').find('.class-invitation').slideToggle();
    });
    
    // 发送邀请信到公共邮箱
    $('#send_invitation').click(function(){
        var class_id = $.trim($('.class-code').text());
        if(!class_id){
            return false;
        }
        jQuery.ajax({
            url : '/class/invitation/email/',
            data: { 'class_id' : class_id },
            dataType: 'json',
            type: "POST",
            success: function(res){
                if(res.code == 0) {
                    smallnote("发送成功");
                }else if(res.code==4004){
                    smallnote(res.message);
                }else{
                    smallnote("发送失败");
                }
            },
            error:function(){
                smallnote("发送失败");
            }
        });
    });
    
});
//创建班级
jQuery(function(){
    $('.createbtn').click(function(){
        var emailreg = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        var class_description = $('textarea[name=class_desc]').val();
        var class_name = $('input[name=classname]').val();
        var school = $('input[name=school]').val();
        var email = $('input[name=email]').val();
        if(!school){
            smallnote('请输入学校名称');
            return
        }
        if(!class_name){
            smallnote('请输入班级名称');
            return
        }
        
        if(email&&(!emailreg.test(email))){
            smallnote('邮箱格式错误')
            return
        }
        
        jQuery.ajax({
            url : '/api/class/create/',
            data: {'class_name' : class_name, 'school' : school, 'class_description' : class_description ,'email' : email},
            dataType: 'json',
            success: function(res){
                if(res.code == 0){
                    var data = res.data;
                    if(data.isexist){
                        smallnote('该班级已经存在，您已经成功加入了该班级');
                    }else{
                        smallnote('该班级成功创建');
                    }
                    $('.class-create').hide();
                    data.studentcount = 0;
                    data.teachercount = data.isexist?-1:1;
                    data.classup = true;
                    var donepanel = $('.create-done');
                    donepanel.show();
                    $(Mustache.render(Template,{'classitem':data})).appendTo(donepanel.find('.done-info'));
                    $('#up-btn').hide();
                    var invitation = $(Mustache.render(Template,{'class_invitation':data}));
                    invitation.appendTo(donepanel);
                    invitation.show();
                    donepanel.find('.isexist').html(data.isexist?'加入':'创建');
                }
            },
            error: function(){
            }
        });
    });
});
//加入班级
jQuery(function(){
    $('#join-search').click(function(){
        var class_id = $.trim($('input[name=classcode]').val());
        if(!class_id){
            return false;
        }
        jQuery.ajax({
            url : '/api/class/getclassbyid/',
            data: { 'class_id' : class_id },
            dataType: 'json',
            success: function(res){
                if(res.code == 0) {
                    if(res.data){
                        $('#class_info').html((Mustache.render(Template,{classitem:res.data})));
                        $('#join-ok').show();
                    }
                }else{
                    smallnote(res.message);
                    $('#join-ok').hide();
                    $('#class_info').html('');
                }
            },
            error:function(){
            }
        });
    });
    $('#join-ok').click(joinClass);
    function joinClass(){
        var class_id = $(".class-item").attr("id");
        if(!class_id){
            return false;
        }
        jQuery.ajax({
            url : '/api/class/join/',
            data: { 'class_id' : class_id },
            dataType: 'json',
            success: function(res){
                if(res.code == 0) {
                    smallnote('成功加入班级');
                }else{
                    smallnote(res.message);
                }
            },
            error:function(){
            }
        });
    }
});

// 修改班级
jQuery(function(){
    $("#up-btn").click(function(){
        id = $(this).attr("id");
        if(id == "up-btn"){
            dufaulttext = $("#up-text").text();
            $("#up-text").html("<textarea>"+dufaulttext+"</textarea>");
            $(this).html("<div class='edit_icon left'></div>保存");
            $(this).attr("id","save-btn");
        }else if(id == "save-btn"){
            var class_desc = $("#up-text textarea").val();
            var class_code = $(".class-code").text();
            jQuery.ajax({
                url: '/api/class/update/',
                data: {'class_id':class_code,'class_desc':class_desc},
                type: "POST",
                dataType: 'json',
                beforeSend: function(){
                    $("#save-btn").html("修改中");
                    $("#save-btn").attr("id","up-btn-ing");
                    return true;
                },
                success: function(res) {
                    $("#up-btn-ing").attr("id","save-btn");
                    if(res.code == 0) {
                        $("#up-text").text(class_desc);
                        $("#save-btn").html("<div class='edit_icon left'></div>编辑");
                        $("#save-btn").attr("id","up-btn");
                        smallnote('修改成功');
                    }else{
                        $("#save-btn").text("<div class='edit_icon left'></div>保存");
                        smallnote('修改失败');
                    }
                },
                error: function() {
                    $("#up-btn-ing").attr("id","save-btn");
                    $("#save-btn").text("<div class='edit_icon left'></div>保存");
                    smallnote('修改失败');
                }
            });
        };
    });
});



// 修改班级公共邮箱
jQuery(function(){
    $("#up-email-btn").click(function(){
        id = $(this).attr("id");
        if(id == "up-email-btn"){
            dufaulttext = $("#up-email-text").text();
            $("#up-email-text").html("<textarea>"+dufaulttext+"</textarea>");
            $(this).html("<div class='edit_icon left'></div>保存");
            $(this).attr("id","save-email-btn");
        }else if(id == "save-email-btn"){
            var class_email = $("#up-email-text textarea").val();
            var class_code = $(".class-code").text();
            jQuery.ajax({
                url: '/api/class/update/email/',
                data: {'class_id':class_code,'email':class_email},
                type: "POST",
                dataType: 'json',
                beforeSend: function(){
                    $("#save-email-btn").html("修改中");
                    $("#save-email-btn").attr("id","up-email-btn-ing");
                    return true;
                },
                success: function(res) {
                    $("#up-email-btn-ing").attr("id","save-email-btn");
                    if(res.code == 0) {
                        $("#up-email-text").text(class_email);
                        $("#save-email-btn").html("<div class='edit_icon left'></div>编辑");
                        $("#save-email-btn").attr("id","up-email-btn");
                        smallnote('修改成功');
                    }else{
                        $("#save-email-btn").text("<div class='edit_icon left'></div>保存");
                        smallnote('修改失败');
                    }
                },
                error: function() {
                    $("#up-btn-ing").attr("id","save-email-btn");
                    $("#save-email-btn").text("<div class='edit_icon left'></div>保存");
                    smallnote('修改失败');
                }
            });
        };
    });
});



// 修改班级班级学校
jQuery(function(){
    $("#up-school-btn").click(function(){
        id = $(this).attr("id");
        if(id == "up-school-btn"){
            dufaulttext = $("#up-school-text").text();
            $("#up-school-text").html("<textarea>"+dufaulttext+"</textarea>");
            $(this).html("<div class='edit_icon left'></div>保存");
            $(this).attr("id","save-school-btn");
        }else if(id == "save-school-btn"){
            var class_school = $("#up-school-text textarea").val();
            var class_code = $(".class-code").text();
            jQuery.ajax({
                url: '/api/class/update/school/',
                data: {'class_id':class_code,'school':class_school},
                type: "POST",
                dataType: 'json',
                beforeSend: function(){
                    $("#save-school-btn").html("修改中");
                    $("#save-school-btn").attr("id","up-school-btn-ing");
                    return true;
                },
                success: function(res) {
                    $("#up-school-btn-ing").attr("id","save-school-btn");
                    if(res.code == 0) {
                        $("#up-school-text").text(class_school);
                        $("#save-school-btn").html("<div class='edit_icon left'></div>编辑");
                        $("#save-school-btn").attr("id","up-school-btn");
                        smallnote('修改成功');
                    }else{
                        $("#save-school-btn").text("<div class='edit_icon left'></div>保存");
                        smallnote('修改失败');
                    }
                },
                error: function() {
                    $("#up-btn-ing").attr("id","save-school-btn");
                    $("#save-school-btn").text("<div class='edit_icon left'></div>保存");
                    smallnote('修改失败');
                }
            });
        };
    });
});
