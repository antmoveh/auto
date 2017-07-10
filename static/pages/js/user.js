var user_info = {};
var user_permissions = [];
var permissions = [];
var prod_list = [];
var server_list = [];
var subscribe_list = [];
var PROD_STEP = 10.0;
$(document).ready(function () {
    load_data();
});

function set_div_height(obj, bottom) {
    if (bottom == undefined) {
        bottom = 20;
    }
    window_height = $(window).height();
    build_div_offset = $(obj).offset().top;
    build_div_height = window_height - build_div_offset - bottom;
    $(obj).css("height", build_div_height);
}

function load_data() {
    $.get("user/?a=lda",
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
            }
            else {
                user_info = response["msg"]["user_info"];
                user_permissions = response["msg"]["user_permissions"];
                permissions = response["msg"]["permissions"];
                prod_list = response["msg"]["prod_list"];
                server_list = response["msg"]["server_list"];
                subscribe_list = response["msg"]["subscribe_list"];
                populate_userinfo();
                if (user_permissions.length > 0) {
                    populate_permissions();
                }
                if (prod_list != undefined && prod_list.length > 0 && server_list.length > 0) {
                    populate_subscribe();
                }
                set_div_height($("div#permissions"));
            }
        }
    );
}

function populate_userinfo() {
    if (!jQuery.isEmptyObject(user_info)) {
        added = "<table class=\"table\" style=\"margin-bottom: 0px;\"><tr><td>用户名:</td><td>" + user_info["username"] + "</td><td>显示名:</td><td><input type=\"text\" name=\"display\" value=\"" + user_info["display"] + "\">";
        added += "</td></tr><tr><td>邮件地址:</td><td><input type=\"text\" name=\"email\" value=\"" + user_info["email"] + "\"></td><td>当前密码:</td><td><input type=\"password\" name=\"password\">";
        added += "</td></tr><td>新密码:</td><td><input type=\"password\" name=\"new_pass\"></td><td>确认密码:</td><td><input type=\"password\" name=\"new_confirm\"></td></tr>";
        added += "<tr><td colspan=\"4\" class=\"text-center\"><button class=\"btn btn-primary\" onclick=\"update_userinfo();\" name=\"up_userinfo\">更新</button></td></tr></table>";
        $("div#user_info").html(added);
    }
}

function populate_permissions() {
    added = "<table class=\"table table-striped\">";
    for (i in user_permissions) {
        added += generate_userPermission(user_permissions[i]);
    }
    added += "</table>";
    $("div#permissions").html(added);
}

