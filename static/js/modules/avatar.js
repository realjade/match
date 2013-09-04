/**
 * @author JadeZhang
 * @context avatar jquery plugin
 */
$(function() {
	var _template = '{{#uploadHead}}'+
					'<div id="uploadHeadWidget">'+
					'  <div class="mainView clearfix">'+
					'    <div class="image-panel">'+
					'      <div class="upload-loading"></div>'+
					'      <div class="upload-info">'+
					'        <div class="upload-area">'+
					'          <form name="uploaddiv" target="{{target}}" action="" method="post" enctype="multipart/form-data">'+
					'            <button type="button" class="upload-btn gbtn"><i class="aicon-avatarselect"></i>选择图片</button>'+
					'            <input type="file" class="upload-ctrl" name="avatar" />'+
					'          </form>'+
					'        </div>'+
					'        <div class="standard">仅支持jpg，jpeg，gif，png，bmp图片文件，且文件小于1M<br/>拖拽或缩放虚线框 生成满意的头像</div>'+
					'      </div>'+
					'    </div>'+
					'    <div class="image-thumn">'+
					'      <div class="normal">'+
					'        <span><img alt="normal" /></span>'+
					'        <div class="sizedesc">200 * 200 像素</div>'+
					'      </div>'+
					'      <div class="tiny">'+
					'        <span><img alt="tiny" /></span>'+
					'        <div class="sizedesc">100 * 100 像素</div>'+
					'      </div>'+
					'      <div class="mini">'+
					'        <span><img alt="mini" /></span>'+
					'        <div class="sizedesc">30 * 30 像素</div>'+
					'      </div>'+
					'    </div>'+
					'    <iframe name="{{target}}" src="" class="async-upload"></iframe>'+
					'  </div>'+
					'</div>'+
					'{{/uploadHead}}'+
					'{{#uploadAgain}}'+
					'<div id="uploadAgain">'+
					'  <form name="uploadAgain" target="{{target}}" action="" method="post" enctype="multipart/form-data">'+
					'    <input type="button" value="+ 重新选择" class="upload-btn" />'+
					'    <input type="file" class="upload-ctrl" name="avatar" />'+
					'  </form>'+
					'</div>'+
					'{{/uploadAgain}}';
	$.fn.avatar = function(o) {
		var self = $(this),
			previewUrl = '';
		init();
		function init() {
			self.options={
				actionUrl:'',
				previewUrl:'',
				cutUrl:'',
				proxyUrl:'',
				ratio:1,
        		thumbnail:true,
        		isCut:true,
        		title:'上传头像',
        		noImage:'请上传您的头像',
				callback:jQuery.noop
			};
			jQuery.extend(self.options, o);
			self.click(show);
		}
		
		function show() {
			//tools.cancelDomain();
			self.image = null;
			self.target = 'asyncUpload_' + tools.uniqueID();
			var w = 715;
			if(!self.options.thumbnail){
				w = 500;
			}
			var dialog = self.dialog = new CommonDialog({
				title: self.options.title,
				width: w,
				message: $.trim(Mustache.render(_template, {uploadHead: {target: self.target}})),
				isConfirm:true,
				okCallback: function() {
					if(self.options.isCut){
						if(self.image == null) {
							error(self.options.noImage);
							return false;
						}
						savediv();
					}else{
						if(previewUrl){
							self.options.callback.call(self,true,{previewUrl:previewUrl});
						}else{
							error(self.options.noImage);
							return false;
						}
					}
					
					success();
				},
				cancelCallback:function(){
					success();
				}
			});
			//frames[self.target].document.domain = window.location.hostname.split('.').reverse().slice(0,2).reverse().join('.');
			dialog.getFooter().prepend($.trim(Mustache.render(_template, {uploadAgain: {target: self.target}})));
			dialog.find('form').attr('action',self.options.actionUrl);
			dialog.find('iframe').attr('src',self.options.proxyUrl);
			dialog.getFooter().find('form').attr('action',self.options.actionUrl);
			if(!self.options.thumbnail){
				dialog.find('.image-thumn').hide();
			}
			bindEvent();
			// 如果没有上传 可以在这里进行临时模拟调试程序
			// this.createCropper('/webstatic/images/girl.jpg');
		}
		
		function createCropper(imgSrc) {
			self.image = imgSrc;
			
			var boxWidth = 425,
				boxHeight = 392,
				expect = 200;
			var that = this,
				temp = new Image();
			temp.onload = function() {
				// 填充图片
				jQuery('#uploadHeadWidget .image-panel').html('<div class="crop-panel"><img src="" alt="crop" class="cropholder" /></div>');
				var cropPanel = jQuery('#uploadHeadWidget .crop-panel');
				cropPanel.hide();
				var cropper = self.cropper = jQuery.Jcrop(cropPanel.find('img'), {
					aspectRatio: self.options.ratio,
					minSize: [30, 30],
					boxWidth: boxWidth,
					boxHeight: boxHeight,
					allowSelect: false,
					keySupport: false
				});
				cropPanel.show();
				cropper.setImage(imgSrc, function() {
					// 为了视觉效果 居中显示
					var holder = this.ui.holder,
						wsize = this.getWidgetSize(),
						zoom = wsize[0] / temp.width;
						
					holder.css({left: (boxWidth - wsize[0])/2, top: (boxHeight - wsize[1])/2});
					
					// 打开选取框
					var x1 = (wsize[0] - expect) / 2 / zoom,
						y1 = (wsize[1] - expect) / 2 / zoom,
						x2 = ((wsize[0] - expect) / 2 + expect ) / zoom,
						y2 = ((wsize[1] - expect) / 2 + expect ) / zoom;
						
					cropper.setOptions({onChange: changeCoords.bind(that)});
					cropper.setSelect(temp.width > expect ? [x1, y1, x2, y2] : [0, 0, temp.width, temp.height]);
					
				});
				if(!self.options.isCut){
					$('.jcrop-holder div',self.dialog.element).hide();
				}
			};
			temp.src = imgSrc;
		}
		
		function changeCoords(coords) {
			var scale = 200 / coords.w,
				bounds = self.cropper.getBounds();
			
			var normalImage = jQuery('#uploadHeadWidget .normal img');
			normalImage.attr('src', self.image).css({width:bounds[0]*scale, marginLeft:-coords.x*scale, marginTop: -coords.y*scale});
			normalImage.show();

			scale = 100 / coords.w;
			var tinyImage = jQuery('#uploadHeadWidget .tiny img');
			tinyImage.attr('src', self.image).css({width:bounds[0]*scale, marginLeft:-coords.x*scale, marginTop: -coords.y*scale});
			tinyImage.show();

			scale = 30 / coords.w;
			var miniImage = jQuery('#uploadHeadWidget .mini img');
			miniImage.attr('src', self.image).css({width:bounds[0]*scale, marginLeft:-coords.x*scale, marginTop: -coords.y*scale});
			miniImage.show();
		}
		
		function savediv() {
			var coord = self.cropper.tellSelect();

			jQuery.ajax({
				url: self.options.cutUrl,
				type: 'post',
				data: {x:parseInt(coord.x,10), y:parseInt(coord.y), w:parseInt(coord.w,10), h:parseInt(coord.h,10)},
				dataType: 'json',
				beforeSend:function(){
					smallnote('正在处理，请稍等...');
				},
				success: function(res) {
					if(res&&res.code == 0){
						self.options.callback.call(self,true,res);
					}else{
						self.options.callback.call(self,false,res);
					}
				}
			});
		}
		
		function bindEvent() {
			// 自动上传
			self.dialog.find('input[name=avatar]').change(function() {
				var file = jQuery(this),
					address = file.val(),
					suffix = address.substring(address.lastIndexOf('.') + 1).toLowerCase();
					
				if(!{'jpg':1,'jpeg':1, 'gif':1, 'png':1, 'bmp':1}[suffix]) {
					error('仅支持jpg，jpeg，gif，png，bmp图片文件');
					file.val('');
					return false;
				}else{
					success();
				}
				jQuery(this.form).submit();
				jQuery('#uploadAgain').show();
				self.dialog.find('.image-panel .upload-loading').show();
				self.dialog.find('.image-panel .upload-info').hide();
			});
			
			self.dialog.find('iframe').bind('load', function() {
				var frame = frames[self.target];
				/*try{
	                frame.document.domain = window.location.hostname.split('.').reverse().slice(0,2).reverse().join('.');
	            }catch(e){
	                tools.log(e);
	            }*/
				try {
					var res = JSON.parse(frame.document.body.innerHTML);
					if(res) {
						success();
						if(res.code == 0) {
							var src =  (res.previewUrl||self.options.previewUrl)+'?t='+Date.now();
							previewUrl = res.previewUrl||self.options.previewUrl;
							createCropper(src);
							frame.document.body.innerHTML = '';	
						}
						else {
							error(res.msg);
							self.dialog.find('.image-panel .upload-info').show();
						}
					}
				}
				catch(e) {}
			});
		}

		function error(txt){
			smallnote(txt,{pattern:'error',top:self.dialog.getHeader().offset().top+3,hold:true});
		}
		function success(){
			smallnote('',{remove:true});
		}
	};
});