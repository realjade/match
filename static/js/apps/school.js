$(function(){
    var template =  '{{#schools}}'+
                    '<tr>'+
                    '  <td>{{name}}</td>'+
                    '  <td>{{city.name}}</td>'+
                    '  <td><a class="btn btn-primary btn-sm">修改</></td>'+
                    '</tr>'+
                    '{{#schools}}'+
                    '{{#school_add}}'+
                    '<div></div>'+
                    '{{/school_add}}';
    //添加学校
    $('#school_add').click(function(){
        var dialog = new CommonDialog({
            title: '添加学校',
            message: Mustache.render(template, {school_add:true}),
            isConfirm:true,
            okCallback: function(){
                jQuery.ajax({
                    url: visitor.rootPath+"/cancelAuthorization.json",
                    data:{id:id},
                    type: "post",
                    dataType: 'json',
                    success: function(response){
                        if(response.result && response.result == "success"){
                            smallnote("恭喜您，取消授权成功");
                            self.parents('.auth-item').remove();
                            $('.auth-item').length || noItem();
                        } else {
                            smallnote(response.return_msg,{patter:'error'});
                        }
                    },
                    error:function(){
                        smallnote("对不起，取消授权失败");
                    }
                });
            }
        });
    });
    $.fn.school = function(o){
        var self = $(this);
        init();
        function init() {
            self.options={
                callback:jQuery.noop
            };
            jQuery.extend(self.options, o);
            var cityPanel = self.cityPanel = $('<div class="school-city"></div>');
            cityPanel.appendTo(self);
            var schoolPanel = self.schoolPanel = $('<div class="school-panel"></div>');
            schoolPanel.appendTo(self);
            var createPanel = self.createPanel = $('<div class="school-create"><input name="schoolname" placeholder="学校名称"/><span class="createbtn btn btn-primary btn-sm">新建学校</span></div>');
            createPanel.appendTo(self);
            initCity();
            bindEvent();
        }
        function initCity(){
            $.ajax({
                url: '/city/list/',
                type: "GET",
                dataType: "json",
                success:function(resp){
                    if(resp&&resp.code == 0){
                        var data = resp.data;
                        for(var i = 0,len = data.length;i<len;i++){
                            var city = data[i];
                            $('<span class="city-item" data-id="'+city.id+'">'+city.name+'</span>').appendTo(cityPanel);
                        }
                        $('.city-item',self.cityPanel).first().trigger('click');
                    }
                }
            });
        }
        function bindEvent(){
            self.on('click','.city-item',changeSchool);
            self.on('click','.school-item',function(){
                self.schoolPanel.find('.selected').removeClass('selected');
                $(this).addClass('selected');
            });
            self.on('click','.createbtn',createSchool());
        }
        function changeSchool(){
            var city = $(this).text();
            self.cityPanel.find('.selected').removeClass('selected');
            $(this).addClass('selected');
            $.ajax({
                url: '/school/list/',
                data:{city:city},
                type: "GET",
                dataType: "json",
                success:function(resp){
                    if(resp&&resp.code == 0){
                        var data = resp.data;
                        for(var i = 0,len = data.length;i<len;i++){
                            var school = data[i];
                            $('<span class="school-item" data-id="'+school.id+'">'+school.name+'</span>').appendTo(schoolPanel);
                        }
                        $('.school-item',self.schoolPanel).first().trigger('click');
                    }
                }
            });
        }
        function createSchool(){
            var cityId = $('.city-item.selected',self.cityPanel).attr('data-id'),
                schoolInput = $('input[name="schoolname"]',self.createPanel),
                schoolName = $.trim(schoolInput.val());
            if(!schoolName){
                smallnote("请输入学校名称");
                return false;
            }else{
                $.ajax({
                url: '/school/add/',
                data:{cityid:cityId,name:schoolName},
                type: "GET",
                dataType: "json",
                success:function(resp){
                    if(resp&&resp.code == 0){
                        smallnote("新建学校成功");
                        $('.school-item',self.schoolPanel).first().trigger('click');
                    }
                }
            });
            }
        }
    };
});