function generate_userPermission(user_info) {
    permission = user_info["permissions"];
    counter = 0;
    added = "";
    select_all = " checked";
    for (index in permissions) {
        pers = permissions[index];
        type = pers["type"];
        actions = pers["actions"];
        if (counter == 0) {
            line = "<tr>";
        }
        type_chk = " checked";
        type_line = "";
        for (i in actions) {
            pid = actions[i]["id"];
            pname = actions[i]["name"];
            if (permission.indexOf(pid) > -1) {
                chk = " checked";
            }
            else {
                chk = "";
                type_chk = "";
                select_all = "";
            }
            type_line += "<tr><td><label><input type=\"checkbox\" pid=\"" + pid.toString() + "\"" + chk + ">" + pname + "</label></td></tr>";
        }
        line += "<td width=\"20%\" class=\"text-center\"><div class=\"panel panel-info\" style=\"margin-bottom: 0px;\"><div class=\"panel-heading\" align=\"center\">";
        line += "<div class=\"input-group\"><span class=\"input-group-addon\"><input type=\"checkbox\" onclick=\"check_type(this);\" type=\"" + type + "\"" + type_chk + "></span>";
        line += "<span class=\"input-group-addon\" onclick=\"collapse_panel(this);\">" + type + "</span></div></div><div class=\"panel-collapse collapse\" name=\"pb\" type=\"" + type + "\">";
        line += "<div class=\"panel-body\" name=\"body_content\"><table class=\"table\" style=\"margin-bottom: 0px;\">";
        line += type_line + "</table></div></div></div></td>";
        counter++;
        if (counter == 5) {
            line += "</tr>";
            added += line;
            counter = 0;
        }
    }
    if (counter > -1 && counter < 10) {
        added += line + "</tr>";
    }
    if (user_info["active"] == "Y") {
        rm_b_d = " class=\"btn btn-default\" disabled=\"true\"";
        ac_b_c = "btn btn-success";
        ac_b_t = "活跃";
    }
    else {
        rm_b_d = " class=\"btn btn-danger\"";
        ac_b_c = "btn btn-default";
        ac_b_t = "禁用";
    }
    response = "<tr><td width=\"10%\" class=\"text-center vert-middle\">" + user_info["username"] + "<br><label><input type=\"checkbox\" name=\"toggle\" onclick=\"toggle_permit(this);\"" + select_all + ">";
    response += "全选</label><br><button uid=\"" + user_info["uid"] + "\" class=\"btn btn-primary\" onclick=\"update_userPermit(this);\">更新权限</button><br><div class=\"input-group\">";
    response += "<span class=\"input-group-btn\"><button name=\"rm_user\" username=\"" + user_info["username"] + "\" uid=\"" + user_info["uid"] + "\" onclick=\"rm_user(this);\"" + rm_b_d + ">X</button>";
    response += "<button name=\"dis_user\" uid=\"" + user_info["uid"] + "\" class=\"" + ac_b_c + "\" onclick=\"dis_user(this);\">" + ac_b_t + "</button>";
    response += "</span></div></td>";
    response += "<td width=\"90%\"><table class=\"table table-bordered table-striped\" style=\"margin-bottom: 0px;\">";
    response += added + "</table></td></tr>";
    return response;
}

function test_subscribe(prod, server, matrix) {
    if (prod == undefined || server == undefined) {
        return false;
    }
    if (matrix == undefined || matrix == false) {
        list = subscribe_list;
        if (list == undefined) {
            return false;
        }
        if (list[prod] == undefined) {
            return false;
        }
        else {

            if (list[prod][server] == undefined) {
                return false;
            }
            else {
                return list[prod][server];
            }
        }
    }
    else {
        if (server == "-1") {
            obj = $("div#subscribe_hidden").find(":hidden[marker=b_" + prod + "]");
            if ($(obj) == undefined || $(obj) == null) {
                return false;
            }
            if ($(obj).attr("s") == "Y") {
                return true;
            }
            else {
                return false;
            }
        }
        else {
            obj = $("div#subscribe_hidden").find(":hidden[marker=c_" + prod + "-" + server + "]");
            if ($(obj) == undefined || $(obj) == null) {
                return false;
            }
            deploy = false;
            test = false;
            if ($(obj).attr("deploy") == "Y") {
                deploy = true;
            }
            if ($(obj).attr("test") == "Y") {
                test = true;
            }
            return {"deploy": deploy, "test": test};
        }
    }
}

function get_prods(start, step) {
    start = parseInt(start);
    step = parseInt(step);
    if (isNaN(start)) {
        start = 0;
    }
    if (isNaN(step)) {
        step = PROD_STEP;
    }
    end = start + step;
    max = prod_list.length;
    if (start >= max) {
        return [];
    }
    if (end > max) {
        end = max;
    }
    r = [];
    for (i = start; i < end; i++) {
        r.push(prod_list[i]);
    }
    return r;
}

