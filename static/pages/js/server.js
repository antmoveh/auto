var servers = [];
var server_info = [];
$(document).ready(function () {
    window_height = $(window).height();
    build_div_offset = $("div#server_div").offset().top;
    build_div_height = window_height - build_div_offset - 50;
    $("div#server_div").css("height", build_div_height);
    load_page();
});

function load_page() {
    sid = get_href_v("sid");
    if (sid == null)
        sid = "";
    else
        sid = "&sid=" + sid;
    $.get("action/?a=sld" + sid, function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                servers = response["msg"]["servers"];
                server_info = response["msg"]["server_info"];
                show_server_list();
                populate_info();
            }
        }
    );
}

function add_host(host_info) {
    if (host_info == undefined) {
        host_id = " value=\"0\"";
        host_address = "";
        ssh_port = "";
        ssh_user = " value=\"kdy_yanfa\"";
        ssh_pass = " value=\"12345678\"";
        ssh_key = " value=\"/data/applications/auto/id_rsa\"";
        paths = [];
    }
    else {
        host_id = " value=\"" + host_info["id"] + "\"";
        host_address = " value=\"" + host_info["host_address"] + "\"";
        ssh_port = " value=\"" + host_info["ssh_port"] + "\"";
        ssh_user = " value=\"" + host_info["ssh_user"] + "\"";
        ssh_pass = " value=\"" + host_info["ssh_pass"] + "\"";
        ssh_key = " value=\"" + host_info["ssh_key"] + "\"";
        paths = host_info["paths"];
    }
    added = "<table class=\"table table-bordered\" name=\"host\"><tbody><tr><td width=\"33%\" name=\"host_num\"></td><input type=\"hidden\" name=\"id\"" + host_id + ">";
    added += "<td width=\"33%\"><div class=\"input-group\"><span class=\"input-group-addon\">主机地址：</span><input type=\"text\" class=\"form-control\" name=\"host_address\"" + host_address + "></div></td>";
    added += "<td width=\"34%\"><div class=\"input-group\"><span class=\"input-group-addon\">SSH端口：</span><input type=\"text\" class=\"form-control\" name=\"ssh_port\"" + ssh_port + "></div></td></tr>";
    added += "<tr><td><div class=\"input-group\"><span class=\"input-group-addon\">SSH账号：</span><input type=\"text\" class=\"form-control\" name=\"ssh_user\"" + ssh_user + "></div></td>";
    added += "<td><div class=\"input-group\"><span class=\"input-group-addon\">SSH密码：</span><input type=\"password\" class=\"form-control\" name=\"ssh_pass\"" + ssh_pass + "></div></td>";
    added += "<td><div class=\"input-group\"><span class=\"input-group-addon\" disabled>SSH密钥文件：</span><input type=\"text\" class=\"form-control\" name=\"ssh_key\"" + ssh_key + "></div></td></tr>";
    added += "<tr><td colspan=\"3\"><table class=\"table\" name=\"host_paths\"><thead><tr><th width=\"50%\">部署路径：</th><th width=\"50%\">";
    added += "<button type=\"button\" class=\"btn btn-primary\" onclick=\"add_path(this);\">添加路径</button> <button type=\"button\" class=\"btn btn-primary\" onclick=\"default_paths(this);\">使用模板</button></th></tr></thead></table>";
    path_num = 1;
    for (index in Object.keys(paths)) {
        added += add_path(undefined, paths[index], path_num);
        path_num++;
    }
    added += "</td></tr></tbody></table>";
    $("div#hosts").append(added);
    set_host_num();
}

function set_host_num() {
    num = 1;
    hosts = $("table[name=host] td[name=host_num]");
    hosts.each(function () {
        $(this).html("<button class=\"btn btn-default\" type=\"button\" onclick=\"del_obj(this);\">主机" + num + "&nbsp;&nbsp;&nbsp;&nbsp;<b><font color=\"red\">x</font></b></button>");
        num++;
    })
}

function default_paths(obj) {
    paths = {
        1: ["release", "release.war", "/data/applications/tomcat7_release", "release.war"],
        2: ["data", "data.war", "/data/applications/tomcat7_data", "data.war"],
        3: ["website", "website.war", "/data/applications/tomcat7_website", "website.war"],
        4: ["movie", "movie.war", "/data/applications/tomcat7_movie", "movie.war"],
    };
    added = "";
    for (i = 1; i < 5; i++) {
        path = paths[i];
        path_info = {"id": "0", "module": path[0], "src_name": path[1], "des_path": path[2], "des_name": path[3]};
        added += add_path(undefined, path_info, "1");
    }
    container = $(obj).parent().parent().parent().parent().parent();
    container.append(added);
    set_path_num(container);
}

