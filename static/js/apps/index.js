
jQuery(function(){
    $('.beishuPlayer').each(function(){
        load_videoplayer($(this).attr('id'));
    });
});
// 标签
var changeIntroStatus = function(n){
    switch(n)
    {
    case 2:
        jQuery('#intro').show();
        jQuery('#info').hide();
        jQuery('#video1').hide();
        jQuery('#video2').hide()
        break;
    case 3:
        jQuery('#video1').show();
        jQuery('#info').hide();
        jQuery('#intro').hide();
        jQuery('#video2').hide()
        break;
    case 4:
        jQuery('#video2').show()
        jQuery('#info').hide();
        jQuery('#intro').hide();
        jQuery('#video1').hide();
        break;
    default:
        jQuery('#info').show();
        jQuery('#intro').hide();
        jQuery('#video1').hide();
        jQuery('#video2').hide()
    }
}
// html5
var using_html5 = false;
var flash_messages = [];
function show_flash_messages(){
    if (flash_messages != undefined && flash_messages != null && flash_messages != ""){
      var m = flash_messages.join(', ');
      smallnote(m);
    }
}



/**判断浏览器的版本**/
jQuery(function() {
    if ($.browser.msie) {
        if ($.browser.version == "6.0" || $.browser.version == "7.0"){
            var element = $('<div class="brower-error"><a href="/static/tools/chrome高级浏览器.exe"><div class="bigshadow"></div></a><div class="browser-error-close">继续访问背书吧</div></div>');
            DOMPanel.append(element);
            this.offset = new Offset(element, {top: 0});
            element.find('.browser-error-close').click(function(){
                element.remove();
            });
        }
    }
});
/* index.js */
jQuery(function(){
    // 幻灯片图片滑动
    //jQuery("html,body").animate({scrollTop:jQuery("#slide").offset().top},800);
    var a =0;
    jQuery("#slide>.slide_box").click(function(){
        var a = jQuery(this).find(".navbox>.navtitle a").attr("href");
        window.open(a);
        return !1 
    }),
    jQuery("#slide>.slide_box").mouseover(function(){
        var b =jQuery(this).index();
        if(b!= a){
            jQuery("#slide .navsumary").hide();
            jQuery(this).find(".navbox>.navsumary").show();
            var c = "bg" + (b + 1);
            b < a && (jQuery.browser.msie?(
                jQuery(".slide_box").stop().animate({backgroundPositionX: "640px"}, 0).removeClass("bg1 bg2 bg3 bg4").addClass(c),
                jQuery("#box_1").parent().stop().animate({backgroundPositionX: "0"}, 100),
                jQuery("#box_2").parent().stop().animate({backgroundPositionX:"-160px"},200),
                jQuery("#box_3").parent().stop().animate({backgroundPositionX: "-320px"},300),
                jQuery("#box_4").parent().stop().animate({backgroundPositionX: "-480px"},400,
                function(){
                    jQuery(".slide_box,#slide").removeClass("bg1 bg2 bg3 bg4").addClass(c);
                }
            )):(
                jQuery(".slide_box").stop().animate({backgroundPosition:"640px 0"},0).removeClass("bg1 bg2 bg3 bg4").addClass(c),
                jQuery("#box_1").parent().stop().animate({backgroundPosition:"0 0"},100),
                jQuery("#box_2").parent().stop().animate({backgroundPosition:"-160px 0"},200),
                jQuery("#box_3").parent().stop().animate({backgroundPosition:"-320px 0"},300),
                jQuery("#box_4").parent().stop().animate({backgroundPosition: "-480px 0"},400,
                function(){
                    jQuery(".slide_box,#slide").removeClass("bg1 bg2 bg3 bg4").addClass(c)
                }
            )), a = b),b > a &&(jQuery.browser.msie?(
                jQuery(".slide_box").stop().animate({backgroundPositionX: "-640px" },0).removeClass("bg1 bg2 bg3 bg4").addClass(c),
                jQuery("#box_1").stop().parent().animate({backgroundPositionX:"0"},400,
                    function(){
                        jQuery(".slide_box,#slide").removeClass("bg1 bg2 bg3 bg4").addClass(c)
                    }
                ),
                jQuery("#box_2").parent().stop().animate({ backgroundPositionX: "-160px" }, 300),
                jQuery("#box_3").parent().stop().animate({backgroundPositionX: "-320px"}, 200),
                jQuery("#box_4").parent().stop().animate({backgroundPositionX: "-480px"}, 100)):(jQuery(".slide_box").stop().animate({backgroundPosition:"-650px 0"},0).removeClass("bg1 bg2 bg3 bg4").addClass(c),
                jQuery("#box_1").stop().parent().animate({backgroundPosition:"0 0"},400,
                    function(){
                        jQuery(".slide_box,#slide").removeClass("bg1 bg2 bg3 bg4").addClass(c)
                    }
                ),
                jQuery("#box_2").parent().stop().animate({backgroundPosition:"-160px 0"}, 300),
                jQuery("#box_3").parent().stop().animate({backgroundPosition:"-320px 0"},200),
                jQuery("#box_4").parent().stop().animate({backgroundPosition: "-480px 0"},100)
            ), a = b)
        }
    });
        
});