function generate_subscribe_matrix(start, step) {
    prods = get_prods(start, step);
    f_p = "<table class=\"col-lg-12\" style=\"margin-bottom: 0px;\"><tr class=\"active\">";
    marker = true;
    f_s = "";
    for (index in server_list) {
        server = server_list[index];
        sid = server["id"];
        f_s += "<tr><td class=\"active\" class=\"text-center vert-middle\">" + server["name"] + "</td><td>";
        f_s += "<table class=\"col-lg-12 table table-bordered table-hover\" style=\"margin-bottom: 0px;\"><tr>";
        for (i in prods) {
            prod = prods[i];
            if (marker) {
                b = "";
                b_subscribe = test_subscribe(prod["id"], "-1", true);
                if (b_subscribe) {
                    b = " checked";
                }
                f_p += "<td width=\"10%\" class=\"text-center\"><label>" + prod["name"] + "<br>";
                f_p += "<input type=\"checkbox\" name=\"build\" onchange=\"change_subscribe(this);\" pid=\"" + prod["id"] + "\"" + b + ">编译</label></td>";
            }
            subscribe = test_subscribe(prod["id"], server["id"], true);
            pid = prod["id"];
            deploy = "";
            test = "";
            fid = "0";
            if (subscribe != false) {
                if (subscribe["deploy"]) {
                    deploy = " checked";
                }
                if (subscribe["test"]) {
                    test = " checked";
                }
                fid = subscribe["id"];
            }
            f_s += "<td width=\"10%\" class=\"text-center\" name=\"subscribe_td\">";
            f_s += "<label><input type=\"checkbox\" name=\"deploy\" onchange=\"change_subscribe(this);\" pid=\"" + pid + "\" sid=\"" + sid + "\"" + deploy + ">部署</label> | ";
            f_s += "<label>测试<input type=\"checkbox\" name=\"test\" onchange=\"change_subscribe(this);\" pid=\"" + pid + "\" sid=\"" + sid + "\"" + test + "></label></td>";
        }
        marker = false;
        f_s += "</tr></table></td></tr>";
    }
    f_p += "</tr></table>";
    return {"prods": f_p, "servers": f_s};
}

function change_subscribe(obj) {
    mod = $(obj).attr("name");
    if ($(obj).prop("checked")) {
        value = "Y";
    }
    else {
        value = "N";
    }
    if (mod == "build") {
        $("div#subscribe_hidden").find(":hidden[marker=b_" + $(obj).attr("pid") + "]").attr("s", value);
    }
    else {
        $("div#subscribe_hidden").find(":hidden[marker=c_" + $(obj).attr("pid") + "-" + $(obj).attr("sid") + "]").attr(mod, value);
    }
}

function populate_subscribe_hidden() {
    added = "";
    build = "";
    for (i in prod_list) {
        prod = prod_list[i];
        pid = prod["id"];
        bid = "0";
        s = "N";
        b_subscribe = test_subscribe(pid, "-1");
        if (b_subscribe != false) {
            bid = b_subscribe["id"];
            s = "Y";
        }
        build += "<input type=\"hidden\" name=\"build\" marker=\"b_" + pid + "\" bid=\"" + bid + "\" s=\"" + s + "\" pid=\"" + pid + "\">";
        for (j in server_list) {
            server = server_list[j];
            sid = server["id"];
            subscribe = test_subscribe(pid, sid);
            deploy = "N";
            test = "N";
            fid = "0";
            if (subscribe != false) {
                deploy = subscribe["deploy"];
                test = subscribe["test"];
                fid = subscribe["id"];
            }
            added += "<input type=\"hidden\" name=\"s_c\" marker=\"c_" + pid + "-" + sid + "\" pid=\"" + pid + "\" sid=\"" + sid + "\" fid=\"" + fid + "\" deploy=\"" + deploy + "\" test=\"" + test + "\">";
        }
    }
    $("div#subscribe_hidden").html(build + added);
}

function populate_subscribe() {
    populate_subscribe_hidden();
    added = "<div id=\"subscribe_matrix\" class=\"col-lg-12 text-center\" style=\"display: block; overflow: auto;\">";
    added += "<table class=\"table table-striped table-bordered\" style=\"margin-bottom: 0px;\"><caption class=\"text-center\"><b>邮件订阅</b></caption><thead>";
    tabs = Math.ceil(prod_list.length / PROD_STEP);
    if (tabs > 1) {
        added += "<tr><th class=\"text-center vert-middle\">产品分页</th><th class=\"text-center\"><table class=\"col-lg-12\">";
        for (i = 0; i < tabs; i++) {
            if (i % 10 == 0) {
                added += "<tr>";
            }
            if (i == 0) {
                selected = " btn-primary";
            }
            else {
                selected = " btn-default";
            }
            title = 1 + i * PROD_STEP;
            title = title.toString() + " - " + (title + PROD_STEP - 1).toString();
            added += "<td width=\"10%\" class=\"text-center\"><button class=\"btn" + selected + "\" start=\"" + i + "\" name=\"prod_b\" onclick=\"change_subscribe_prods(this);\">" + title + "</button></td>";
            if (i % 10 == 9) {
                added += "</tr>";
            }
        }
        added += "</table></th></tr>";
    }
    added += "<tr class=\"active\"><th width=\"15%\"></th><th width=\"85%\" name=\"subscribe_prods\">";
    matrix = generate_subscribe_matrix();
    added += matrix["prods"] + "</th></tr></thead><tbody name=\"subscribe_servers\">";
    added += matrix["servers"] + "</tbody></table></div><div align=\"center\"><button class=\"btn btn-primary\" onclick=\"submit_subscribe();\" name=\"ups\">更新邮件订阅列表</button></div>";
    $("div#permissions").html(added);
}

