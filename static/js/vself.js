/**HTML各种功能判断**/
jQuery(function() {
   jQuery.support.placeholder = false;
   test = document.createElement('input');
   if('placeholder' in test) jQuery.support.placeholder = true;
});
/** 所有由脚本创建的DOM结构都应该放置在这个容器里**/
(function () {

    var panel = null;

    this.DOMPanel = {

        append: function (dom) {
            this.getPanel().append(dom);
        },

        prepend: function (dom) {
            this.getPanel().prepend(dom);
        },

        getPanel: function () {
            if (panel === null) {
                panel = jQuery('#domPanel');
                if (panel.size() === 0) {
                    panel = jQuery('<div id="domPanel" />').prependTo('body');
                }
            }

            return panel;
        }
    };

})();
/**指定位置**/
var Offset = function(element, o){  
    this.options = {
        top: null,
        left: null
    };
    jQuery.extend(this.options,o);
    this.initialize(element);   
};

Offset.prototype={
    initialize: function(element) {
        this.element = jQuery(element);
        this.setOffset();
        this.listenResize();
    },
    
    setOffset: function() {
        var left = this.options.left;
        // 如果LEFT没有指定 那么水平居中
        if(left == null) {
            left = (jQuery(window).width() - this.element.outerWidth()) / 2;
            left = Math.max(0, left);
        }
    
        var top = this.options.top;
        // 如果TOP没有指定 那么垂直居中
        if(top == null) {
            top = (jQuery(window).height() - this.element.outerHeight()) / 2;
            top = Math.max(0, top);
        }
        
        // 如果元素不是fixed定位 那么加上滚动条距离
        if(this.element.css('position') != 'fixed') {
            left += jQuery(document).scrollLeft();
            top += jQuery(document).scrollTop();
        }
        
        this.element.css({left:left, top:top});
    },
    
    listenResize: function() {
        var self = this;
        var contextProxy = function() {
            // 防止销魂元素后导致内存泄露（因为RESIZE事件是注册在WINDOW对象上 而不是ELEMENT元素上）
            if(self.element.parent().size() === 0) {
                jQuery(window).unbind('resize', contextProxy);
            }
            else if(self.element.is(':visible') && parseInt(self.element.css('top')) >= 0) {
                self.setOffset();
            }
        };
        jQuery(window).resize(contextProxy);
    }
};

/**提示smallnot**/
SmallNote=function(o){
    this.options={
        top: 0, time: 4000, pattern: null,text:'加载中...'
    };
    jQuery.extend(this.options, o);
    var element = this.element = jQuery('<div class="smallnote">' + this.options.text + '</div>');
    element.css({top: this.options.top});
    
    // 额外的定制样式 目前支持的只有一种： error
    // 如果传递额外的类型 需要自行定义style, 需要注意的是class会自动添加前缀：supernatant-[pattern]
    if(this.options.pattern !== null) {
        element.addClass('smallnote-' + this.options.pattern);
    }

    // 保持单例
    if(SmallNote.present) {
        SmallNote.present.remove();
    }
    SmallNote.present = this;
    DOMPanel.append(element);
    this.offset = new Offset(element, {top: this.options.top});
    // 启用销毁定时器
    this.destroyTimer();
};
SmallNote.prototype={
    destroyTimer: function() {
        var that = this;
        setTimeout(function() {
            that.element.fadeOut('slow', function() {
                that.remove();
            });
        }, this.options.time);
    },
    remove:function(){
        return this.element && this.element.remove();
    }
};
function smallnote(text,options){
    var o;
    if(options){
        options.text=text;
        o=options;
    }else{
        o={text:text};
    }
    new SmallNote(o);
}
/**顶部菜单效果**/ 
jQuery(function() {
    var panel = jQuery('#home-header .quick-menus'),
        items = panel.find('li').not('.split'),
        menus = items.find('.menu');
    
    // 阻止冒泡
    panel.click(function(e) {e.stopPropagation();});
    
    // 展开菜单
    menus.click(function() {
        var item = jQuery(jQuery(this).parent());
        item.toggleClass('selected');
        items.not(item).removeClass('selected');
    });
    
    // 鼠标左键点击隐藏菜单
    jQuery(document).on('click', function(e) {
        items.removeClass('selected');
    });
});

/**
 * 模板
 */
var Template = null;
jQuery(function() {
    Template = jQuery('#vselfTempl').html();
});

/**
 * placeholder实现
 */
