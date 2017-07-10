var prod_list = [];
var module_list = {};
var jenkins_list = [];
var buildjob_list = {};
var server_list = [];
var host_list = {};
var host_paths = [];
var actions = [];
var dropdown_list = [];
var dropdown_id = 0;
var task_list = [];
var test_list = [];
var test_detail = {};
$(document).ready(function () {
    load_data();
});

function load_data() {
    sid = get_href_v("s");
    pid = get_href_v("pid");
    if (sid == null || pid == null) {
        ps = "";
    }
    else {
        ps = "&pid=" + pid + "&s=" + sid;
    }
    hid = get_href_v("h");
    if (hid == null) {
        h = "";
    }
    else {
        h = "&h=" + hid;
    }
    $.get("action/?a=ldm" + ps + h,
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
            }
            else {
                prod_list = response["msg"]["prod_list"];
                module_list = response["msg"]["module_list"];
                jenkins_list = response["msg"]["jenkins"];
                server_list = response["msg"]["server_list"];
                host_list = response["msg"]["host_list"];
                actions = response["msg"]["actions"];
                task_list = response["msg"]["task_list"];
                test_list = response["msg"]["test_list"];
                populate();
            }
        }
    );
}

function set_prod_name(pid) {
    if (pid == "0") {
        $("table#manage_prod").find(":text[name=prod_name]").attr("pid", "0");
        $("table#manage_prod").find(":text[name=prod_name]").val("");
        $("table#manage_prod").find(":text[name=prod_name]").attr("pname", "");
        $("table#manage_prod").find("button[name=add_module]").attr("disabled", "true");
        $("table#manage_prod").find("button[name=dis]").attr("disabled", "true");
        $("table#manage_prod").find("button[name=rm]").attr("disabled", "true");
    }
    else {
        for (i in prod_list) {
            p = prod_list[i];
            if (p[0].toString() == pid) {
                $("table#manage_prod").find(":text[name=prod_name]").attr("pid", p[0].toString());
                $("table#manage_prod").find(":text[name=prod_name]").val(p[1]);
                $("table#manage_prod").find(":text[name=prod_name]").attr("pname", p[1]);
                toggle_dis_rm_button(p[2], $("table#manage_prod").find("button[name=dis]"), $("table#manage_prod").find("button[name=rm]"));
                return true;
            }
        }
        return false;
    }
}

function populate() {
    if (prod_list.length > 0) {
        pid = get_href_v("pid");
        if (pid == null) {
            pid = "0";
        }
        add_droplist("prod_list", prod_list, pid, "添加新产品", $("table#manage_prod").find("div[name=products]"), "<li><a href=\"#\" pid=\"0\">添加新产品</a></li>");
        set_prod_name(pid);
        populate_modules();
        populate_server();
        populate_host();
        populate_actions();
    }
    __populate_server();
    __populate_host();
}

function add_droplist(mode, list, id, title, obj, extra) {
    if (list != undefined) {
        c_id = "0";
        s_p = title;
        o_s = "<ul class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu\" style=\"height:555px;overflow:scroll\" >";
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
        added = "<button type=\"button\" class=\"btn btn-default dropdown-toggle\" name=\"" + mode + "\" data-toggle=\"dropdown\" pid=\"" + c_id + "\">" + s_p + "<span class=\"caret\"></span></button>" + o_s + s + extra + o + o_e;
        $(obj).html(added);
    }
}

function populate_modules() {
    pid = $("table#manage_prod").find(":text[name=prod_name]").attr("pid");
    if (pid == "0") {
        $("table#manage_module").html("");
    }
    else {
        list = module_list[pid];
        counter = 0;
        added = "";
        for (index in list) {
            m = list[index];
            end = "";
            if (counter == 0) {
                added += "<tr>";
            }
            if (counter == 1) {
                end = "</tr>";
                counter = -1;
            }
            if (m[2] == "Y") {
                rm_b_d = " class=\"btn btn-default\" disabled=\"true\"";
                ac_b_c = "btn btn-success";
                ac_b_t = "已启用";
            }
            else {
                rm_b_d = " class=\"btn btn-danger\"";
                ac_b_c = "btn btn-default";
                ac_b_t = "已禁用";
            }
            added += "<td class=\"text-center\" mid=\"" + m[0] + "\"><table class=\"table\" style=\"margin-bottom: 0px;\"><tbody><tr></td>";
            added += "<td class=\"text-center vert-middle\" style=\"border-top: none;\"><div class=\"input-group col-lg-12\"><span class=\"input-group-btn\">";
            added += "<button name=\"rm\" onclick=\"rm_module(" + m[0] + ", \'" + m[1] + "\');\"" + rm_b_d + ">X</button>";
            added += "<button name=\"dis\" class=\"" + ac_b_c + "\" onclick=\"dis_module(" + m[0] + ");\">" + ac_b_t + "</button>";
            added += "</span><input type=\"text\" class=\"form-control\" name=\"module_name\" class=\"text-center\" mname=\"" + m[1] + "\" value=\"" + m[1] + "\">";
            added += "<span class=\"input-group-btn\"><button class=\"btn btn-primary\" onclick=\"edit_module(" + m[0] + ")\">修改</button>";
            added += "<button class=\"btn btn-primary\" onclick=\"show_module_build(" + m[0] + ")\">编译</button></span></div></td></tr></tbody></table>";
            added += end;
            counter++;
        }
        $("table#manage_module").html(added);
    }
}

