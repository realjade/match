
// 添加班级
jQuery(function(){
    
    // 初始化地区信息
    jQuery("#area").area({cache:region});
    
    jQuery('#step_1 .next .btn-primary').on('click', function(){
        var school = jQuery('#school .current');
        if(school.length){
            // next step
            var school_id = mySchool = school.attr('data-id');
            window.location.href = '/class/create/step2/?school_id='+school_id;
        }
        else{
            jQuery('#step_1 .next').append('<div class="error tip link">请先选择一个学校</div>');
            return false;
        }
    });

    jQuery('#myclass dd').delegate('a', 'click', function(){
        var self = jQuery(this);
        if(self.hasClass('current')){
            self.removeClass('current');
        }
        else{
            jQuery('#myclass dd').find('.current').removeClass('current');
            self.addClass('current');
        }
    });

    jQuery('#course8').on('change',function(){
        if(this.checked){
            jQuery('#course9').show();
        }
        else{
            jQuery('#course9').hide();
        }
    });
    
    jQuery('#step_2 .next .btn-primary').on('click', function(){
        var choosenClass = jQuery('#step_2 .current');
        if(choosenClass.length){
            var ccid = choosenClass.attr('data-id');
            window.location.href = '/class/create/step3/?class_id='+ccid;
        }
        else{
            var class_name = jQuery.trim(jQuery(':input[name=class_name]').val()),
                class_description = jQuery('textarea[name=class_description]').val(),
                school_id = jQuery('#schoolid').val();
            if(class_name.length){
                jQuery.ajax({
                    url : '/ajax/class/create/',
                    data: { 'school_id' : school_id, 'class_name' : class_name, 'class_description' : class_description },
                    dataType: 'json',
                    success: function(res){
                        if(res.code == 0){
                            window.location.href = '/class/create/step3/?class_id='+res.data.class_id;
                        }
                    },
                    error: function(){
                    }
                });
            }
            else{
                jQuery('#step_2 .next').append('<div class="error tip link">请选择一个班级或添加一个班级</div>');
                return false;
            }
        }
    });
});