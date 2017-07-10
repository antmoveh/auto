var server_list = [];
var db_list = null;
var host_list = null;
$(document).ready(function () {
    get_servers_dbs();
});

function check_server(obj) {
    sid = $(obj).attr("sid");
    d_l = db_list[sid];
    for (index in d_l) {
        d = d_l[index];
        did = d[0].toString();
        if ($(obj).is(":checked") == true) {
            $(obj).parent().parent().parent().parent().find(":checkbox[dbid=" + did + "]").prop("checked", true);
        }
        else {
            $(obj).parent().parent().parent().parent().find(":checkbox[dbid=" + did + "]").prop("checked", false);
        }
    }
}

function submit_dbc() {
    $("button#add_ndb").attr("disabled", "disabled");
    $("button#submit_dbc").attr("disabled", "disabled");
    db_name = $(":text#db_name").val();
    if (db_name == '' || db_name == undefined) {
        BootstrapDialog.show({title: "信息不全", message: "请输入需要创建的数据库名"});
        $("button#add_ndb").removeAttr("disabled");
        $("button#submit_dbc").removeAttr("disabled");
        return false;
    }
    dbs_list = $("div[name=dbs_list]").find(":checkbox");
    dbs = [];
    $(dbs_list).each(function () {
        if ($(this).is(":checked") == true && $(this).attr("dbid") != undefined) {
            dbs.push($(this).attr("dbid"));
        }
    });
    if (dbs.length == 0) {
        BootstrapDialog.show({title: "信息不全", message: "请选择要创建数据库的服务器"});
        $("button#add_ndb").removeAttr("disabled");
        $("button#submit_dbc").removeAttr("disabled");
        return false;
    }
    return_v = {
        "db_name": db_name,
        "dbs": dbs,
    };
    toggle_modal($("div#loading"), "show");
    $.post('action/?a=dbc', {
            'request': JSON.stringify(return_v),
        },
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                $("button#add_ndb").removeAttr("disabled");
                $("button#submit_dbc").removeAttr("disabled");
                toggle_modal($("div#loading"), "hide");
                return false;
            }
            else {
                BootstrapDialog.show({title: "成功", message: response["msg"]});
                $("button#add_ndb").removeAttr("disabled");
                $("button#submit_dbc").removeAttr("disabled");
                toggle_modal($("div#loading"), "hide");
                return true;
            }
        }
    );
}

function get_servers_dbs() {
    if (server_list.length == 0) {
        $.get('action/?a=gsd', function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                    return false;
                }
                else {
                    server_list = response["msg"]["server_list"];
                    db_list = response["msg"]["db_list"];
                    populate_lists();
                }
            }
        );
    }
}

function populate_lists() {
    if (server_list.length > 0) {
        l_s = "<table width=\"100%\" class=\"table-bordered\"><tbody>";
        l_e = "</tbody></table>";
        counter = 0;
        added = "";
        for (s_i in server_list) {
            s = server_list[s_i];
            sid = s[0].toString();
            d_l = db_list[s[0]];
            prefix = "";
            surfix = "";
            if (counter == 4) {
                counter = 0;
                surfix = "</tr>";
            }
            else {
                if (counter == 0) {
                    prefix = "<tr>";
                }
                counter++;
            }
            added += prefix + "<td width=\"20%\" style=\"vertical-align: top;\"><div class=\"panel panel-info\" style=\"margin-bottom: 0px;\"><div class=\"panel-heading\" align=\"center\" name=\"ph\" sid=\"" + sid + "\">";
            added += "<div class=\"input-group\"><span class=\"input-group-addon\"><input type=\"checkbox\" onclick=\"check_server(this);\" sid=\"" + sid + "\"></span>";
            added += "<span class=\"input-group-addon\" onclick=\"collapse_panel(this);\">" + s[1] + "</span></div></div><div class=\"panel-collapse collapse\" name=\"pb\" sid=\"" + sid + "\">";
            added += "<div class=\"panel-body\" name=\"body_content\"><table class=\"table\" style=\"margin-bottom: 0px;\"><tbody>";
            for (d_i in d_l) {
                d = d_l[d_i];
                did = d[0].toString();
                added += "<tr><td><label><input type=\"checkbox\" dbid=\"" + did + "\">" + d[1] + "</label></td><td align=\"right\"><div class=\"input-group input-group-sm\" dbid=\"" + did + "\" dbn=\"" + d[1] + "\">";
                //added += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" onclick=\"edit_dbh(this);\"><span class=\"glyphicon glyphicon-pencil\"></span></button>";
                added += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" onclick=\"del_dbh(this);\"><span class=\"glyphicon glyphicon-remove\"></span></button></span></div></td></tr>";
            }
            added += "</tbody></table></div></div></div></div></td>" + surfix;
        }
        added = l_s + added + l_e;
        $("div[name=dbs_list]").html(added);
    }
}