function show_add_module() {
    pname = $("table#manage_prod").find(":text[name=prod_name]").attr("pname");
    $("div#ModuleModal").find("td[name=prod]").text(pname);
    $("div#ModuleModal").modal("show");
}

function add_module() {
    pid = $("table#manage_prod").find(":text[name=prod_name]").attr("pid");
    if (pid != "0") {
        module_name = $("div#ModuleModal").find(":text[name=module]").val();
        if (module_name.length < 1) {
            BootstrapDialog.show({title: "信息不足", message: "请填写子模块名称"});
            return false;
        }
        $.post("action/?a=adm&pid=" + pid, {"module": module_name},
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

function edit_module(mid) {
    mname = $("table#manage_module").find("td[mid=" + mid + "]").find(":text[name=module_name]").val();
    old_mname = $("table#manage_module").find("td[mid=" + mid + "]").find(":text[name=module_name]").attr("mname");
    if (mname == old_mname)
        return false;
    if (mname.length > 0) {
        $.post("action/?a=edm&mid=" + mid, {"module_name": mname},
            function (data, status) {
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
    else {
        BootstrapDialog.show({title: "缺少信息", message: "请填写子模块名称"});
    }
}

function dis_module(mid) {
    $.get("action/?a=dim&mid=" + mid,
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                toggle_dis_rm_button(response["msg"], $("table#manage_module").find("td[mid=" + mid + "]").find("button[name=dis]"), $("table#manage_module").find("td[mid=" + mid + "]").find("button[name=rm]"));
                return true;
            }
        }
    );
}

function rm_module(mid, mname) {
    bsConfirm("是否删除子模块 " + mname + "？").then(
        function (r) {
            if (r) {
                $.get("action/?a=rmm&mid=" + mid,
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

function set_buildinfo(b) {
    add_droplist("jenkins", jenkins_list, b["jenkins"], "请选择Jenkins服务器", $("div#BuildModal").find("div[name=jenkins_list]"), "");
    $("div#BuildModal").find(":text[name=job_name]").val(b["job_name"]);
    $("div#BuildModal").find(":password[name=token]").val(b["token"]);
    $("div#BuildModal").find(":text[name=git_url]").val(b["git_url"]);
    $("div#BuildModal").find(":text[name=code_path]").val(b["code_path"]);
    $("div#BuildModal").find(":text[name=sql_path]").val(b["sql_path"]);
}

function show_module_build(mid) {
    pname = $("table#manage_prod").find(":text[name=prod_name]").attr("pname");
    mname = $("table#manage_module").find("td[mid=" + mid + "]").find(":text[name=module_name]").attr("mname");
    $("div#BuildModal").find(":hidden[name=mid]").val(mid);
    $("div#BuildModal").find("td[name=prod]").text(pname + " " + mname);
    $("div#BuildModal").find("td[name=mod]").html("<input type=\"text\" name=\"mod\" value=\"WAR\" disabled>");
    if (buildjob_list[mid] != undefined && buildjob_list[mid] != null) {
        b = buildjob_list[mid];
        set_buildinfo(b);
        $("div#BuildModal").modal("show");
    }
    else {
        $.get("view/?a=gbi&mid=" + mid,
            function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                    return false;
                }
                else {
                    if (response["msg"]["build"] == "true") {
                        buildjob_list[mid] = response["msg"]["buildinfo"];
                        b = buildjob_list[mid];
                    }
                    else {
                        b = {
                            "jenkins": "1",
                            "job_name": pname + "-" + mname,
                            "token": "KoK0ZuIZ3",
                            "git_url": "",
                            "code_path": "",
                            "sql_path": ""
                        };
                    }
                    set_buildinfo(b);
                    $("div#BuildModal").modal("show");
                    return true;
                }
            }
        );
    }
}

function add_buildjob() {
    lack_data = "";
    mid = $("div#BuildModal").find(":hidden[name=mid]").val();
    if (mid == undefined || mid == null || mid == "0" || mid == 0) {
        return false;
    }
    mod = $("div#BuildModal").find(":text[name=mod]").val();
    jenkins = $("div#BuildModal").find("button[name=jenkins]").attr("pid");
    if (jenkins == undefined || jenkins == "0") {
        lack_data += "Jenkins ";
    }
    job_name = $("div#BuildModal").find(":text[name=job_name]").val();
    if (job_name == undefined || job_name.length < 1) {
        lack_data += "工程名 ";
    }
    token = $("div#BuildModal").find(":password[name=token]").val();
    if (token == undefined || token.length < 1) {
        lack_data += "工程密钥 ";
    }
    git_url = $("div#BuildModal").find(":text[name=git_url]").val();
    if (git_url == undefined || git_url.length < 1) {
        lack_data += "代码仓库 ";
    }
    code_path = $("div#BuildModal").find(":text[name=code_path]").val();
    sql_path = $("div#BuildModal").find(":text[name=sql_path]").val();
    if (lack_data.length > 0) {
        BootstrapDialog.show({title: "缺失数据", message: "请提供以下信息: " + lack_data});
        return false;
    }
    buildjob = {
        "mod": mod,
        "jenkins": jenkins,
        "job_name": job_name,
        "token": token,
        "git_url": git_url,
        "code_path": code_path,
        "sql_path": sql_path
    };
    $.post("action/?a=amb&mid=" + mid, {"buildjob": JSON.stringify(buildjob)},
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                BootstrapDialog.show({title: "执行成功", message: response["msg"]});
                buildjob_list[mid] = buildjob;
                return true;
            }
        }
    );
}

function submit_prod_name() {
    pid = $("table#manage_prod").find(":text[name=prod_name]").attr("pid");
    pname = $("table#manage_prod").find(":text[name=prod_name]").val();
    $.post("action/?a=aup&pid=" + pid, {'prod_name': pname},
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

function dis_prod() {
    pid = $("table#manage_prod").find(":text[name=prod_name]").attr("pid");
    $.get("action/?a=dip&pid=" + pid,
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                toggle_dis_rm_button(response["msg"], $("table#manage_prod").find("div[name=prod]").find("button[name=dis]"), $("table#manage_prod").find("div[name=prod]").find("button[name=rm]"));
            }
        }
    );
}

function rm_prod() {
    var pname = $("table#manage_prod").find(":text[name=prod_name]").attr("pname");
    var pid = $("table#manage_prod").find(":text[name=prod_name]").attr("pid");
    bsConfirm("是否删除" + pname + "产品?").then(
        function (r) {
            if (r) {
                if ($("table#manage_module").children().length == 0) {
                    $.get("action/?a=rmp&pid=" + pid,
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
                else {
                    BootstrapDialog.show({title: "执行出错！", message: "存在子模块不能删除产品"});
                }
            }
        }
    );

}

function populate_server() {
    pid = get_href_v("pid");
    if (pid != undefined && pid != "0" && jQuery.isEmptyObject(server_list) == false) {
        sid = get_href_v("s");
        if (sid == null)
            sid = "0";
        add_droplist("server_list", server_list, sid, "服务器", $("table#manage_deploy").find("div[name=server]"), "");
    }
}

function __populate_server() {
    var sid = get_href_v("s");
    if (sid == null)
        sid = "0";
    add_droplist("server_list", server_list, sid, "服务器", $("table#exec_script").find("div[name=server]"), "");
}

function __populate_host() {
    sid = $("table#exec_script").find("button[name=server_list]").attr("pid");
    if (sid != undefined && sid != "0" && jQuery.isEmptyObject(server_list) == false && jQuery.isEmptyObject(host_list) == false) {
        hid = get_href_v("h");
        if (hid == null || hid.length == 0)
            hid = "0";
        hosts = host_list[sid];
        add_droplist("host_list", hosts, hid, "主机列表", $("table#exec_script").find("div[name=host]"), "<li><a href=\"#\" pid=\"0\">主机列表</a></li>");
    }
}

function execute_shell() {
    var hid = $("table#exec_script").find("button[name=host_list]").attr("pid");
    var shell = $("table#exec_script").find(":text[name=script_context]").val();
    if (hid == 0 || shell == "") {
        BootstrapDialog.show({title: "执行出错！", message: "主机或者SHELL命令为空"});
        return false;
    }
    var request = {"hid": hid, "shell": shell};
    $.post("action/?a=esh", {"request": JSON.stringify(request)},
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

function populate_host() {
    sid = $("table#manage_deploy").find("button[name=server_list]").attr("pid");
    if (sid != undefined && sid != "0" && jQuery.isEmptyObject(server_list) == false && jQuery.isEmptyObject(host_list) == false) {
        hid = get_href_v("h");
        if (hid == null || hid.length == 0)
            hid = "0";
        hosts = host_list[sid];
        add_droplist("host_list", hosts, hid, "主机列表", $("table#manage_deploy").find("div[name=host]"), "<li><a href=\"#\" pid=\"0\">主机列表</a></li>");
        h_paths = {};
        if (hid == "0") {
            for (h_i in hosts) {
                host = hosts[h_i];
                paths = host[2];
                for (p_i in paths) {
                    module = paths[p_i];
                    if (!h_paths.hasOwnProperty(module)) {
                        h_paths[module] = module;
                    }
                }
            }
            keys = Object.keys(h_paths);
            for (i in keys) {
                host_paths.push(keys[i]);
            }
        }
        else {
            for (i in hosts) {
                host = hosts[i];
                if (host[0].toString() == hid) {
                    host_paths = host[2];
                    break;
                }
            }
        }
    }
}

function populate_actions() {
    for (i in actions) {
        add_action("", actions[i]);
    }
}

function action_bind_dropdown(obj, obj2) {
    $("div#action_list").on("click", obj + " li a",
        function () {
            set_btn_txt($("div#action_list").find(obj).find("button"), $(this).attr("pid"), $(this).text());
            if (obj2 != undefined && obj2 != null) {
                $(obj).find(obj2).val($(this).text());
                $(obj).find(obj2).attr("param", $(this).attr("pid"));
            }
        }
    );

}

function generate_dropdown(dropdown_name, btn_name, default_btn_pid, default_btn_text, items, value) {
    d_id = dropdown_id.toString();
    dropdown_id++;
    list = "";
    btn_pid = default_btn_pid;
    btn_text = default_btn_text;
    for (i in items) {
        item = items[i];
        list += "<li><a href=\"#\" pid=\"" + item[0] + "\">" + item[1] + "</a></li>";
        if (item[0].toString() == value) {
            btn_pid = item[0].toString();
            btn_text = item[1];
        }
    }
    response = "<div class=\"dropdown\" name=\"" + dropdown_name + "\">";
    response += "<button type=\"button\" class=\"btn btn-default dropdown-toggle\" data-toggle=\"dropdown\" pid=\"" + btn_pid + "\" name=\"" + btn_name + "\">" + btn_text + "<span class=\"caret\"></span></button>";
    response += "<ul class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu\">";
    response += list + "</ul></div>";
    return response;
}

function generate_path_dropdown(btn_name, value) {
    did = dropdown_id.toString();
    dropdown_id++;
    dropdown_list.push(d_id);
    items = [];
    for (i in host_paths) {
        items.push([host_paths[i], host_paths[i]]);
    }
    dropdown = generate_dropdown("d_" + d_id, btn_name, "0", "路径", items, value);
    return "<span class=\"input-group-addon\">路径:</span><span class=\"input-group-btn\">" + dropdown + "</span>";
}

function generate_module_dropdown(pid, btn_name, value) {
    d_id = dropdown_id.toString();
    dropdown_id++;
    dropdown_list.push(d_id);
    dropdown = generate_dropdown("d_" + d_id, btn_name, "0", "子模块", module_list[pid], value);
    return "<span class=\"input-group-addon\">子模块:</span><span class=\"input-group-btn\">" + dropdown + "</span>";
}

function generate_items_dropdown(title, btn_name, value, keys) {
    items = keys;
    if (items == undefined) {
        items = [["Y", "是"], ["N", "否"]];
    }
    d_id = dropdown_id.toString();
    dropdown_id++;
    dropdown_list.push(d_id);
    dropdown = generate_dropdown("d_" + d_id, btn_name, items[0][0], items[0][1], items, value);
    return "<span class=\"input-group-addon\">" + title + ":</span><span class=\"input-group-btn\">" + dropdown + "</span>";
}

function add_action(action_type, action_detail) {
    if (action_detail == undefined) {
        aid = "0";
        operation = action_type;
        param1 = "";
        param2 = "";
        param3 = "";
        param4 = "";
        param5 = "";
        active = "Y";
    }
    else {
        aid = action_detail["aid"];
        operation = action_detail["operation"];
        param1 = action_detail["param1"];
        param2 = action_detail["param2"];
        param3 = action_detail["param3"];
        param4 = action_detail["param4"];
        param5 = action_detail["param5"];
        active = action_detail["active"];
    }
    action = "<div class=\"input-group col-lg-12 row\" name=\"action\" style=\"text-align: left;\"><input type=\"hidden\" name=\"aid\" value=\"" + aid + "\"><input type=\"hidden\" name=\"operation\" value=\"" + operation + "\">";
    dropdown_list = [];
    pid = $("table#manage_prod").find(":text[name=prod_name]").attr("pid");
    switch (operation) {
        case "dep_start":
            action = "";
            $("table#manage_deploy").find(":hidden[name=dep_start]").val(aid);
            break;
        case "tomcat":
            action += "<span class=\"input-group-addon\">Tomcat</span>";
            action += generate_items_dropdown("行为", "param1", param1, [["start", "启动"], ["stop", "关闭"]]);
            action += generate_path_dropdown("param2", param2);
            action += "<input type=\"hidden\" name=\"param3\" value=\"\">";
            if (param4 == "") {
                param4 = "pid";
            }
            action += "<span class=\"input-group-addon\">pid文件:</span><input type=\"text\" class=\"form-control\" name=\"param4\" value=\"" + param4 + "\">";
            action += generate_items_dropdown("强制关闭", "param5", param5, [["20", "是"], ["0", "否"]]);
            break;
        case "deploy":
            action += "<span class=\"input-group-addon\">部署代码</span>";
            action += generate_module_dropdown(pid, "param1", param1);
            action += generate_path_dropdown("param2", param2);
            action += generate_items_dropdown("打包配置文件", "param3", param3);
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param4\" pid=\"" + param4 + "\">预留</button></span>";
            action += "<span class=\"input-group-addon\">预留:</span><input type=\"text\" class=\"form-control\" name=\"param5\" disabled value=\"" + param5 + "\">";
            break;
        case "db_update":
            action += "<span class=\"input-group-addon\">DB升级</span>";
            action += generate_module_dropdown(pid, "param1", param1);
            action += "<span class=\"input-group-addon\">升级文件路径:</span><input type=\"text\" class=\"form-control\" name=\"param2\" value=\"" + param2 + "\">";
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param3\" pid=\"" + param3 + "\">预留</button></span>";
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param4\" pid=\"" + param4 + "\">预留</button></span>";
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param5\" pid=\"" + param5 + "\">预留</button></span>";
            break;
        case "conf":
            action += "<span class=\"input-group-addon\">配置文件</span>";
            action += generate_module_dropdown(pid, "param1", param1);
            action += generate_path_dropdown("param2", param2);
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param3\" pid=\"" + param3 + "\">预留</button></span>";
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param4\" pid=\"" + param4 + "\">预留</button></span>";
            action += "<span class=\"input-group-addon\">预留:</span><input type=\"text\" class=\"form-control\" name=\"param5\" disabled value=\"" + param5 + "\">";
            break;
        case "tar":
            action += "<span class=\"input-group-addon\">TAR</span>";
            action += generate_items_dropdown("行为", "param1", param1, [["create", "压缩"], ["extract", "解压"]]);
            action += "<span class=\"input-group-addon\">TAR文件路径:</span><input type=\"text\" class=\"form-control\" name=\"param2\" value=\"" + param2 + "\">";
            action += "<span class=\"input-group-addon\">工作路径:</span><input type=\"text\" class=\"form-control\" name=\"param3\" value=\"" + param3 + "\">";
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param4\" pid=\"" + param4 + "\">预留</button></span>";
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param5\" pid=\"" + param5 + "\">预留</button></span>";
            break;
        case "jar":
            action += "<span class=\"input-group-addon\">JAR</span>";
            action += generate_items_dropdown("行为", "param1", param1, [["create", "压缩"], ["extract", "解压"]]);
            action += "<span class=\"input-group-addon\">JAR文件路径:</span><input type=\"text\" class=\"form-control\" name=\"param2\" value=\"" + param2 + "\">";
            action += "<span class=\"input-group-addon\">工作路径:</span><input type=\"text\" class=\"form-control\" name=\"param3\" value=\"" + param3 + "\">";
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param4\" pid=\"" + param4 + "\">预留</button></span>";
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param5\" pid=\"" + param5 + "\">预留</button></span>";
            break;
        case "operate_file":
            action += "<span class=\"input-group-addon\">文件</span>";
            action += generate_items_dropdown("行为", "param1", param1, [["cp", "复制"], ["mv", "移动"]]);
            action += "<span class=\"input-group-addon\">来源文件路径:</span><input type=\"text\" class=\"form-control\" name=\"param2\" value=\"" + param2 + "\">";
            action += "<span class=\"input-group-addon\">目标文件路径:</span><input type=\"text\" class=\"form-control\" name=\"param3\" value=\"" + param3 + "\">";
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param4\" pid=\"" + param4 + "\">预留</button></span>";
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param5\" pid=\"" + param5 + "\">预留</button></span>";
            break;
        case "sftp":
            action += "<span class=\"input-group-addon\">SFTP</span>";
            action += generate_items_dropdown("行为", "param1", param1, [["push", "推送到远程"], ["pull", "下载到本地"]]);
            action += "<span class=\"input-group-addon\">远程文件路径:</span><input type=\"text\" class=\"form-control\" name=\"param2\" value=\"" + param2 + "\">";
            action += "<span class=\"input-group-addon\">本地文件路径:</span><input type=\"text\" class=\"form-control\" name=\"param3\" value=\"" + param3 + "\">";
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param4\" pid=\"" + param4 + "\">预留</button></span>";
            action += "<span class=\"input-group-btn\"><button class=\"btn btn-default\" type=\"button\" disabled name=\"param5\" pid=\"" + param5 + "\">预留</button></span>";
            break;
        case "tomcod":
            action += "<span class=\"input-group-addon\">TomCod</span>";
            action += generate_module_dropdown(pid, "param1", param1);
            action += "<span class=\"input-group-addon\">Tomcat端口:</span><input type=\"text\" class=\"form-control\" name=\"param2\" value=\"" + param2 + "\">";
            action += "<span class=\"input-group-addon\">包名:</span><input type=\"text\" class=\"form-control\" name=\"param3\" value=\"" + param3 + "\">";
            break;
        case "dep_finish":
            action = "";
            $("table#manage_deploy").find(":hidden[name=dep_finish]").val(aid);
            if (param1.length > 0) {
                $("table#manage_deploy").find(":text[name=test_url]").val(param1);
            }
            break;
        default:
            action = "";
            break;
    }
    if (action.length > 0) {
        if (active == 'Y') {
            rm_b_d = " class=\"btn btn-default\" disabled=\"true\"";
            ac_b_c = "btn btn-success";
            ac_b_t = "已启用";
        }
        else {
            rm_b_d = " class=\"btn btn-danger\"";
            ac_b_c = "btn btn-default";
            ac_b_t = "已禁用";
        }
        action += "<span class=\"input-group-btn\"><button type=\"button\" name=\"dis\" onclick=\"dis_action(this);\" class=\"" + ac_b_c + "\">" + ac_b_t + "</button>";
        action += "<button type=\"button\" name=\"rm\" onclick=\"rm_action(this);\"" + rm_b_d + "><b>x</b></button></span></div>";
    }
    else {
        return false;
    }
    $("div#action_list").append(action);
    for (i in dropdown_list) {
        action_bind_dropdown("div[name=d_" + dropdown_list[i] + "]");
    }
}

function dis_action(obj) {
    aid = $(obj).parent().parent().find(":hidden[name=aid]").val();
    if (aid == "0") {
        if ($(obj).text() == "已启用") {
            active = 'N';
        }
        else {
            active = 'Y';
        }
        toggle_dis_rm_button(active, obj, $(obj).parent().find("button[name=rm]"));
    }
    else {
        $.get("action/?a=dia&aid=" + aid,
            function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                    return false;
                }
                else {
                    toggle_dis_rm_button(response["msg"], obj, $(obj).parent().find("button[name=rm]"));
                    return true;
                }
            }
        );
    }
}

function rm_action(obj) {
    $(obj).parent().parent().remove();
}

function set_actions() {

}

function get_action_param(action, param) {
    if (action != undefined && param != undefined) {
        value = $(action).find(":hidden[name=" + param + "]").val();
        if (value == undefined) {
            value = $(action).find(":text[name=" + param + "]").val();
        }
        if (value == undefined) {
            value = $(action).find(":button[name=" + param + "]").attr("pid");
        }
        if (value == undefined) {
            value = "";
        }
        return value;
    }
    else {
        return "";
    }
}

function submit_actions() {
    pid = get_href_v("pid");
    sid = get_href_v("s");
    if (pid == null || sid == null) {
        return false;
    }
    hid = get_href_v("h");
    if (hid == null) {
        hid = "0";
    }
    action_list = [];
    $("div#action_list").find("div[name=action]").each(
        function () {
            if (action_list.length == 0) {
                s_aid = $("table#manage_deploy").find(":hidden[name=dep_start]").val();
                dep_start = {
                    "aid": s_aid,
                    "operation": "dep_start",
                    "param1": "",
                    "param2": "",
                    "param3": "",
                    "param4": "",
                    "param5": "",
                    "active": "Y"
                };
                action_list.push(dep_start);
            }
            aid = get_action_param($(this), "aid");
            operation = get_action_param($(this), "operation");
            param1 = get_action_param($(this), "param1");
            param2 = get_action_param($(this), "param2");
            param3 = get_action_param($(this), "param3");
            param4 = get_action_param($(this), "param4");
            param5 = get_action_param($(this), "param5");
            active = $(this).find("button[name=dis]").text();
            switch (operation) {
                case "tomcat":
                    if (param1 == "start") {
                        param3 = "bin/startup.sh";
                    }
                    else {
                        param3 = "bin/shutdown.sh";
                    }
                    break;
                default:
                    break;
            }
            if (active == "已启用") {
                active = "Y";
            }
            else {
                active = "N";
            }
            action = {
                "aid": aid,
                "operation": operation,
                "param1": param1,
                "param2": param2,
                "param3": param3,
                "param4": param4,
                "param5": param5,
                "active": active
            };
            action_list.push(action);
        }
    );
    if (action_list.length > 0) {
        f_aid = $("table#manage_deploy").find(":hidden[name=dep_finish]").val();
        param1 = $("table#manage_deploy").find(":text[name=test_url]").val();
        dep_finish = {
            "aid": f_aid,
            "operation": "dep_finish",
            "param1": param1,
            "param2": "",
            "param3": "",
            "param4": "",
            "param5": "",
            "active": "Y"
        };
        action_list.push(dep_finish);
    }
    toggle_modal($("div#loading"), "show");
    $("button#submit_actions").attr("disabled", "true");
    $.post("action/?a=eda&pid=" + pid + "&s=" + sid + "&h=" + hid, {"action_list": JSON.stringify(action_list)},
        function (data, status) {
            $("button#submit_actions").removeAttr("disabled");
            toggle_modal($("div#loading"), "hide");
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                BootstrapDialog.show({title: "成功", message: response["msg"]});
                return false;
            }
        }
    );
}

function show_testlist() {
    pid = get_href_v("pid");
    sid = get_href_v("s");
    if (pid != null && sid != null) {
        populate_testlist();
        $("div#TestListModal").modal("show");
    }
    else {
        BootstrapDialog.show({title: "警告", message: "必须指定产品项目及服务器后才可配置自动测试工程"});
    }
}

function populate_testlist() {
    if (task_list.length > 0) {
        var l_s = "<table width=\"100%\" class=\"table-bordered\"><tbody>";
        var l_e = "</tbody></table>";
        var counter = 0;
        var added = "";
        for (var c_l in task_list) {
            var c = task_list[c_l];
            var cid = c[0].toString();
            var cname = c[1].toString();
            var prefix = "";
            var surfix = "";
            if (counter == 3) {
                counter = 0;
                surfix = "</tr>";
            }
            else {
                if (counter == 0) {
                    prefix = "<tr>";
                }
                counter++;
            }
            added += prefix + "<td width=\"20%\">";
            added += "<input type=\"checkbox\" name=\"check_box\" cid=\"" + cid + "\" value=\"" + cname + "\">";
            added += " <span>" + cname + "</span></td>";
            added += surfix;
        }
        added = l_s + added + l_e;
        $("div#TestListModal").find("tbody[name=list]").html(added);
        setTimeout(function () {
            $("#TestListModal").find(":checkbox[name=check_box]").each(function () {
                if (test_list.indexOf($(this).attr("cid")) > -1) {
                    $(this).attr("checked", "true");
                }
            });
        }, 100);
    }
}

function submit_show_param() {
    var pid = get_href_v("pid");
    var sid = get_href_v("s");
    var job = "";
    $("#TestListModal").find(":checkbox[name=check_box]").each(function () {
        if ($(this).prop("checked")) {
            job += $(this).attr("cid") + ",";
        }
    });
    if (job != "") {
        job = "&job=" + job;
    }
    $.get("autotest_login/?a=saj&pid=" + pid + "&sid=" + sid + job, function (data, status) {
            var response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                show_param(pid, sid);
                return true;
            }
        }
    )
}

function show_param(pid, sid) {
    $.get("autotest_login/?a=smp&pid=" + pid + "&sid=" + sid, function (data, status) {
            var response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                $("div#ParaModal").find("textarea#para_area").val(response["msg"]);
                return true;
            }
        }
    );
    $("div#ParaModal").modal("show")
}

function submit_area() {
    var pid = get_href_v("pid");
    var sid = get_href_v("s");
    var text = $("div#ParaModal").find("textarea#para_area").val();
    var request = {"pid": pid, "sid": sid, "text": text};
    toggle_modal($("div#loading"), "show");
    $.post("autotest/?a=msae", {
            'request': JSON.stringify(request)
        },
        function (data, status) {
            toggle_modal($("div#loading"), "hide");
            var response = JSON.parse(data);
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


function wast_populate_testlist() {
    added = "";
    for (i in test_list) {
        test = test_list[i];
        tid = test["id"].toString();
        d_b_c = "btn btn-default";
        d_b_t = "已禁用";
        r_b_d = "";
        r_b_c = "btn btn-danger";
        if (test["active"] == "Y") {
            d_b_c = "btn btn-success";
            d_b_t = "已启用";
            r_b_d = " disabled=\"true\"";
            r_b_c = "btn btn-default";
        }
        added += "<tr><td>" + test["name"] + "</td><td><div class=\"input-group\"><span class=\"input-group-btn\"><button class=\"btn btn-info\" tid=\"" + tid + "\" onclick=\"edit_testjob(this);\">";
        added += "修改</button><button class=\"" + d_b_c + "\" name=\"dis\" tid=\"" + tid + "\" onclick=\"dis_test(this);\">" + d_b_t + "</button>";
        added += "<button class=\"" + r_b_c + "\" name=\"rm\" tid=\"" + tid + "\" tname=\"" + test["name"] + "\" onclick=\"rm_test(this);\"" + r_b_d + ">X</button></td></tr>";
    }
    $("div#TestListModal").find("tbody[name=list]").html(added);
}

function dis_test(obj) {
    tid = $(obj).attr("tid");
    if (tid != undefined) {
        $.get("action/?a=dit&tid=" + tid,
            function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                    return false;
                }
                else {
                    toggle_dis_rm_button(response["msg"], $(obj), $(obj).parent().find("button[name=rm]"));
                    return true;
                }
            }
        );
    }
}

function rm_test(obj) {
    tid = $(obj).attr("tid");
    tname = $(obj).attr("tname");
    if (tid != undefined) {
        bsConfirm("是否删除自动测试工程 " + tname + " ?").then(
            function (r) {
                if (r) {
                    $.get("action/?a=rmt&tid=" + tid,
                        function (data, status) {
                            response = JSON.parse(data);
                            if (response["status"] == "FAILED") {
                                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                                return false;
                            }
                            else {
                                $(obj).parent().parent().parent().parent().remove();
                                for (i in test_list) {
                                    if (test_list[i]["id"].toString() == tid) {
                                        test_list.splice(i, 1);
                                        break;
                                    }
                                }
                                return true;
                            }
                        }
                    );
                }
            }
        );
    }
}

function edit_testjob(obj) {
    tid = $(obj).attr("tid");
    if (tid == undefined) {
        tid = "0";
    }
    if (test_detail[tid] == undefined) {
        if (tid == "0") {
            populate_testjob(tid);
            $("div#TestModal").modal("show");
        }
        else {
            $.get("action/?a=gtd&tid=" + tid,
                function (data, status) {
                    response = JSON.parse(data);
                    if (response["status"] == "FAILED") {
                        BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                        return false;
                    }
                    else {
                        test_detail[tid] = response["msg"];
                        $("div#TestModal").find("tbody[name=params]").remove();
                        populate_testjob(tid);
                        $("div#TestModal").modal("show");
                    }
                }
            );
        }
    }
    else {
        $("div#TestModal").modal("show");
    }
}

function populate_testjob(tid) {
    var name = "";
    var jid = "0";
    var job_name = "";
    var token = "";
    var id = "0";
    var params = [];
    var param = {};
    if (test_detail[tid] != undefined) {
        t = test_detail[tid];
        id = tid;
        name = t["name"];
        jid = t["jid"];
        job_name = t["job_name"];
        token = t["token"];
        params = t["params"];
    }
    $("div#TestModal").find(":text[name=name]").val(name);
    $("div#TestModal").find(":text[name=name]").attr("tid", id);
    $("div#TestModal").find(":text[name=job_name]").val(job_name);
    $("div#TestModal").find(":password[name=token]").val(token);
    add_droplist("jenkins", jenkins_list, jid, "请选择Jenkins服务器", $("div#TestModal").find("div[name=jenkins_list]"), "");
    $("div#TestModal").find("tbody[name=params]").children().remove();
    for (i in params) {
        param = params[i];
        add_test_param(param["id"], param["key"], param["value"]);
    }
}

function add_test_param(pid, key, value) {
    if (pid == undefined) {
        pid = "0";
    }
    if (key == undefined) {
        key = "";
    }
    if (value == undefined) {
        value = "";
    }
    var param = "";
    param = "<tr name=\"param\"><td colspan=\"2\" class=\"vert-middle\" style=\"text-align: right;\"><input type=\"text\" name=\"key\" value=\"" + key + "\" class=\"form-control\"></td>";
    param += "<td colspan=\"2\" class=\"vert-middle\"><input type=\"text\" pid=\"" + pid + "\" name=\"value\" value=\"" + value + "\" class=\"form-control\"></td>";
    param += "<td colspan=\"1\" class=\"text-center vert-middle\"><button class=\"btn btn-danger\" onclick=\"rm_param(this);\">X</button></td></tr>";
    $("div#TestModal").find("tbody[name=params]").append(param);
}

function submit_test() {
    pid = get_href_v("pid");
    sid = get_href_v("s");
    tid = $("div#TestModal").find(":text[name=name]").attr("tid");
    name = $("div#TestModal").find(":text[name=name]").val();
    jid = $("div#TestModal").find("div[name=jenkins_list]").find("button[name=jenkins]").attr("pid");
    job_name = $("div#TestModal").find(":text[name=job_name]").val();
    token = $("div#TestModal").find(":password[name=token]").val();
    var params = [];
    $("div#TestModal").find("tbody[name=params]").find("tr[name=param]").each(
        function () {
            key = $(this).find(":text[name=key]").val();
            value = $(this).find(":text[name=value]").val();
            if (key.length > 0 && value.length > 0) {
                params.push({"pid": $(this).find(":text[name=value]").attr("pid"), "key": key, "value": value});
            }
        }
    );
    if (pid == null || sid == null) {
        BootstrapDialog.show({title: "警告", message: "必须指定产品项目及服务器后才可配置自动测试工程"});
        return false;
    }
    empty = "";
    if (name.length == 0) {
        empty += "工程名 ";
    }
    if (job_name.length == 0) {
        empty += "任务名 ";
    }
    if (token.length == 0) {
        empty += "密钥";
    }
    if (empty.length > 0) {
        BootstrapDialog.show({title: "警告", message: "请提供以下信息: " + empty});
        return false;
    }
    if (jid == "0") {
        BootstrapDialog.show({title: "警告", message: "请选择运行测试任务的Jenkins服务器"});
        return false;
    }
    toggle_modal($("div#loading"), "show");
    $("div#TestModal").find("button[name=submit_test]").attr("disabled", "true");
    $.post("action/?a=edt&pid=" + pid + "&sid=" + sid, {
            "tid": tid,
            "name": name,
            "jid": jid,
            "job_name": job_name,
            "token": token,
            "params": JSON.stringify(params)
        },
        function (data, status) {
            toggle_modal($("div#loading"), "hide");
            $("div#TestModal").find("button[name=submit_test]").removeAttr("disabled");
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                new_test = response["msg"];
                ntid = new_test["id"];
                nt = true;
                for (i in test_list) {
                    ot = test_list[i];
                    if (ntid == ot["id"]) {
                        nt = false;
                    }
                }
                if (nt) {
                    test_list.push(new_test);
                    populate_testlist();
                }
                $("div#TestModal").modal("hide");
            }
        }
    );
}

function rm_param(obj) {
    if (obj != undefined) {
        $(obj).parent().parent().remove();
    }
}

function set_btn_txt(btn, pid, txt) {
    if ($(btn).attr("pid") != pid) {
        $(btn).html(txt + "<span class=\"caret\"></span>");
        $(btn).attr("pid", pid);
    }
}

$(function () {
        $("div#action_list").sortable({
            distance: 15,
            cursor: "move",
            update: function () {
                set_actions();
            }
        });
        $("div[name=products]").on('click', 'li a', function () {
                if ($(this).attr("pid") == "0")
                    window.location = "?m=manage";
                else
                    window.location = "?m=manage&pid=" + $(this).attr("pid");
            }
        );
        $("div[name=jenkins_list]").on('click', 'li a',
            function () {
                set_btn_txt($("div#BuildModal").find("button[name=jenkins]"), $(this).attr("pid"), $(this).text());
            }
        );
        $("table#manage_deploy").find("div[name=host]").on('click', 'li a',
            function () {
                sid = $("table#manage_deploy").find("button[name=server_list]").attr("pid");
                hid = $(this).attr("pid");
                href = window.location.href;
                href = set_href_v("s", sid, href);
                href = set_href_v("h", hid, href);
                window.location = href;
            }
        );
        $("div#TestModal").find("div[name=jenkins_list]").on('click', 'li a',
            function () {
                set_btn_txt($("div#TestModal").find("button[name=jenkins]"), $(this).attr("pid"), $(this).text());
            }
        );
        $("table#manage_deploy").find("div[name=server]").on('click', 'li a',
            function () {
                window.location = set_href_v("s", $(this).attr("pid"));
            }
        );
        $("table#exec_script").find("div[name=server]").on('click', 'li a',
            function () {
                window.location = set_href_v("s", $(this).attr("pid"));
            }
        );
        $("table#exec_script").find("div[name=host]").on('click', 'li a',
            function () {
                var sid = $("table#exec_script").find("button[name=server_list]").attr("pid");
                var hid = $(this).attr("pid");
                var href = window.location.href;
                var href = set_href_v("s", sid, href);
                href = set_href_v("h", hid, href);
                window.location = href;
            }
        );
    }
);