function add_path(obj, path_info, path_num) {
    if (obj == undefined) {
        added = "";
        if (path_info != undefined) {
            path_id = " value=\"" + path_info["id"] + "\"";
            module = " value=\"" + path_info["module"] + "\"";
            src_name = " value=\"" + path_info["src_name"] + "\"";
            des_path = " value=\"" + path_info["des_path"] + "\"";
            des_name = " value=\"" + path_info["des_name"] + "\"";
            added = "<table class=\"table\" name=\"host_path\"><tbody><tr><td width=\"33%\" name=\"path_num\">";
            added += "<button class=\"btn btn-default\" type=\"button\" onclick=\"del_obj(this);\">部署路径" + path_num + "&nbsp;&nbsp;&nbsp;&nbsp;<b><font color=\"red\">x</font></b></button></td>";
            added += "<input type=\"hidden\" name=\"id\"" + path_id + ">";
            added += "<td width=\"33%\"><div class=\"input-group\"><span class=\"input-group-addon\">模块名称：</span><input type=\"text\" class=\"form-control\" name=\"path_module\"" + module + "></div></td>";
            added += "<td width=\"34%\"><div class=\"input-group\"><span class=\"input-group-addon\">来源文件：</span><input type=\"text\" class=\"form-control\" name=\"path_src\"" + src_name + " disabled></div></td></tr>";
            added += "<tr><td colspan=\"2\"><div class=\"input-group col-lg-12\"><span class=\"input-group-addon\">路径地址：</span><input type=\"text\" class=\"form-control\" name=\"path\"" + des_path + " disabled></div></td>";
            added += "<td><div class=\"input-group\"><span class=\"input-group-addon\">目的文件：</span><input type=\"text\" class=\"form-control\" name=\"path_des\"" + des_name + " disabled></div></td></tr></tbody></table>";
        }
        return added;
    }
    else {
        added = "<table class=\"table\" name=\"host_path\"><tbody><tr><td width=\"33%\" name=\"path_num\"></td><input type=\"hidden\" name=\"id\" value=\"0\">";
        added += "<td width=\"33%\"><div class=\"input-group\"><span class=\"input-group-addon\">模块名称：</span><input type=\"text\" class=\"form-control\" name=\"path_module\"></div></td>";
        added += "<td width=\"34%\"><div class=\"input-group\"><span class=\"input-group-addon\">来源文件：</span><input type=\"text\" class=\"form-control\" name=\"path_src\" disabled></div></td></tr>";
        added += "<tr><td colspan=\"2\"><div class=\"input-group col-lg-12\"><span class=\"input-group-addon\">路径地址：</span><input type=\"text\" class=\"form-control\" name=\"path\" disabled></div></td>";
        added += "<td><div class=\"input-group\"><span class=\"input-group-addon\">目的文件：</span><input type=\"text\" class=\"form-control\" name=\"path_des\" disabled></div></td></tr></tbody></table>";
        container = $(obj).parent().parent().parent().parent().parent();
        container.append(added);
        set_path_num(container);
        return true;
    }
}

function set_path_num(container) {
    num = 1;
    paths = $(container).children("table[name=host_path]");
    paths.each(function () {
        path_num = $(this).children().children().children().first();
        $(path_num).html("<button class=\"btn btn-default\" type=\"button\" onclick=\"del_obj(this);\">部署路径" + num + "&nbsp;&nbsp;&nbsp;&nbsp;<b><font color=\"red\">x</font></b></button>");
        num++;
    })
}

function add_database(db_info) {
    if (db_info == undefined) {
        db_id = " value=\"0\"";
        db_module = "";
        db_host = "";
        db_port = "";
        db_name = "";
        db_user = "";
        db_pass = "";
    }
    else {
        db_id = " value=\"" + db_info["id"] + "\"";
        db_module = " value=\"" + db_info["db_module"] + "\"";
        db_host = " value=\"" + db_info["db_host"] + "\"";
        db_port = " value=\"" + db_info["db_port"] + "\"";
        db_name = " value=\"" + db_info["db_name"] + "\"";
        db_user = " value=\"" + db_info["db_user"] + "\"";
        db_pass = " value=\"" + db_info["db_pass"] + "\"";
    }
    added = "<table class=\"table table-bordered\" name=\"database\"><tbody><tr><td name=\"db_num\"><div>a</div></td><input type=\"hidden\" name=\"id\"" + db_id + ">";
    added += "<td colspan=\"2\"><div class=\"input-group col-lg-12\"><span class=\"input-group-addon\">模块：</span><input type=\"text\" class=\"form-control\" name=\"db_module\"" + db_module + "></div></td></tr>";
    added += "<tr><td colspan=\"2\"><div class=\"input-group col-lg-12\"><span class=\"input-group-addon\">地址：</span><input type=\"text\" class=\"form-control\" name=\"db_host\"" + db_host + "></div></td>";
    added += "<td><div class=\"input-group\"><span class=\"input-group-addon\">端口：</span><input type=\"text\" class=\"form-control\" name=\"db_port\"" + db_port + "></div></td></tr>";
    added += "<tr><td width=\"33%\"><div class=\"input-group\"><span class=\"input-group-addon\">数据库名：</span><input type=\"text\" class=\"form-control\" name=\"db_name\"" + db_name + "></div></td>";
    added += "<td width=\"34%\"><div class=\"input-group\"><span class=\"input-group-addon\">账号：</span><input type=\"text\" class=\"form-control\" name=\"db_user\"" + db_user + "></div></td>";
    added += "<td width=\"33%\"><div class=\"input-group\"><span class=\"input-group-addon\">密码：</span><input type=\"text\" class=\"form-control\" name=\"db_pass\"" + db_pass + "></div></td></tr></tbody></table>";
    $("div#databases").append(added);
    set_db_num();
}

