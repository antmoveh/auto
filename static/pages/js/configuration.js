var server_list = [];
var host_list = [];
var path_list = [];
var prod_list = [];
var module_list = {};
var config_list = {};
var config_content = [];
$(document).ready(function () {
    window_height = $(window).height();
    build_div_offset = $("div#configdetail").offset().top;
    build_div_height = window_height - build_div_offset - 10;
    $("div#configdetail").css("height", build_div_height);
    load_data();
});

function load_data() {
    var cid = get_href_v("cid");
    var aid = get_href_v("aid");
    if (cid == null)
        cid = "";
    else
        cid = "&cid=" + cid;
    if (aid == null)
        aid = "";
    else
        aid = "&aid=" + aid;
    $.get('action/?a=ldc' + cid + aid,
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
            }
            else {
                server_list = response["msg"]["server_list"];
                host_list = response["msg"]["host_list"];
                path_list = response["msg"]["path_list"];
                prod_list = response["msg"]["prod_list"];
                module_list = response["msg"]["module_list"];
                config_list = response["msg"]["config_list"];
                config_content = response["msg"]["content"];
                populate();
            }
        }
    );
}

function populate() {
    var pid = "0";
    var mid = "0";
    var cid = "0";
    var sid = "0";
    var hid = "0";
    var aid = "0";
    if (Object.keys(config_content).length > 0) {
        pid = config_content["pid"];
        mid = config_content["mid"];
        cid = config_content["cid"];
        sid = config_content["sid"];
        hid = config_content["hid"];
        aid = config_content["aid"];
    }
    add_droplist("prod", prod_list, pid, "请选择产品", $("table#file_name").find("div#prod"));
    if (cid != "0") {
        add_droplist("module", module_list[pid], mid, "请选择子模块", $("table#file_name").find("div#module"));
        add_droplist("config", config_list[pid][mid], cid, "请选择配置文件", $("table#file_name").find("div#config"));
    }
    add_droplist("servers", server_list, sid, "通用配置", $("table#file_name").find("div#servers"));
    if (sid != "0") {
        add_droplist("host", host_list[sid], hid, "请选择主机", $("table#file_name").find("div#host"));
        add_droplist("path", path_list[sid][hid], aid, "请选择路径", $("table#file_name").find("div#path"));
    }
    $("textarea[name=config]").val(config_content["content"]);
    if (config_content["content"] == "") {
        $("#disrealtion").attr("disabled", "true");
        $("#submit_test").attr("disabled", "true");
    } else {
        $("#relation").attr("disabled", "true");
        var aid = get_href_v("aid");
        if (aid != null)
            $("textarea[name=config]").removeAttr("disabled");
    }
}

function add_droplist(mode, list, id, title, obj) {
    if (list != undefined) {
        c_id = "0";
        s_p = title;
        o_s = "<ul class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu\">";
        o_e = "</ul>";
        s = "";
        o = "";
        for (index in list) {
            l_item = list[index];
            if (id == l_item[0].toString()) {
                c_id = l_item[0].toString();
                s_p = l_item[1];
                s = "<li><a href=\"#\" pid=\"" + c_id + "\">" + s_p + "</a></li><li class=\"divider\"></li>";
            }
            else {
                o += "<li><a href=\"#\" pid=\"" + l_item[0].toString() + "\">" + l_item[1] + "</a></li>";
            }
        }
        added = "<button type=\"button\" class=\"btn btn-default dropdown-toggle\" name=\"" + mode + "\" data-toggle=\"dropdown\" pid=\"" + c_id + "\">" + s_p + "<span class=\"caret\"></span></button>" + o_s + s + o + o_e;
        $(obj).html(added);
    }
}

function submit_test() {
    var cid = get_href_v("cid");
    var aid = get_href_v("aid");
    var conf = $("textarea[name=config]").val();
    if (cid == 0 || cid == null || aid == 0 || aid == null) {
        BootstrapDialog.show({title: "执行出错！", message: "清选择配置文件和部署路径"});
        return false;
    }
    var request = {"cid": cid, "aid": aid, "conf": conf};
    toggle_modal($("div#loading"), "show");
    $("button#submit_test").attr("disabled", "true");
    $.post('action/?a=set', {
            'request': JSON.stringify(request),
        },
        function (data, status) {
            toggle_modal($("div#loading"), "hide");
            $("button#submit_test").removeAttr("disabled");
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                window.location.reload();
                return true;
            }
        }
    );
}

