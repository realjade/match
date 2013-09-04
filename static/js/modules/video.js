//加载视频
function load_flowplayer(id){
    flowplayer(id, {
        src: "/static/swf/flowplayer-3.2.11.swf",
        wmode: "opaque"
    },
    {
        plugins:  {
            controls:  {
                fullscreen: false
            },
            pseudo: {
                url: "/static/swf/flowplayer.pseudostreaming-3.2.9.swf"
            }
        },
        clip: {
            scaling: 'fit',
            autoPlay: true,
            accelerated: true,
            provider: 'pseudo'
        },
        onBeforeClick: function(){
            var el = jQuery(this.getParent());
            el.width(432);
            el.height(324);
            if(!el.parent().find('a.videostop')[0]){
                ael = jQuery('<a class="videostop video-btn btn">收起</a>')
                ael.click(function(){
                    var p = flowplayer(el.attr('id'));
                    p.close();
                    p.unload();
                })
                el.after(ael);
            }
            el.parent().find('a.videostop').show();
        },
        onUnload: function(){
            var el = jQuery(this.getParent());
            el.width(135);
            el.height(110);
            el.parent().find('a.videostop').hide();
        }
    });
}

function supports_video() {
  return !!document.createElement('video').canPlayType;
}

function supports_h264_baseline_video() {
  if (!supports_video()) { return false; }
  var v = document.createElement("video");
  return v.canPlayType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"');
}

function stop_videoplayer(id){
    var videoplayer = _V_(id);
    videoplayer.pause();
    videoplayer.size(248, 186);
    jQuery(videoplayer.el).find('a.videostop').hide();
}

function resize_videoplayer(){
    var videoplayer = this;
    var el = videoplayer.el;
    videoplayer.size(432, 324);
    if(!jQuery(el).find('a.videostop')[0]){
        ael = jQuery('<a class="videostop video-btn btn">收起</a>')
        ael.click(function(){
            stop_videoplayer(jQuery(el).attr('id'));
        })
        $(el).append(ael);
    }
    jQuery(videoplayer.el).find('a.videostop').show();
}

function load_videoplayer(id){
    if(using_html5){
        _V_.options.flash.swf = "/static/swf/video-js.swf";
        var videoplayer = _V_(id, {}, function(){});
        videoplayer.addEvent("play", resize_videoplayer);
    }else{
        load_flowplayer(id);
    }
}