function set_db_num() {
    num = 1;
    dbs = $("table[name=database] td[name=db_num]");
    dbs.each(function () {
        $(this).html("<button class=\"btn btn-default\" type=\"button\" onclick=\"del_obj(this);\">数据库" + num + "&nbsp;&nbsp;&nbsp;&nbsp;<b><font color=\"red\">x</font></b></button>");
        num++;
    })
}

function show_server_list() {
    o_s = "<ul class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu\" style=\"height:585px;overflow:scroll\">";
    o_e = "</ul>";
    selected = "";
    o = "";
    pid = "0";
    s_p = "新建项目";
    current_sid = get_href_v("sid");
    for (index in servers) {
        s = servers[index];
        if (s[0].toString() == current_sid) {
            pid = s[0].toString();
            s_p = s[1];
            selected = "<li><a href=\"#\" pid=\"" + pid + "\">" + s_p + "</a></li><li class=\"divider\"></li>";
        }
        else {
            o += "<li><a href=\"#\" pid=\"" + s[0].toString() + "\">" + s[1] + "</a></li>";
        }
    }
    if (pid == "0") {
        o = "<li><a href=\"#\" pid=\"" + pid + "\">" + s_p + "</a></li><li class=\"divider\"></li>" + o;
    }
    else {
        o = "<li><a href=\"#\" pid=\"0\">新建项目</a></li>" + o;
    }
    added = "<button type=\"button\" class=\"btn btn-default dropdown-toggle col-lg-12\" name=\"servers\" data-toggle=\"dropdown\" pid=\"" + pid + "\">" + s_p + "<span class=\"caret\"></span></button>" + o_s + selected + o + o_e;
    $("div[name=servers]").html(added);
}

function load_server(s_id) {
    if (s_id == 0) {
        window.location = "?m=server";
    }
    else {
        window.location = "?m=server&sid=" + s_id;
    }
}

function populate_info() {
    if (Object.keys(server_info).length == 6) {
        $("div#server_name").find(":hidden[name=server_id]").val(server_info["id"]);
        $("div#server_name").find(":text[name=server_name]").val(server_info["name"]);
        $("div#server_name").find("button[name=disable]").removeAttr("disabled");
        toggle_dis_rm_button(server_info["production"], $("div#server_name").find("button[name=production]"), null, "生产环境", "测试环境", null, "btn-info");
        toggle_dis_rm_button(server_info["active"], $("div#server_name").find("button[name=disable]"), $("div#server_name").find("button[name=delete]"));
        for (index in Object.keys(server_info["hosts"])) {
            add_host(server_info["hosts"][index]);
        }
        for (index in Object.keys(server_info["databases"])) {
            add_database(server_info["databases"][index]);
        }
    }
}

function del_obj(obj) {
    $(obj).parent().parent().parent().parent().remove();
}

function submit_server() {
    server_id = $("div#server_name").find(":hidden[name=server_id]").val();
    server_name = $("div#server_name").find(":text[name=server_name]").val();
    is_p = $("div#server_name").find("button[name=production]").attr("production");
    all_db_info = get_all_db_info();
    all_host_info = get_hosts_info();
    request = {
        "server_id": server_id,
        "server_name": server_name,
        "production": is_p,
        "hosts": all_host_info,
        "databases": all_db_info,
    };
    toggle_modal($("div#loading"), "show");
    $("button#submit_server").attr("disabled", "true");
    $.post('action/?a=eds', {
            'request': JSON.stringify(request)
        },
        function (data, status) {
            $("button#submit_server").removeAttr("disabled");
            toggle_modal($("div#loading"), "hide");
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                if (response["status"] == "NEW") {
                    BootstrapDialog.show({title: "成功", message: "新项目添加成功！"});
                    window.location = "?m=server&sid=" + response["msg"].toString();
                }
                else {
                    BootstrapDialog.show({title: "成功", message: response["msg"]});
                    return true;
                }
            }
        }
    );
}

