$(function(){
    var template =  '{{#schools}}'+
                    '<tr data-id="{{id}}" data-name="{{name}}">'+
                    '  <td>{{name}}</td>'+
                    '  <td>{{city.name}}</td>'+
                    '  <td><a class="updateBtn btn btn-primary btn-sm">修改</></td>'+
                    '</tr>'+
                    '{{/schools}}'+
                    '{{#school_add}}'+
                    '<div class="school-add form-horizontal">'+
                    '{{^isUpdate}}'+
                    '  <div class="form-group">'+
                    '    <label class="col-lg-3 control-label">所属城市：</label>'+
                    '    <div class="col-lg-8">'+
                    '      <select class="city form-control"></select>'+
                    '    </div>'+
                    '  </div>'+
                    '{{/isUpdate}}'+
                    '  <div class="form-group">'+
                    '    <label class="col-lg-3 control-label">学校名称：</label>'+
                    '    <div class="col-lg-8">'+
                    '      <input class="form-control" name="schoolname" placeholder="学校名称" value="{{schoolname}}"/>'+
                    '    </div>'+
                    '  </div>'+
                    '</div>'+
                    '{{/school_add}}';
    var schoolList = $('#school_list');
    bindEvent();
    initSchoolList();
    //初始化
    function initSchoolList(){
        $.ajax({
            url: '/school/list/',
            type: "get",
            dataType: 'json',
            success: function(resp){
                if(resp && resp.code == 0){
                    var schools = resp.data,
                        tmpl = Mustache.render(template, {schools:schools});
                    schoolList.html(tmpl);
                }
            }
        });
    }
    //添加事件
    function bindEvent(){
        schoolList.on('click','.updateBtn',updateSchool);
    }
    //更新学校
    function updateSchool(){
        var schoolItem = $(this).parents('tr'),
            schoolName = schoolItem.attr('data-name'),
            schoolId = schoolItem.attr('data-id');
        var dialog = new CommonDialog({
            title: '更新学校',
            message: Mustache.render(template, {school_add:{isUpdate:true,schoolname:schoolName}}),
            isConfirm:true,
            okCallback: function(){
                var nameInput = this.find('input[name="schoolname"]'),
                    name = $.trim(nameInput.val());
                if(!name){
                    smallnote("请输入学校名称");
                    nameInput.parents('.form-group').addClass('has-error');
                    return false;
                }
                if(name == schoolName){
                    return true;
                }
                $.ajax({
                    url: '/school/update/',
                    data:{schoolid:schoolId,name:name},
                    type: "post",
                    dataType: 'json',
                    success: function(resp){
                        if(resp && resp.code == 0){
                            smallnote("更新学校成功");
                            initSchoolList();
                        }
                    }
                });
            }
        });
        dialog.find('input[name="schoolname"]').focus().inputEnter(function(){
            dialog.confirm();
        });
    }
    //添加学校
    $('#school_add').click(function(){
        var dialog = new CommonDialog({
            title: '添加学校',
            message: Mustache.render(template, {school_add:true}),
            isConfirm:true,
            okCallback: function(){
                var cityId = this.find('.city').val(),
                    nameInput = this.find('input[name="schoolname"]'),
                    name = $.trim(nameInput.val());
                if(!name){
                    smallnote("请输入学校名称");
                    nameInput.parents('.form-group').addClass('has-error');
                    return false;
                }
                $.ajax({
                    url: '/school/add/',
                    data:{cityid:cityId,name:name},
                    type: "post",
                    dataType: 'json',
                    success: function(resp){
                        if(resp && resp.code == 0){
                            smallnote("添加学校成功");
                            initSchoolList();
                        }
                    }
                });
            }
        });
        dialog.find('input[name="schoolname"]').focus().inputEnter(function(){
            dialog.confirm();
        });
        var citySelect = dialog.find('.city');
        $.ajax({
                url: '/city/list/',
                type: "get",
                dataType: 'json',
                success: function(resp){
                    if(resp&&resp.code == 0){
                        var data = resp.data;
                        for(var i = 0,len = data.length;i<len;i++){
                            var city = data[i];
                            $('<option value='+city.id+'>'+city.name+'</option>').appendTo(citySelect);
                        }
                    }
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
