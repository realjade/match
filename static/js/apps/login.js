// 登录
jQuery(function(){

	jQuery(':input[name=username]').focus();

	// 只做非空检验
	var checkEmpty = function(){
		
		if(!jQuery(':input[name=username]').val()) {
			//jQuery('div.control-group:first').addClass('error');
			//jQuery('div.control-group:first .controls .help-inline').text('请输入用户名');
		}
		else if(!jQuery(':input[name=password]').val()){
			//jQuery('div.control-group:last').addClass('error');
			//jQuery('div.control-group:last .controls .help-inline').text('请输入密码');
		}
		else{
			//jQuery('div.control-group').removeClass('error');
			//jQuery('div.control-group .controls .help-inline').text('');
		}
	};
	// checkEmpty();
	// 提交
	jQuery('form[name=login]').submit(function(){
	
		//alert('HERE');
		//checkEmpty();

		if(jQuery('form div.error').length){
			return false;
		}

	});
	
});