jQuery(function () {
    if(!jQuery.support.placeholder){
        jQuery('input[placeholder],textarea[placeholder]').each(function(){
            var target = jQuery(this),
                parent = target.parent(),
                element = jQuery('<div class="placeholder">'
                              +'<label>'+target.attr('placeholder')+'</label>'
                           +'</div>');
            target.removeAttr('placeholder');
            element.append(target);
            parent.append(element);
        });
        $.fn.placeholder=function(o){
            var target = jQuery(this),
                parent = target.parent(),
                element = jQuery('<div class="placeholder">'
                              +'<label>'+target.attr('placeholder')+'</label>'
                           +'</div>');
            target.removeAttr('placeholder');
            element.append(target);
            parent.append(element);
        };
        jQuery('.placeholder input,.placeholder textarea').each(function () {
            var input = jQuery(this),
                label = jQuery(this).siblings('label');
            if (input.val()) {
                label.hide();
            }
        });
        jQuery('.placeholder input,.placeholder textarea').live('input propertychange focus blur keydown', function (e) {
            var input = jQuery(this),
                label = jQuery(this).siblings('label');
            if (input.val().length > 0 || (e.type == 'keydown' && !e.ctrlKey && !e.altKey && !e.shiftKey && e.keyCode != 8)) {
                if (!input.attr('readonly')) label.hide();
            }
            else {
                label.show();
            }
        });

        // 添加一个FOCUS状态
        jQuery('.placeholder input, .placeholder textarea').live('focus', function () {
            var input = jQuery(this);
            input.parent('.placeholder').addClass('focus');
        });
        jQuery('.placeholder input, .placeholder textarea').live('blur', function () {
            var input = jQuery(this);
            input.parent('.placeholder').removeClass('focus');
        });
        jQuery('.placeholder label').live('click', function () {
            var label = jQuery(this),
                input = jQuery(this).siblings('input,textarea');
            input.focus();
        });
    }
});