function collapse_panel(obj) {
    $(obj).parent().parent().parent().find("div[name=pb]").collapse('toggle');
}

/*function set_edit_host(host_info) {
 if (host_info == undefined) {
 $("div#NewDBCModal").find(":hidden[name=dbid]").val("0");
 $("div#NewDBCModal").find(":text[name=name]").val("");
 $("div#NewDBCModal").find(":text[name=db_host]").val("");
 $("div#NewDBCModal").find(":text[name=db_port]").val("");
 $("div#NewDBCModal").find(":text[name=db_user]").val("root");
 $("div#NewDBCModal").find(":password[name=db_pass]").val("");
 $("div#NewDBCModal").find(":text[name=ssh_port]").val("");
 $("div#NewDBCModal").find(":text[name=ssh_user]").val("kdy_yanfa");
 $("div#NewDBCModal").find(":password[name=ssh_pass]").val("");
 $("div#NewDBCModal").find(":text[name=ssh_key]").val("/data/applications/auto/id_rsa");
 }
 else {
 $("div#NewDBCModal").find(":hidden[name=dbid]").val(host_info[""]);
 $("div#NewDBCModal").find(":text[name=name]").val(host_info[""]);
 $("div#NewDBCModal").find(":text[name=db_host]").val(host_info[""]);
 $("div#NewDBCModal").find(":text[name=db_port]").val(host_info[""]);
 $("div#NewDBCModal").find(":text[name=db_user]").val(host_info[""]);
 $("div#NewDBCModal").find(":password[name=db_pass]").val(host_info[""]);
 $("div#NewDBCModal").find(":text[name=ssh_port]").val(host_info[""]);
 $("div#NewDBCModal").find(":text[name=ssh_user]").val(host_info[""]);
 $("div#NewDBCModal").find(":password[name=ssh_pass]").val(host_info[""]);
 $("div#NewDBCModal").find(":text[name=ssh_key]").val(host_info[""]);
 }
 }*/

function show_add_dbc(obj) {
    if (obj == undefined) {
        if ($("div#NewDBCModal").find("div[name=servers]").html().length == 0) {
            add_server_list();
        }
        $("div#NewDBCModal").modal('show');
    }
    else {
        dbid = $(obj).parent().parent().attr("dbid");
        sid = $(obj).parent().parent().parent().parent().parent().parent().parent().parent().attr("sid");
    }
}

function edit_dbh(obj) {
    dbid = $(obj).parent().parent().attr("dbid");
    sid = $(obj).parent().parent().parent().parent().parent().parent().parent().parent().attr("sid");

}

function del_dbh(obj) {
    dbid = $(obj).parent().parent().attr("dbid");
    dbn = $(obj).parent().parent().attr("dbn");
    bsConfirm("是否移除选定数据库主机 " + dbn + "？").then(function (r) {
            if (r) {
                $.get("action/?a=ddh&did=" + dbid, function (data, status) {
                        response = JSON.parse(data);
                        if (response["status"] == "FAILED") {
                            BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                            return false;
                        }
                        else {
                            $(obj).parent().parent().parent().parent().remove();
                        }
                    }
                );
            }
            else {
                return false;
            }
        }
    );
}

function add_server_list() {
    if (server_list.length > 0) {
        s_p = "请选择服务器";
        pid = "0";
        o_s = "<ul class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu\" style=\"height:440px;overflow:scroll\">";
        o_e = "</ul>";
        o = "";
        for (index in server_list) {
            server = server_list[index];
            o += "<li><a href=\"#\" pid=\"" + server[0].toString() + "\">" + server[1] + "</a></li>";
        }
        added = "<button type=\"button\" class=\"btn btn-default dropdown-toggle\" name=\"server\" data-toggle=\"dropdown\" pid=\"" + pid + "\">" + s_p + "<span class=\"caret\"></span></button>" + o_s + o + o_e;
        $("div#NewDBCModal").find("div[name=servers]").html(added);
    }
}