function create_relation() {
    var cid = get_href_v("cid");
    var aid = get_href_v("aid");
    var path = $("div#ConfigModal").find(":text[name=path]").val();
    var in_p = $("div#ConfigModal").find("button[name=in_p]").attr("pid");
    $("div#ConfigModal").modal('hide');
    if (path.length < 1) {
        BootstrapDialog.show({title: "信息不全", message: "未提供配置文件路径信息"});
        return false;
    }
    var request = {"cid": cid, "aid": aid, "path": path, "in_p": in_p};
    $.post('action/?a=ncf', {
            'request': JSON.stringify(request),
        },
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                BootstrapDialog.show({title: "执行成功", message: response["msg"]});
                location.reload();
                return true;
            }
        }
    );
}

function read_config() {
    var mid = $("button[name=module]").attr("pid");
    if (mid == 0 || mid == undefined) {
        BootstrapDialog.show({title: "执行出错！", message: "请选择产品和模块，在更新配置"});
        return false;
    }
    $.get('action/?a=crc&mid=' + mid,
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                BootstrapDialog.show({title: "执行成功！", message: response["msg"]});
                return true;
            }
        }
    );
}

function relation() {
    var cid = get_href_v("cid");
    var aid = get_href_v("aid");
    if (cid == 0 || cid == null || aid == 0 || aid == null) {
        BootstrapDialog.show({title: "执行出错！", message: "清选择配置文件和部署路径"});
        return false;
    } else {
        $("div#ConfigModal").modal('show');
    }
}

function disrelation() {
    var cid = get_href_v("cid");
    var aid = get_href_v("aid");
    if (cid == 0 || cid == null || aid == 0 || aid == null) {
        BootstrapDialog.show({title: "执行出错！", message: "清选择配置文件和部署路径"});
        return false;
    }
    bsConfirm("是否确定取消关联,本操作无法恢复!").then(function (r) {
            if (r) {
                $.get("action/?a=rmc&cid=" + cid + "&aid=" + aid,
                    function (data, status) {
                        response = JSON.parse(data);
                        if (response["status"] == "FAILED") {
                            BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                            return false;
                        }
                        else {
                            window.location.reload();
                            return true;
                        }
                    }
                );
            }
            else
                return false;
        }
    );
}

function set_btn_txt(btn, pid, txt) {
    if ($(btn).attr("pid") != pid) {
        $(btn).html(txt + "<span class=\"caret\"></span>");
        $(btn).attr("pid", pid);
    }
}

$(function () {
        var cid = get_href_v("cid");
        var aid = get_href_v("aid");
        if (cid == null || aid == null || aid == "0") {
            $("#relation").attr("disabled", "true");
            $("#disrealtion").attr("disabled", "true");
            $("#submit_test").attr("disabled", "true");
        }
        $("div[name=in_p]").on('click', 'li a', function () {
                set_btn_txt($("div#ConfigModal").find("button[name=in_p]"), $(this).attr("pid"), $(this).text());
            }
        );
        $("div#prod").on('click', 'li a', function () {
                pid = $(this).attr("pid");
                set_btn_txt($("table#file_name").find("button[name=prod]"), pid, $(this).text());
                add_droplist("module", module_list[pid], "0", "请选择子模块", $("table#file_name").find("div#module"));
            }
        );
        $("div#module").on('click', 'li a', function () {
                pid = $("table#file_name").find("button[name=prod]").attr("pid");
                mid = $(this).attr("pid");
                set_btn_txt($("table#file_name").find("button[name=module]"), mid, $(this).text());
                add_droplist("config", config_list[pid][mid], "0", "请选择配置文件", $("table#file_name").find("div#config"));
            }
        );
        $("div#config").on('click', 'li a', function () {
                var aid = get_href_v("aid");
                if (aid == null)
                    var a = "";
                else
                    var a = "&aid=" + aid;
                window.location = "?m=configuration&cid=" + $(this).attr("pid") + a;
            }
        );
        $("div#servers").on('click', 'li a', function () {
                var sid = $(this).attr("pid");
                set_btn_txt($("table#file_name").find("button[name=servers]"), sid, $(this).text());
                add_droplist("host", host_list[sid], "0", "请选择主机", $("table#file_name").find("div#host"));
            }
        );
        $("div#host").on('click', 'li a', function () {
                var sid = $("table#file_name").find("button[name=servers]").attr("pid");
                var hid = $(this).attr("pid");
                set_btn_txt($("table#file_name").find("button[name=host]"), hid, $(this).text());
                add_droplist("path", path_list[sid][hid], "0", "请选择路径", $("table#file_name").find("div#path"));
            }
        );
        $("div#path").on('click', 'li a', function () {
                var cid = get_href_v("cid");
                if (cid == null) {
                    var c = "";
                    set_btn_txt($("table#file_name").find("button[name=path]"), $(this).attr("pid"), $(this).text());
                } else {
                    var c = "&cid=" + cid;
                    window.location = "?m=configuration&aid=" + $(this).attr("pid") + c;
                }
            }
        );
    }
);
