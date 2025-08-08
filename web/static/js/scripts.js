function include(file) {
    var script = document.createElement('script');
    script.src = "/static/js/"+file+".js";
    script.type = 'text/javascript';
    script.defer = true;
    document.getElementsByTagName('head').item(0).appendChild(script);
    console.log("included "+file);
}
include("ajax_call");
include("get_time");
include("reload");