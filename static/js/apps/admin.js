jQuery(function() {
    function getprovince(){
        var province = [];
        $.each(region,function(i,item){
            province.push({'region_id':item.region_id,'region_name':item.region_name});
        });
        return province;
    }
    
    function getcity(proid){
        var city = [];
        var cities = region["provinces"+proid].city;
        if(!cities){
            return false;
        }
        $.each(cities,function(i,item){
            city.push({'region_id':item.region_id,'region_name':item.region_name,'provinceid':proid});
        });
        return city
    }
    
    function getcounty(proid,cityid){
        var county = [];
        var counties = region["provinces"+proid].city["cities"+cityid].county;
        if(!counties){
            return false;
        }
        $.each(counties,function(i,item){
            county.push({'region_id':item.region_id,'region_name':item.region_name,'provinceid':proid,'cityid':cityid});
        });
        return county;
    }
    
    function optionformat(item){
        return "<option data="+ item['region_id'] +" value="+item['region_name']+">"+ item['region_name'] +"</option>"
    }
    
    $(document).ready(function(){
        $.each(getprovince(),function(i,item){
            $("#province").append(optionformat(item));
        })
        
        $.each(getcity(2),function(i,item){
            $("#city").append(optionformat(item));
        });
        
        $.each(getcounty(2,52),function(i,item){
            $("#county").append(optionformat(item));
        });
    });
    
    $("#province").change(function(){
        proid = $("#province :selected").attr("data");
        $("#city").html("");
        $.each(getcity(proid),function(i,item){
            $("#city").append(optionformat(item));
        });
    });
    
    $("#city").change(function(){
        proid = $("#province :selected").attr("data");
        cityid = $("#city :selected").attr("data");
        $("#county").html("");
        $.each(getcounty(proid, cityid),function(i,item){
            $("#county").append(optionformat(item));
        });
    });
    
});
