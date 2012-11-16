$('#popbox_bg').click(function() { $('#popbox_bg').hide(); });
$('#popbox_bg').append('[ <a href="#" onclick="return false" id="popbox_close">close</a> ]');
$('#popbox').click(function() { return false; });
$('#popbox_close').click(function() { $('#popbox_bg').hide(); });
function popbox_show(url,type) { 
    $('#popbox').html('LOADING...');
    $('#popbox_bg').show(100);
    switch(type) { 
        case "video":
            var player_location = "/gamestatic/popbox/player.swf"
            var flv_html = ""
                +"<embed "
                +"type='application/x-shockwave-flash' "
                +"id='popbox_embed' "
                +"name='popbox_embed' "
                +"src='"+player_location+"' "
                +"width='470' "
                +"height='320' "
                +"bgcolor='black' "
                +"allowscriptaccess='always' "
                +"allowfullscreen='true' "
                +"wmode='transparent' "
                +"flashvars='file="+url+"&backcolor=000000&frontcolor=ffeecc&lightcolor=A86C00&screencolor=111000&autostart=true' /> ";
            $('#popbox').html(flv_html);
            break;
        case "image":
            $('#popbox').html('<img id="popbox_img" src="'+url+'" />'); 
            break;
    }
    return false;
}
