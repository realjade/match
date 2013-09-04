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
            el.width(640);
            el.height(480);
            el.parent().find('a.videostop').show();
        },
        onUnload: function(){
            var el = jQuery(this.getParent());
            el.width(640);
            el.height(480);
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
    videoplayer.size(640, 480);
    jQuery(videoplayer.el).find('a.videostop').hide();
}

function resize_videoplayer(){
    var videoplayer = this;
    var el = videoplayer.el;
    videoplayer.size(640, 480);
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