// 遮罩层
MaskLayer = function(o){
    if(MaskLayer.present)
        MaskLayer.present.getElement().remove();
    MaskLayer.present = this;
};
MaskLayer.prototype = {
    getElement: function () {
        if (!this.element) {
            this.element = jQuery('#masklayer');
            if (this.element.size() == 0) {
                this.element = jQuery('<div id="masklayer" />').appendTo(DOMPanel.getPanel());
            }
        }
        return this.element;
    },

    show: function () {
        this.getElement().show();
    },

    hide: function () {
        this.getElement().hide();
    }
};
// 弹窗
CommonDialog = function(o){
    this.options ={
        width: 465,
        height:null,
        title: '提示',
        message: '你木有事做吗？你真的木有事做吗？那你替我写封情书给布娃娃吧~',
    };
    jQuery.extend(this.options, o);
    this.init();
};
CommonDialog.prototype = {
    init:function () {
        var element = this.element = this.getElement();
        this.bindEvent();
        // 添加到页面
        DOMPanel.append(element);
        // 定位
        this.offset = new Offset(element, {
            top: this.options.top,
            left: this.options.left
        });
        this.mask = new MaskLayer();
        // 显示
        this.show();
    },
    getElement: function () {
        var fragment = ['<div class="common-dialog">', '<div class="wrapper">', '<header>', '<h3 class="title">',
        this.options.title, '</h3>','</header>', '<section>',
        this.options.message, '</section>', '</div>', '</div>'].join('');

        var element = jQuery(fragment);

        // 设置样式
        element.css({
            width: this.options.width
        });
        if(this.options.height){
            element.css({
                height: this.options.height
            });
        }
        return element;
    },
    show: function () {
        this.element.show();
        this.offset.setOffset();
        this.mask.show();
    },
    close: function (keepMask) {
        this.element.remove();
        this.mask.hide();
    },
    bindEvent: function () {
        var self = this;
        this.element.find('header .close').click(function () {
            self.close();
        });
    }
};
ImageRotate = function(o){
    this.options = {
        message:Mustache.render(Template,{'imagerotate':{'imgpath':o.imgpath}}),
        success:null,
        title:'请将视频旋转至正确的角度'
    };
    jQuery.extend(this.options, o);
    var dialog = new CommonDialog(this.options);
    dialog.show();
    this.dialog =dialog;
    this.element = dialog.element;
    this.bindEvent();
    this.rotate = 0;
};
ImageRotate.prototype = {
    bindEvent:function(){
        var self = this;
        self.element.on('click','.imgconfirm',function(){
            if(self.options.success)
                self.options.success.apply(self);
            self.element.find('.process').show();
            self.element.find('.imgconfirm').hide();
        });
        self.element.on('click','.rotate-left',function(){
            self.rotate -= 90;
            var imgpath = self.element.find('#imgpath');
            imgpath.rotate(self.rotate);
        });
        self.element.on('click','.rotate-right',function(){
            self.rotate += 90;
            var imgpath = self.element.find('#imgpath');
            imgpath.rotate(self.rotate);
        });
    },
    close:function(){
        var self  = this;
        self.dialog.close();
    }
};
ImageShow = function(o){
    this.options = {
        message:Mustache.render(Template,{'imageshow':{'images':this.wrapdata(o)}}),
        success:null,
        title:'图片查看',
        width:600,
        height:510,
        removed:null
    };
    jQuery.extend(this.options, o);
    var dialog = new CommonDialog(this.options);
    dialog.show();
    this.dialog =dialog;
    this.element = dialog.element;
    this.init();
    this.bindEvent();
};
ImageShow.prototype = {
    init:function(){
        var element = this.element,
            thumbnail = element.find('.thumbnails');
        thumbnail.css('width',thumbnail.find('li').length*90+'px');
        var firstimage = $('img',thumbnail).first();
        firstimage.addClass('active');
        $('.factimage',element).attr('src',firstimage.attr('data-path'));
        if(vself.visitor.isteacher){
            $('.remove',element).hide();
        }
        $('img',thumbnail).each(function(index){
            $(this).attr('data-index',index);
        });
    },
    bindEvent:function(){
        var self = this;
        var index = 0;
        var element = this.element,
                thumbnail = element.find('.thumbnails'),
                firstimg = thumbnail.find('img').first(),
                lastimg = thumbnail.find('img').last(),
                factimg = $('.factimage',element);
        $(".turnleft",element).click(function(){
            var current = $('img.active',element);
            if(current[0] != firstimg[0]){
                var prev = current.parent().prev().find('img');
                prev.addClass('active');
                current.removeClass('active');
                factimg.attr('src',prev.attr('data-path'));
                if((parseInt(thumbnail.css('left'),10)+prev.attr('data-index')*90)<=0&&parseInt(thumbnail.css('left'),10)<0){
                    var left = parseInt(thumbnail.css('left'),10);
                    thumbnail.animate({"left":left+90+"px"});
                    index = 0;
                }
            }
        });
        $(".turnright",element).click(function(){
            var current = $('img.active',element);
            if(current[0] != lastimg[0]){
                var next = current.parent().next().find('img');
                next.addClass('active');
                current.removeClass('active');
                factimg.attr('src',next.attr('data-path'));
                if((parseInt(thumbnail.css('left'),10)+next.attr('data-index')*90) >= 450){
                    var left = parseInt(thumbnail.css('left'),10);
                    thumbnail.animate({"left":left-90+"px"});
                    index = 5;
                }
            }
        });
        $("img",thumbnail).click(function(){
            var current = $('img.active',element);
            current.removeClass('active');
            $(this).addClass('active');
            factimg.attr('src',$(this).attr('data-path'));
        });
        factimg.click(function(){
            var path  = $(this).attr('src');
            window.open(document.location.protocol+'//'+document.location.host+path);
        });
        $('.close',element).click(function(){
            self.dialog.close();
        });
        $('.remove',element).click(function(){
            var current = $('img.active',element);
            if(confirm('确定要删除该图片？'))
                jQuery.ajax({
                    url: '/task/image/remove/',
                    data: {'path':current.attr('data-path'),'works_id':self.options.works_id},
                    type: "POST",
                    dataType: 'json',
                    success: function(response) {
                        if(response.code=='0') {
                            smallnote('删除成功');
                            var next = current.parent().next().find('img');
                            next.addClass('active');
                            current.remove();
                            factimg.attr('src',next.attr('data-path'));
                            if((parseInt(thumbnail.css('left'),10)+next.attr('data-index')*90) >= 450){
                                var left = parseInt(thumbnail.css('left'),10);
                                thumbnail.animate({"left":left-90+"px"});
                                index = 5;
                            }
                            if(self.options.removed){
                                self.options.removed.call(self,response.data);
                            }
                        }else{
                            smallnote(response.message);
                        }
                    },
                    error: function() {
                        smallnote('删除失败');
                    }
                });
        });
    },
    wrapdata:function(o){
        var result=[],
            thumbnails = o.thumbnails,
            pathes = o.pathes;
        for(var i=0,len=thumbnails.length;i<len;i++){
            result.push({'thumbnail':thumbnails[i],'path':pathes[i]});
        }
        return result;
    }
};
