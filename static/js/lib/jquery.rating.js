jQuery(function() {
    jQuery('.star').each(function(){
        $(this).jRating({});
    });
});
jQuery(function() {
    jQuery('.showstar').each(function(){
        $(this).jRating({isDisabled:true});
    });
});

(function($) {
    $.fn.jRating = function(op) {
        var options={
            length:10,
            isDisabled:false
        }
        options = $.extend(options,op);
        var target = $(this);
        var starlength = parseInt(target.attr('data-star')?target.attr('data-star'):0);
        target.attr('data-star',starlength);
        initstar(starlength);
        if(!options.isDisabled){
            $('.flowerstar',target).mouseover(function(){
                refreshstar($(this).attr('data-index'));
            });
            $('.flowerstar',target).mouseout(function(){
                refreshstar(target.attr('data-star'));
            });
            $('.flowerstar',target).click(function(){
                target.attr('data-star',$(this).attr('data-index'));
            });
        }else{
            if(!target.attr('title'))
                target.attr('title','共'+starlength+'颗小红花')
        }
        function initstar(redcount){
            for(var i=1;i<=options.length;i++){
                var classname = 'grayflower';
                if(i<=redcount)
                    classname = 'redflower';
                $('<div class="'+classname+' flowerstar" data-index="'+i+'"></div>').appendTo(target);
            }
            $('<div class="clear"></div>').appendTo(target);
            if(!options.isDisabled){
                $('.flowerstar',target).each(function(){
                    $(this).attr('title',$(this).attr('data-index')+'颗小红花');
                });
            }
        }
        function refreshstar(redindex){
            $('.flowerstar',target).each(function(){
                if(parseInt($(this).attr('data-index'))<=redindex){
                    $(this).removeClass('grayflower');
                    $(this).addClass('redflower');
                }else{
                    $(this).removeClass('redflower');
                    $(this).addClass('grayflower');
                }
            });
        }
    }
})(jQuery);