function add_host_list() {
    sid = $("div#NewDBCModal").find("div[name=servers]").find("button[name=server]").attr("pid");
    c_sid = $("div#NewDBCModal").find("div[name=hosts]").find("button[name=host]").attr("sid");
    if (sid == c_sid) {
        return false;
    }
    if (host_list != null && host_list[sid] != null && host_list[sid].length > 0) {
        s_p = "请选择服务器";
        pid = "0";
        o_s = "<ul class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu\">";
        o_e = "</ul>";
        o = "";
        for (index in host_list[sid]) {
            host = host_list[sid][index];
            o += "<li><a href=\"#\" pid=\"" + host[0].toString() + "\">" + host[1] + "</a></li>";
        }
        added = "<button type=\"button\" class=\"btn btn-default dropdown-toggle\" name=\"host\" data-toggle=\"dropdown\" sid=\"" + sid + "\" pid=\"" + pid + "\">" + s_p + "<span class=\"caret\"></span></button>" + o_s + o + o_e;
        $("div#NewDBCModal").find("div[name=hosts]").html(added);
    }
}

function add_dbc() {
    var prod = $("div#NewDBCModal").find("button[name=server]").attr("pid");
    var empty_items = "";
    if (prod == undefined || prod.length == 0 || prod == "0") {
        empty_items += " 产品";
    }
    var name = $("div#NewDBCModal").find(":text[name=name]").val();
    if (name == undefined || name.length == 0) {
        empty_items += " 别称";
    }
    var type = $("div#NewDBCModal").find(":text[name=type]").val();
    if (type == undefined || type.length == 0) {
        empty_items += " 类型";
    }
    var db_host = $("div#NewDBCModal").find(":text[name=db_host]").val();
    if (db_host == undefined || db_host.length == 0) {
        empty_items += " 地址";
    }
    var db_name = $("div#NewDBCModal").find(":text[name=db_name]").val();
    if (db_name == undefined || db_name.length == 0) {
        empty_items += " 库名";
    }
    var db_port = $("div#NewDBCModal").find(":text[name=db_port]").val();
    if (db_port == undefined || db_port.length == 0) {
        empty_items += " 端口";
    }
    var db_user = $("div#NewDBCModal").find(":text[name=db_user]").val();
    if (db_user == undefined || db_user.length == 0) {
        empty_items += " 用户";
    }
    var db_pass = $("div#NewDBCModal").find(":password[name=db_pass]").val();
    if (db_pass == undefined || db_pass.length == 0) {
        empty_items += " 密码";
    }
    if (empty_items.length > 0) {
        BootstrapDialog.show({title: "信息不全", message: "请填写信息：" + empty_items});
        return false;
    }
    var request = {
        "server": prod,
        "name": name,
        "type": type,
        "db_host": db_host,
        "db_name": db_name,
        "db_port": db_port,
        "db_user": db_user,
        "db_pass": db_pass
    };
    $.post("action/?a=ndb", {"request": JSON.stringify(request),}, function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                BootstrapDialog.show({title: "成功", message: response["msg"]});
                $("div#NewDBCModal").modal('hide');
                location.reload();
            }
        }
    );
}


function set_host_detail() {
    sid = $("div#NewDBCModal").find("div[name=servers]").find("button[name=server]").attr("pid");
    hid = $("div#NewDBCModal").find("div[name=hosts]").find("button[name=host]").attr("pid");
    hosts = host_list[sid];
    for (index in hosts) {
        host = hosts[index];
        if (host[0].toString() == hid) {
            $("div#NewDBCModal").find(":text[name=name]").val(host[1]);
            $("div#NewDBCModal").find(":text[name=db_host]").val(host[1]);
            $("div#NewDBCModal").find(":text[name=ssh_port]").val(host[2]);
            $("div#NewDBCModal").find(":text[name=ssh_user]").val(host[3]);
            $("div#NewDBCModal").find(":password[name=ssh_pass]").val(host[4]);
            $("div#NewDBCModal").find(":text[name=ssh_key]").val(host[5]);
            return true;
        }
    }
    BootstrapDialog.show({title: "执行出错！", message: "无法找到指定主机数据"});
}

function set_btn_txt(btn, pid, txt) {
    if ($(btn).attr("pid") != pid) {
        $(btn).html(txt + "<span class=\"caret\"></span>");
        $(btn).attr("pid", pid);
    }
}

$(function () {
        $("div#NewDBCModal").find("div[name=servers]").on('click', 'li a', function () {
                set_btn_txt($("div#NewDBCModal").find("button[name=server]"), $(this).attr("pid"), $(this).text());
                add_host_list();
            }
        );
        $("div#NewDBCModal").find("div[name=hosts]").on('click', 'li a', function () {
                set_btn_txt($("div#NewDBCModal").find("button[name=host]"), $(this).attr("pid"), $(this).text());
                set_host_detail();
            }
        );
    }
);
