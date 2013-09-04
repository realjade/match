(function () {
tools = {
    cookie:{
        set:function(name,value){
            var exp  = new Date();
            exp.setTime(exp.getTime() + 30*24*60*60*1000);   
            document.cookie = name + '='+ escape (value) + ';expires=' + exp.toGMTString()+';path=/';
        },
        get:function(name){
            var arr = document.cookie.match(new RegExp('(^| )'+name+'=([^;]*)(;|$)'));
            if(arr != null) return unescape(arr[2]); return null;
        },
        del:function(name){
            var exp = new Date();
            exp.setTime(exp.getTime() - 1);
            var cval=api.cookie.getCookie(name);
            if(cval!=null){
                document.cookie= name + '='+cval+';expires='+exp.toGMTString()+';path=/';
                document.cookie= name + '='+cval+';expires='+exp.toGMTString();
            }
        }
    },
    log:function(_message){
        if('console' in window && 'log' in window.console){
            console.log(_message);
        }
    },
    // 纵向滚动到指定位置
    scrollTween: function(y, callback) {
        jQuery('html, body').animate({
                scrollTop: (y || 0)
        }, 500, 'easeOutExpo', function () {
            return callback && callback();
        });
    },
    
    // 取消选中的文本
    clearSelect: function() {
        if(document.selection && document.selection.empty) {
            document.selection.empty();
        }
        else if(window.getSelection) {
            window.getSelection().removeAllRanges();
        }
    },
    
    // 计算字符串的字节长度
    countByte: function(str) {
        var size = 0;
        for (var i = 0, l = str.length; i < l; i++) {
            size += str.charCodeAt(i) > 255 ? 2 : 1;
        }

        return size;
    },
    
    // 根据字节截取长度
    substrByByte: function (str, limit) {
        for (var i = 1, l = str.length + 1; i < l; i++) {
            if (this.countByte(str.substring(0, i)) > limit) {
                return str.substring(0, i - 1);
            }
        }

        return str;
    },
    
    //获得URL中键值对
    paramOfUrl: function (url) {
        url = url || location.href;
        var paramSuit = url.substring(url.indexOf('?') + 1).split("&");
        var paramObj = {};
        for (var i = 0; i < paramSuit.length; i++) {
            var param = paramSuit[i].split('=');
            if (param.length == 2) {
                var key = decodeURIComponent(param[0]);
                var val = decodeURIComponent(param[1]);
                if (paramObj.hasOwnProperty(key)) {
                    paramObj[key] = jQuery.makeArray(paramObj[key]);
                    paramObj[key].push(val);
                }
                else {
                    paramObj[key] = val;
                }
            }
        }
        return paramObj;
    },
    
    cancelBubble: function(_event) {
        if (_event && _event.stopPropagation)
            _event.stopPropagation();
        else
            window.event.cancelBubble=true;
    },
    
    cancelDefault: function(_event) {
        if(_event && _event.preventDefault){
            _event.preventDefault();
        } else{
            window.event.returnValue = false;
        }
        return false;
    },
    
    reflow: function(obj) {
        jQuery(obj).each(function() {
            jQuery(this).hide().show();
        });
    },
    
    dateformat:function(datetime,type){
        if(type=='full'){
            return new Date(datetime).strftime('%Y年%m月%d日, %H:%M:%S');
        }
        if(!type||type=='medium'){
            return new Date(datetime).strftime('%m月%d日%H:%M');
        }
    }
}
Date.prototype.strftime = function(format) {
    var self = this;
    function padding(n, p) {
        if(n < 10) {
            return (p || '0') + n;
        }
        return n;
    }
    function repl(s, c) {
        switch(c) {
            case 'd':
                return padding(self.getDate());
            case 'e':
                return self.getDate();
            case 'u':
                return self.getDay() + 1;
            case 'w':
                return self.getDay();
            case 'm':
                return padding(self.getMonth() + 1);
            case 'C':
                return parseInt(self.getFullYear() / 20 - 1, 10);
            case 'y':
                return padding(self.getFullYear() % 100);
            case 'Y':
                return self.getFullYear();
            case 'H':
                return padding(self.getHours());
            case 'I':
                return padding(self.getHours() % 12);
            case 'l':
                return padding(self.getHours() % 12, ' ');
            case 'M':
                return padding(self.getMinutes());
            case 'p':
                return self.getHours() <12 ? 'AM' : 'PM';
            case 'P':
                return self.getHours() <12 ? 'am' : 'pm';
            case 'r':
                return self.strftime('%I:%M:%S %p');
            case 'R':
                return self.strftime('%H:%M');
            case 'S':
                return padding(self.getSeconds());
            case 'T':
                return self.strftime('%H:%M:%S');
            case 'D':
                return self.strftime('%m/%d/%Y');
            case 'F':
                return self.strftime('%Y-%m-%d');
            case 's':
                return parseInt(self.getTime()/1000, 10);
            case 'x':
                return self.toLocaleDateString();
            case 'X':
                return self.toLocaleTimeString();
            case 'n':
                return '\n';
            case 't':
                return '\t';
            case '%':
                return '%';
            default:
                return self.strftime(c);
        }
        return c;
    }
    var ret = format.replace(/%(\w)/g, repl);
    return ret;
};
})();