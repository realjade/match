jQuery(function(){
    jQuery('#exportall').click(function(){
        parents = jQuery('.ct_oper');
        checkboxes = jQuery('input:checkbox');
        classids = []
        for( var i = 0; i< parents.length;i++){
            p = parents[i];
            checkbox = checkboxes[i];
            if(checkbox.checked){
                classids.push(p.children[0].value);   
            }
        }
        url = '/teacher/export/?';
        for(var i=0;i<classids.length;i++){
            url += 'classid='+classids[i]+'&';
        }
        url = url.substring(0,url.length-1);
        window.open(url);
    });
});