function toggle_production() {
    sid = get_href_v("sid");
    if (sid == null || sid == "0") {
        is_p = $("div#server_name").find("button[name=production]").attr("production");
        if (is_p == "Y") {
            is_p = "N";
        }
        else {
            is_p = "Y";
        }
        $("div#server_name").find("button[name=production]").attr("production", is_p);
        toggle_dis_rm_button(is_p, $("div#server_name").find("button[name=production]"), null, "生产环境", "测试环境", null, "btn-info");
    }
    else {
        $.get("action/?a=ssp&sid=" + sid,
            function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                }
                else {
                    $("div#server_name").find("button[name=production]").attr("production", response["msg"]);
                    toggle_dis_rm_button(response["msg"], $("div#server_name").find("button[name=production]"), null, "生产环境", "测试环境", null, "btn-info");
                }
            }
        );
    }
}

function get_all_db_info() {
    all_db_info = [];
    all_dbs = $("div#databases").find("table[name=database]");
    all_dbs.each(function () {
        all_db_info.push(get_db_info($(this)));
    });
    return all_db_info;
}

function get_db_info(db_obj) {
    db_info = {};
    db_info["id"] = $(db_obj).find(":hidden[name=id]").val();
    db_info["db_module"] = $(db_obj).find(":text[name=db_module]").val();
    db_info["db_host"] = $(db_obj).find(":text[name=db_host]").val();
    db_info["db_port"] = $(db_obj).find(":text[name=db_port]").val();
    db_info["db_name"] = $(db_obj).find(":text[name=db_name]").val();
    db_info["db_user"] = $(db_obj).find(":text[name=db_user]").val();
    db_info["db_pass"] = $(db_obj).find(":text[name=db_pass]").val();
    return db_info;
}

function get_hosts_info() {
    all_host_info = [];
    all_hosts = $("div#hosts").find("table[name=host]");
    all_hosts.each(function () {
        all_host_info.push(get_host_info($(this)));
    });
    return all_host_info;
}

function get_host_info(host_obj) {
    host_info = {};
    host_info["id"] = $(host_obj).find(":hidden[name=id]").val();
    host_info["host_address"] = $(host_obj).find(":text[name=host_address]").val();
    host_info["ssh_port"] = $(host_obj).find(":text[name=ssh_port]").val();
    host_info["ssh_user"] = $(host_obj).find(":text[name=ssh_user]").val();
    host_info["ssh_pass"] = $(host_obj).find(":password[name=ssh_pass]").val();
    host_info["ssh_key"] = $(host_obj).find(":text[name=ssh_key]").val();
    host_info["paths"] = get_host_paths($(host_obj).find("table[name=host_path]"));
    return host_info;
}

function get_host_paths(path_list) {
    paths = [];
    path_list.each(function () {
        paths.push(get_host_path($(this)));
    });
    return paths;
}

function get_host_path(path_obj) {
    path_info = {};
    path_info["id"] = $(path_obj).find(":hidden[name=id]").val();
    path_info["path_module"] = $(path_obj).find(":text[name=path_module]").val();
    path_info["path_src"] = $(path_obj).find(":text[name=path_src]").val();
    path_info["path"] = $(path_obj).find(":text[name=path]").val();
    path_info["path_des"] = $(path_obj).find(":text[name=path_des]").val();
    return path_info;
}

function disable_server() {
    sid = $("div#server_name").find(":hidden[name=server_id]").val();
    $.get("action/?a=dis&sid=" + sid, function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                toggle_dis_rm_button(response["msg"], $("div#server_name").find("button[name=disable]"), $("div#server_name").find("button[name=delete]"));
                return true;
            }
        }
    );
}

function delete_server() {
    sid = $("div#server_name").find(":hidden[name=server_id]").val();
    sname = $("div#server_name").find(":text[name=server_name]").val();
    bsConfirm("是否确定删除 " + sname + " 项目？").then(function (r) {
            if (r) {
                $.get("action/?a=des&sid=" + sid, function (data, status) {
                        response = JSON.parse(data);
                        if (response["status"] == "FAILED") {
                            BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                            return false;
                        }
                        else {
                            window.location = "?m=server";
                        }
                    }
                );
            }
            else
                return false;
        }
    );
}

$(function () {
        $("div[name=servers]").on('click', 'li a', function () {
                sid = $(this).attr("pid");
                current_sid = get_href_v("sid");
                if (sid != current_sid) {
                    if (sid == "0")
                        window.location = "?m=server";
                    else
                        window.location = "?m=server&sid=" + sid;
                }
            }
        );
    }
);