function change_subscribe_prods(obj) {
    start = parseInt($(obj).attr("start")) * PROD_STEP;
    matrix = generate_subscribe_matrix(start, PROD_STEP);
    $("div#subscribe_matrix").find("button[name=prod_b]").each(
        function () {
            $(this).removeClass("btn-primary");
            $(this).addClass("btn-default");
        }
    );
    $(obj).removeClass("btn-default");
    $(obj).addClass("btn-primary");
    $("div#subscribe_matrix").find("th[name=subscribe_prods]").html(matrix["prods"]);
    $("div#subscribe_matrix").find("tbody[name=subscribe_servers]").html(matrix["servers"]);
}

function submit_subscribe() {
    check_list = [];
    build_list = [];
    build_list_o = {};
    check_list_o = {};
    $("div#permissions").find("button[name=ups]").attr("disabled", "true");
    $("div#subscribe_hidden").find(":hidden[name=build]").each(
        function () {
            if ($(this).attr("s") == "Y") {
                if ($(this).attr("bid") == "0") {
                    build_list.push($(this).attr("pid"));
                }
                else {
                    build_list_o[$(this).attr("bid")] = $(this).attr("pid");
                }
            }
        }
    );
    $("div#subscribe_hidden").find(":hidden[name=s_c]").each(
        function () {
            deploy = $(this).attr("deploy");
            test = $(this).attr("test");
            if (deploy == "Y" || test == "Y") {
                if ($(this).attr("fid") == "0") {
                    check_list.push({
                        "pid": $(this).attr("pid"),
                        "sid": $(this).attr("sid"),
                        "deploy": deploy,
                        "test": test
                    });
                }
                else {
                    check_list_o[$(this).attr("fid")] = {"deploy": deploy, "test": test};
                }
            }
        }
    );
    toggle_modal($("div#loading"), "show");
    $.post("user/?a=ups", {
            "check_list": JSON.stringify(check_list),
            "build_list": JSON.stringify(build_list),
            "build_list_o": JSON.stringify(build_list_o),
            "check_list_o": JSON.stringify(check_list_o)
        },
        function (data, status) {
            toggle_modal($("div#loading"), "hide");
            $("div#permissions").find("button[name=ups]").removeAttr("disabled");
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                deleted_b = response["msg"]["d_b"];
                new_b = response["msg"]["n_b"];
                deleted_s = response["msg"]["d_s"];
                new_s = response["msg"]["n_s"];
                for (i in deleted_b) {
                    $("div#subscribe_hidden").find(":hidden[marker=b_" + deleted_b[i] + "]").attr("bid", "0");
                }
                for (i in new_b) {
                    $("div#subscribe_hidden").find(":hidden[marker=b_" + new_b[i]["pid"] + "]").attr("bid", new_b[i]["bid"]);
                }
                for (i in deleted_s) {
                    $("div#subscribe_hidden").find(":hidden[marker=c_" + deleted_s[i]["pid"] + "-" + deleted_s[i]["sid"] + "]").attr("fid", "0");
                }
                for (i in new_s) {
                    $("div#subscribe_hidden").find(":hidden[marker=c_" + new_s[i]["pid"] + "-" + new_s[i]["sid"] + "]").attr("fid", new_s[i]["fid"]);
                }
                BootstrapDialog.show({title: "执行成功", message: response["msg"]["info"]});
                return true;
            }
        }
    );
}

