// 一个元素收缩到另一个元素位置
jQuery(function() {
    $.fn.shrink = function(target){
        var srcele = $(this),
            copyele = $(this).clone(true);
        copyele.css({'position':'absolute',
            'top':$(this).offset().top,
            'left':$(this).offset().left,
            'border':'1px solid #999'});
        copyele.appendTo($(this).parent());
        copyele.animate({
            'top':target.offset().top,
            'left':target.offset().left,
            'width':target.width(),
            'height':target.height()
            }, 500, function() {
                copyele.remove();
            });
    }
});
//滚动条滚动到一个元素位置
jQuery(function() {
    $.fn.scroll = function(callback){
        var target = $(this);
        jQuery('html, body').animate({
                scrollTop: (target.offset().top-50 || 0)
        }, 500, 'easeOutExpo', function () {
            return callback && callback();
        });
    }
});