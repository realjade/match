// 显示班级
jQuery(function() {
    var myclasses = $('#myclasses'),
        selectclass = $("#selectclass");
    selectclass.click(function(event){
        $('#myclasses').css('top',$(this).offset().top+$(this).height()).css('left',$(this).offset().left).show();
        tools.cancelBubble(event);
        $(document).one('click', function(){
            myclasses.hide();
        });
    });
    myclasses.on('click','li',function(event){
        var classname = '';
        myclasses.find('input:checked').each(function(){
            classname+='@'+$(this).parents('li').find('label').text();
        });
        selectclass.html(classname);
    });
    
    $(document).ready(function(){
        selectclass.html('@'+$("#myclasses input:checked").parents('li').find('label').text());
    });
    
    
})