function collapse_panel(obj) {
    $(obj).parent().parent().parent().find("div[name=pb]").collapse('toggle');
}

function check_type(obj) {
    type = $(obj).attr("type");
    s = $(obj).is(":checked");
    $(obj).parent().parent().parent().parent().find(":checkbox").each(
        function () {
            $(this).prop("checked", s);
        }
    );
}

function toggle_permit(obj) {
    s = $(obj).is(":checked");
    $(obj).parent().parent().parent().find(":checkbox").each(
        function () {
            if ($(this).attr("name") != "toggle") {
                $(this).prop("checked", s);
            }
        }
    );
}

function update_userinfo() {
    display = $("div#user_info").find(":text[name=display]").val();
    email = $("div#user_info").find(":text[name=email]").val();
    password = $("div#user_info").find(":password[name=password]").val();
    new_pass = $("div#user_info").find(":password[name=new_pass]").val();
    new_confirm = $("div#user_info").find(":password[name=new_confirm]").val();
    if (new_pass.length > 0) {
        if (new_pass.length < 8) {
            BootstrapDialog.show({title: "参数出错", message: "密码长度不足8位"});
            return false;
        }
        if (new_pass != new_confirm) {
            BootstrapDialog.show({title: "参数出错", message: "确认密码不匹配"});
            return false;
        }
        password = $.md5(password);
        new_pass = $.md5(new_pass);
    }
    request = {"display": display, "email": email, "old_password": password, "password": new_pass};
    toggle_modal($("div#loading"), "show");
    $("div#user_info").find("button[name=up_userinfo]").attr("disabled", "true");
    $.post("user/?a=uui", request,
        function (data, status) {
            $("div#user_info").find("button[name=up_userinfo]").removeAttr("disabled");
            toggle_modal($("div#loading"), "hide");
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                BootstrapDialog.show({title: "执行成功", message: response["msg"]});
                return true;
            }
        }
    );
}

function update_userPermit(obj) {
    uid = $(obj).attr("uid");
    permits = [];
    $(obj).parent().parent().find(":checkbox").each(
        function () {
            if ($(this).is(":checked") == true && $(this).attr("pid") != undefined) {
                permits.push($(this).attr("pid"));
            }
        }
    );
    toggle_modal($("div#loading"), "show");
    $(obj).attr("disabled", "true");
    $.post("user/?a=uup&u=" + uid, {'permits': JSON.stringify(permits)},
        function (data, status) {
            $(obj).removeAttr("disabled");
            toggle_modal($("div#loading"), "hide");
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                BootstrapDialog.show({title: "执行成功", message: response["msg"]});
                return true;
            }
        }
    );
}

function rm_user(obj) {
    uid = $(obj).attr("uid");
    username = $(obj).attr("username");
    bsConfirm("是否删除用户 " + username + " ?").then(
        function (r) {
            if (r) {
                $.get("user/?a=rmu&u=" + uid,
                    function (data, status) {
                        response = JSON.parse(data);
                        if (response["status"] == "FAILED") {
                            BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                            return false;
                        }
                        else {
                            window.location.reload();
                        }
                    }
                );
            }
        }
    );
}

function dis_user(obj) {
    uid = $(obj).attr("uid");
    $.get("user/?a=diu&u=" + uid,
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                if (response["msg"] == "Y") {
                    $(obj).text("活跃");
                    $(obj).removeClass("btn-default");
                    $(obj).addClass("btn-success");
                    $(obj).parent().find("button[name=rm_user]").removeClass("btn-danger");
                    $(obj).parent().find("button[name=rm_user]").addClass("btn-default");
                    $(obj).parent().find("button[name=rm_user]").attr("disabled", "true");
                }
                else {
                    $(obj).text("禁用");
                    $(obj).removeClass("btn-success");
                    $(obj).addClass("btn-default");
                    $(obj).parent().find("button[name=rm_user]").removeClass("btn-default");
                    $(obj).parent().find("button[name=rm_user]").addClass("btn-danger");
                    $(obj).parent().find("button[name=rm_user]").removeAttr("disabled");
                }
                return true;
            }
        }
    );
}
