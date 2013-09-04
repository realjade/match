$(document).bind("mobileinit", function(){
  $.extend(  $.mobile , {
    loadingMessage: "加载中,请耐心等待...",
    pageLoadErrorMessage:"对不起，页面加载失败，请稍后再试。",
    defaultPageTransition:'slide'
  });
});