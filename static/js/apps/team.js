$(function(){
    var template = '{{#teams}}'+
                    '<tr>'+
                    '  <td>Mark</td>'+
                    '  <td>Otto</td>'+
                    '  <td>@mdo</td>'+
                    '  <td>@mdo</td>'+
                    '</tr>'+
                    '{{/teams}}';
   //添加球队
   $('#team_add').click(function(){
       var dialog = new CommonDialog({
            title: '添加球队',
            message: "确定要取消该应用的授权吗？取消后，该应用将无法访问您的任何数据和信息。",
            isConfirm:true,
            okCallback: function(){
                jQuery.ajax({
                    url: visitor.rootPath+"/cancelAuthorization.json",
                    data:{id:id},
                    type: "post",
                    dataType: 'json',
                    success: function(response){
                        if(response.result && response.result == "success"){
                            smallnote("恭喜您，取消授权成功");
                            self.parents('.auth-item').remove();
                            $('.auth-item').length || noItem();
                        } else {
                            smallnote(response.return_msg,{patter:'error'});
                        }
                    },
                    error:function(){
                        smallnote("对不起，取消授权失败");
                    }
                });
            }
        });
   });
});
