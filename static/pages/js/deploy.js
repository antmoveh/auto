var update_timer = null;
var servers = [];
var product_list = [];
var dep_list = [];
var history_list = {};
var deploy_detail = {};
var test_list = {};
var count = 0;
var PAGE_STEP = 20;
$(document).ready(function () {
    var window_height = $(window).height();
    var server_table_offset = $("table#server_list").offset().top;
    var server_table_height = window_height - server_table_offset - 80;
    $("table#server_list").css("height", server_table_height);
    update();
    update_timer = setInterval(update, 30000);
});

function show_servers() {
    $("table tbody[name=server_list]").html('');
    for (index in servers) {
        server_info = servers[index];
        sid = server_info["id"];
        if (server_info["production"] == "Y") {
            is_p = " <button class=\"btn btn-success\">生产环境</button>";
        }
        else {
            is_p = " <button class=\"btn btn-info\">测试环境</button>";
        }
        added = "<tr name=\"s" + sid + "\"> <input type=\"hidden\" value=\"" + sid + "\" name=\"server_id\">";
        added += "<td class=\"text-center vert-middle\" name=\"dep_server\">" + server_info["name"] + "</td>";
        added += "<td class=\"text-center vert-middle\" name=\"production\">" + is_p + "</td>";
        added += "<td class=\"text-center vert-middle\" name=\"dep_ver\">" + server_info["version"] + "</td>";
        added += "<td class=\"text-center vert-middle\" name=\"dep_time\">" + server_info["time"] + "</td>";
        added += "<td class=\"text-center vert-middle\" name=\"dep_user\">" + server_info["user"] + "</td>";
        status_icon = get_status_icon(server_info["status"]);
        added += "<td class=\"text-center vert-middle\" name=\"status\">" + status_icon + "</td>";
        added += "<td class=\"text-center vert-middle\" name=\"actions\"><a href=\"#\" title=\"编译并部署\"><img class=\"disabled\" src=\"/static/pages/img/build.png\" width=\"32\"></a> ";
        added += "<a href=\"#\" title=\"部署\" onclick=\"show_dep_menu(" + sid + ");\"><img src=\"/static/pages/img/deploy.png\" width=\"32\"></a> ";
        added += "<a href=\"#\" title=\"测试\" onclick=\"show_test_menu(" + sid + ");\"><img src=\"/static/pages/img/test.png\" width=\"32\"></a> ";
        added += "<a href=\"#\" title=\"日志\" onclick=\"show_log(" + sid + ");\"><img src=\"/static/pages/img/log.png\" width=\"32\"></a> ";
        added += "<a href=\"#\" title=\"历史记录\" onclick=\"show_history_modal(" + sid + ", \'" + server_info["name"] + "\');\"><img src=\"/static/pages/img/history.png\" width=\"32\"></a> ";
        added += "<a href=\"#\" title=\"设置\"><img src=\"/static/pages/img/settings.png\" class=\"disabled\" width=\"32\"></a></td></tr>";
        $("table tbody[name=server_list]").append(added);
    }
}

function show_test_menu(sid) {
    toggle_modal($("div#loading"), "show");
    $.get("view/?a=gst",
        function (data, status) {
            toggle_modal($("div#loading"), "hide");
            var response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
            }
            else {
                test_list = response["msg"];
                populate_testlist("aaction");
                populate_testlist("acase");
                $("div#TestListModal").modal("show");
            }
        }
    );
}

function populate_testlist(a) {
    if (test_list[a].length > 0) {
        var l_s = "<table width=\"100%\" class=\"table-bordered\"><tbody>";
        var l_e = "</tbody></table>";
        var counter = 0;
        var added = "";
        for (var c_l in test_list[a]) {
            var c = test_list[a][c_l];
            var cid = c[0].toString();
            var cname = c[1].toString();
            var prefix = "";
            var surfix = "";
            if (counter == 2) {
                counter = 0;
                surfix = "</tr>";
            }
            else {
                if (counter == 0) {
                    prefix = "<tr>";
                }
                counter++;
            }
            added += prefix + "<td width=\"25%\">";
            added += "<input type=\"checkbox\" name=" + a + " cid=\"" + cid + "\" value=\"" + cname + "\">";
            added += " <span>" + cname + "</span></td>";
            added += surfix;
        }
        added = l_s + added + l_e;
        $("div#TestListModal").find("div[name=" + a + "]").html(added);
    }
}

function show_action_param() {
    var task_list = "";
    $("#TestListModal").find(":checkbox[name=aaction]").each(function () {
        if ($(this).prop("checked")) {
            task_list += $(this).attr("cid") + ",";
        }
    });
    if (task_list == "") {
        BootstrapDialog.show({title: "执行出错！", message: "请选择测试任务"});
        return false;
    }
    $.get("autotest_login/?a=dsap" + "&task_list=" + task_list, function (data, status) {
            var response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                show_param("task", task_list);
                return true;
            }
        }
    );
}

function show_case_param() {
    var case_list = "";
    $("#TestListModal").find(":checkbox[name=acase]").each(function () {
        if ($(this).prop("checked")) {
            case_list += $(this).attr("cid") + ",";
        }
    });
    if (case_list == "") {
        BootstrapDialog.show({title: "执行出错！", message: "请选择测试任务"});
        return false;
    }
    $.get("autotest_login/?a=dscp" + "&case_list=" + case_list, function (data, status) {
            var response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                show_param("case", case_list);
                return true;
            }
        }
    );
}

function show_param(a, b) {
    $.get("autotest_login/?a=dsmp&file=" + a, function (data, status) {
            var response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                $("div#ParaModal").find("textarea#para_area").val(response["msg"]);
                $("div#ParaModal").find("button[name=sub]").val(a);
                $("div#ParaModal").find("button[name=sub]").attr("t", b);
                return true;
            }
        }
    );
    $("div#ParaModal").modal("show");
}

function submit_area(th) {
    var file = $(th).val();
    var t = $(th).attr("t");
    var text = $("div#ParaModal").find("textarea#para_area").val();
    var request = {"file": file, "text": text};
    $.post("autotest_login/?a=dsa", {
            'request': JSON.stringify(request)
        },
        function (data, status) {
            var response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                run_case(file, t);
                return true;
            }
        }
    );
}

function run_case(file, t) {
    $.get("autotest_login/?a=drc&file=" + file + "&t=" + t, function (data, status) {
            var response = JSON.parse(data);
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

function waste_show_test_menu(sid) {
    toggle_modal($("div#loading"), "show");
    $.get("view/?a=gts&sid=" + sid,
        function (data, status) {
            toggle_modal($("div#loading"), "hide");
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
            }
            else {
                test_list[sid] = response["msg"];
                populate_testlist(sid);
                $("div#TestListModal").modal("show");
            }
        }
    );
}

function waste_populate_testlist(sid) {
    added = "";
    if (test_list[sid] != undefined) {
        for (i in test_list[sid]) {
            t = test_list[sid][i];
            s = get_status_icon(t["status"]);
            added += "<tr name=\"test\" jid=\"" + t["jid"] + "\" tid=\"" + t["tid"] + "\" sid=\"" + sid + "\"><td name=\"name\" class=\"vert-middle\">" + t["name"] + "</td>";
            added += "<td class=\"text-center vert-middle\">" + t["time"] + "</td>";
            added += "<td name=\"status\" class=\"text-center vert-middle\">" + s + "</td><td name=\"actions\" class=\"text-center vert-middle\">";
            added += "<button class=\"btn btn-primary\" onclick=\"run_test(this);\">触发测试</button> ";
            added += "<button class=\"btn btn-info\"" + t["detail_url"] + ">测试详情</button></td></tr>";
        }
    }
    $("div#TestListModal").find("tbody[name=list]").html(added);
}

function get_status_icon(s) {
    switch (s) {
        case "Y":
            status_icon = "<img src=\"/static/pages/img/success.png\" width=\"32\">";
            break;
        case "F":
            status_icon = "<img src=\"/static/pages/img/failed.png\" width=\"32\">";
            break;
        case "W":
            status_icon = "<img src=\"/static/pages/img/wait.png\" width=\"32\">";
            break;
        case "D":
            status_icon = "<img src=\"/static/pages/img/deploy.png\" width=\"32\">";
            break;
        case "T":
            status_icon = "<img src=\"/static/pages/img/test.png\" width=\"32\">";
            break;
        default:
            status_icon = "N/A";
            break;
    }
    return status_icon;
}

function run_all_test() {
    jobs = [];
    $("div#TestListModal").find("tbody[name=list]").find("tr[name=test]").each(
        function () {
            jobs.push($(this).attr("jid"));
        }
    );
    bsConfirm("是否确定触发全部测试工程？").then(
        function (r) {
            if (r) {
                $.post("action/?a=tat", {"tests": JSON.stringify(jobs)},
                    function (data, status) {
                        response = JSON.parse(data);
                        if (response["status"] == "FAILED") {
                            BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                        }
                        else {
                            BootstrapDialog.show({title: "成功", message: response["msg"]});
                            s = get_status_icon("W");
                            $("div#TestListModal").find("tbody[name=list]").find("tr[name=test]").find("td[name=status]").each(
                                function () {
                                    $(this).html(s);
                                }
                            );
                        }
                    }
                );
            }
        }
    );
}

function run_test(obj) {
    jid = $(obj).parent().parent().attr("jid");
    $.get("action/?a=tst&jid=" + jid,
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
            }
            else {
                BootstrapDialog.show({title: "成功", message: response["msg"]});
                s = get_status_icon("W");
                $(this).parent().parent().find("td[name=status]").html(s);
            }
        }
    );
}

function show_history_modal(sid, sname) {
    if (history_list[sid] != undefined) {
        populate_history(sid, sname);
        $("div#HistoryModal").modal('show');
        return true;
    }
    else {
        $.get("view/?a=ldh&sid=" + sid,
            function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                    return false;
                }
                else {
                    history_list[sid] = response["msg"]["history_list"];
                    sname = response["msg"]["server"];
                    populate_history(sid, sname);
                    $("div#HistoryModal").modal('show');
                    return true;
                }
            }
        );
    }
}

function populate_history(sid, sname) {
    histories = history_list[sid];
    $("div#HistoryModal").find("div[name=History_header]").html("<h3>" + sname + " 部署历史</h3>");
    added = "";
    for (i in histories) {
        h = histories[i];
        added += "<tr><td><div class=\"panel panel-info\" style=\"margin-bottom: 0px;\"><div class=\"panel-heading\" align=\"center\" did=\"" + h["id"] + "\" onclick=\"toggle_detail(this);\">";
        added += "<table class=\"table\" style=\"margin-bottom: 0px;\"><tr><td width=\"25%\" style=\"text-align: center; vertical-align: middle;\">" + h["prod"] + " " + h["version"] + "</td>";
        status_icon = get_status_icon(h["status"]);
        added += "<td width=\"20%\" style=\"vertical-align: middle;\">执行人: " + h["user"] + "</td><td width=\"25%\" style=\"vertical-align: middle;\">" + h["time"] + "</td>";
        added += "<td width=\"15%\" style=\"vertical-align: middle;\">状态: " + status_icon + "</td><td width=\"15%\" style=\"vertical-align: middle;\">运行中: " + h["on"] + "</td></tr></table>";
        added += "</div><div class=\"panel-collapse collapse\" name=\"pb\"><div class=\"panel-body\" name=\"body_content\"></div></div></td></tr>";
    }
    $("div#HistoryModal").find("table[name=history_list]").html(added);
}

function toggle_detail(obj) {
    did = $(obj).attr("did");
    if (deploy_detail[did] != undefined) {
        $(obj).parent().find("div[name=pb]").collapse('toggle');
    }
    else {
        $.get("view/?a=ldd&did=" + did,
            function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                    return false;
                }
                else {
                    deploy_detail[did] = response["msg"];
                    populate_detail(deploy_detail[did], $(obj).parent().find("div[name=body_content]"));
                    $(obj).parent().find("div[name=pb]").collapse('toggle');
                }
            }
        );
    }
}

function populate_detail(details, obj) {
    added = "<table class=\"table table-hover\"><thead><tr><th width=\"25%\" style=\"text-align: center;\">时间</th><th width=\"15%\" style=\"text-align: center;\">状态</th>";
    added += "<th width=\"60%\" style=\"text-align: center;\">日志</th></tr></thead><tbody>";
    for (i in details) {
        d = details[i];
        added += "<tr><td style=\"text-align: center; border-right: 1px solid #000000;\">" + d["time"] + "</td><td style=\"text-align: center; border-right: 1px solid #000000;\">" + d["status"] + "</td>";
        added += "<td>" + d["detail"] + "</td><tr>";
    }
    added += "</tbody></table>";
    $(obj).html(added);
}

function opt_loading(action) {
    if (action == "show") {
        var top_p = ($(window).height() - $("div#DeployModal-loading").height()) / 2;
        var left = ($("body").width() - $("div#DeployModal-loading").width()) / 2;
        var scrollTop = $(document).scrollTop();
        var scrollLeft = $(document).scrollLeft();
        $("div#DeployModal-loading").css({position: 'absolute', 'top': top_p + scrollTop, 'left': left + scrollLeft});
        $("div#DeployModal-loading").show();
    }
    else {
        $("div#DeployModal-loading").hide();
    }
}

function show_dep_menu(sid) {
    var prod_length = $("div#DeployModal").find("div[name=prod_list]").children().length;
    if (sid == $("div#DeployModal").find(":hidden[name=sid]").val() && prod_length > 0) {
        $("div#DeployModal").modal('show');
    }
    else {
        $("div#DeployModal").find(":hidden[name=sid]").val(sid);
        opt_loading("show");
        $.get("view/?a=gpl&s=" + sid,
            function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                }
                else {
                    product_list = response["msg"];
                    show_dep_modal(sid);
                }
            }
        );
    }
}

function show_log(sid) {
    opt_loading("show");
    $.get("view/?a=dpl&sid=" + sid, function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                opt_loading("hide");
                return false;
            }
            if (response["status"] == "OK") {
                d_log = response["msg"];
                server = d_log["server"];
                prod = d_log["product"];
                ver = d_log["version"];
                u = d_log["user"];
                s = d_log["status"];
                d_time = d_log["time"];
                desc = d_log["desc"];
                logs = d_log["logs"];	//[time, status, detail]
                $("div#LogModal").find("td[name=server]").text(server);
                $("div#LogModal").find("td[name=product]").text(prod);
                $("div#LogModal").find("td[name=version]").text(ver);
                $("div#LogModal").find("td[name=username]").text(u);
                $("div#LogModal").find("td[name=status]").text(s);
                $("div#LogModal").find("td[name=time]").text(d_time);
                //$("div#LogModal").find("td[name=desc]").html("");
                added = "<table class=\"table table-hover\"><thead><tr><th width=\"25%\" style=\"text-align: center;\">时间</th><th width=\"15%\" style=\"text-align: center;\">状态</th>";
                added += "<th width=\"60%\" style=\"text-align: center;\">日志</th></tr></thead><tbody>";
                for (i = 0; i < logs.length; i++) {
                    added += "<tr><td style=\"text-align: center; border-right: 1px solid #000000;\">" + logs[i][0] + "</td><td style=\"text-align: center; border-right: 1px solid #000000;\">" + logs[i][1] + "</td>";
                    added += "<td>" + logs[i][2] + "</td><tr>";
                }
                added += "</tbody></table>";
                $("div#LogModal").find("td[name=logs]").html(added);
                $("div#LogModal").find(":hidden[name=sid]").val(sid);
                $("div#LogModal").modal('show');
            }
            opt_loading("hide");
        }
    );
}

function populate_prod_list() {
    s_p = "请选择部署产品";
    pid = "0";
    prod_list = [];
    if (product_list != []) {
        p_list = product_list["prod_list"];
        for (i = 0; i < p_list.length; i++) {
            if (p_list[i][2] == 1) {
                pid = p_list[i][0];
                s_p = p_list[i][1];
            }
            else
                prod_list.push([p_list[i][0], p_list[i][1]]);
        }
    }
    added = "<button type=\"button\" class=\"btn btn-default dropdown-toggle\" name=\"s\" data-toggle=\"dropdown\" pid=\"" + pid + "\">" + s_p + "<span class=\"caret\"></span></button>";
    added += "<ul class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu\">";
    if (pid != "0")
        added += "<li><a href=\"#\" pid=\"" + pid + "\">" + s_p + "</a></li><li class=\"divider\"></li>";
    for (i = 0; i < prod_list.length; i++)
        added += "<li><a href=\"#\" pid=\"" + prod_list[i][0] + "\">" + prod_list[i][1] + "</a></li>";
    added += "</ul>";
    $("div#DeployModal").find("div[name=prod_list]").html(added);
    bid = populate_branch_list(pid);
    populate_ver_list(pid, bid);
}

function populate_branch_list(pid) {
    s_v = "请选择产品版本";
    bid = "0";
    branch_list = [];
    if (pid == "0")
        pid = $("div#DeployModal").find("div[name=prod_list]").find("button[name=s]").attr("pid");
    if (pid != "0") {
        b_list = product_list["ver_list"][pid]["branch_list"];
        for (i = 0; i < b_list.length; i++) {
            if (b_list[i][2] == 1) {
                bid = b_list[i][0];
                s_v = b_list[i][1];
            }
            branch_list.push([b_list[i][0], b_list[i][1]]);
        }
    }
    added = "<button type=\"button\" class=\"btn btn-default dropdown-toggle\" name=\"s\" data-toggle=\"dropdown\" pid=\"" + bid + "\">" + s_v + "<span class=\"caret\"></span></button>";
    added += "<ul class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu\">";
    for (i = 0; i < branch_list.length; i++)
        added += "<li><a href=\"#\" pid=\"" + branch_list[i][0] + "\">" + branch_list[i][1] + "</a></li>";
    added += "</ul>";
    $("div#DeployModal").find("div[name=branch_list]").html(added);
    return bid;
}

function populate_ver_list(pid, bid) {
    s_v = "请选择编译版本";
    vid = "0";
    ver_list = [];
    if (pid == "0")
        pid = $("div#DeployModal").find("div[name=prod_list]").find("button[name=s]").attr("pid");
    if (bid == "0")
        bid = $("div#DeployModal").find("div[name=branch_list]").find("button[name=s]").attr("pid");
    if (pid != "0" && bid != "0") {
        v_list = product_list["ver_list"][pid]["build_list"][bid];
        for (i = 0; i < v_list.length; i++) {
            if (v_list[i][2] == 1) {
                vid = v_list[i][0];
                s_v = v_list[i][1];
            }
            ver_list.push([v_list[i][0], v_list[i][1]]);
        }
    }
    added = "<button type=\"button\" class=\"btn btn-default dropdown-toggle\" name=\"s\" data-toggle=\"dropdown\" pid=\"" + vid + "\">" + s_v + "<span class=\"caret\"></span></button>";
    added += "<ul class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu\">";
    for (i = 0; i < ver_list.length; i++)
        added += "<li><a href=\"#\" pid=\"" + ver_list[i][0] + "\">" + ver_list[i][1] + "</a></li>";
    added += "</ul>";
    $("div#DeployModal").find("div[name=ver_list]").html(added);
}

function show_dep_modal(sid) {
    s_name = '';
    for (i in servers) {
        if (servers[i]["id"].toString() == sid) {
            s_name = servers[i]["name"];
            break;
        }
    }
    if (s_name.length > 0)
        $("div#DeployModal").find("div[name=deploy_header]").html("<h3>部署服务器：" + s_name + "</h3>");
    populate_prod_list();
    opt_loading("hide");
    $("div#DeployModal").modal('show');
}

function set_btn_txt(btn, pid, txt, set_b, set_v) {
    if ($(btn).attr("pid") != pid) {
        $(btn).html(txt + "<span class=\"caret\"></span>");
        $(btn).attr("pid", pid);
        bid = "0";
        if (set_b) {
            bid = populate_branch_list(pid);
        }
        if (set_v) {
            populate_ver_list("0", bid);
        }
    }
}

function show_info(lvl, content, sid) {
    switch (lvl) {
        case "info":
            popup = $("div#ResponseInfo");
            break;
        case "warning":
            popup = $("div#ResponseWarn");
            break;
        case "alert":
            popup = $("div#ResponseAlert");
            break;
        default:
            popup = null;
            break;
    }
    if (popup != null) {
        close_btn = "<button type=\"button\" class=\"close\" onclick=\"$(this).parent().hide();\">&times;</button>";
        $(popup).text(content);
        $(popup).append(close_btn);
        var top_p = ($(window).height() - $(popup).height()) / 2;
        var left = ($("body").width() - $(popup).width()) / 2;
        var scrollTop = $(document).scrollTop();
        var scrollLeft = $(document).scrollLeft();
        $(popup).css({position: 'absolute', 'top': top_p + scrollTop, 'left': left + scrollLeft});
        $(popup).show();
    }
    if (sid != null && sid != "0") {
        $("table tbody[name=server_list] tr[name=s" + sid + "] td[name=status]").find("img").attr("src", "/static/pages/img/deploy.png");
    }
}

function deploy() {
    sid = $("div#DeployModal").find(":hidden[name=sid]").val();
    pid = $("div[name=prod_list]").find("button[name=s]").attr("pid");
    bid = $("div[name=branch_list]").find("button[name=s]").attr("pid");
    vid = $("div[name=ver_list]").find("button[name=s]").attr("pid");
    user = $("div[name=deploy_body]").find(":text[name=dep_user]").attr("uid");
    if (sid == undefined || sid == "0") {
        BootstrapDialog.show({title: "信息不全", message: "未指定要进行部署的服务器"});
        return false;
    }
    if (pid == undefined || pid == "0") {
        BootstrapDialog.show({title: "信息不全", message: "未指定要部署的产品"});
        return false;
    }
    if (vid == undefined || vid == "0") {
        BootstrapDialog.show({title: "信息不全", message: "未指定要部署的版本"});
        return false;
    }
    if (user == undefined || user == "0") {
        BootstrapDialog.show({title: "信息不全", message: "未知部署账号"});
        return false;
    }
    $("div#DeployModal").modal('hide');
    var top_p = ($(window).height() - $("div#DeployStart").height()) / 2;
    var left = ($("body").width() - $("div#DeployStart").width()) / 2;
    var scrollTop = $(document).scrollTop();
    var scrollLeft = $(document).scrollLeft();
    $("div#DeployStart").css({position: 'absolute', 'top': top_p + scrollTop, 'left': left + scrollLeft});
    $("div#DeployStart").show();
    $.post("action/?a=dep", {
            "sid": sid,
            "pid": pid,
            "bid": bid,
            "vid": vid,
            "uid": user,
        },
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                $("div#DeployStart").hide();
                return false;
            }
            else {
                $("tbody[name=server_list]").find("tr[name=s" + sid + "]").find("td[name=status]").html("<img src=\"/static/pages/img/deploy.png\" width=\"32\">");
                $("div#DeployStart").hide();
                BootstrapDialog.show({title: "执行成功", message: response["msg"]});
            }
        }
    );
}

function update() {
    var p = get_href_v("p");
    if (p != null)
        p = "&p=" + p;
    else
        p = "";
    $.get("view/?a=upd" + p,
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                $("body").append(response["msg"]);
            }
            else {
                servers = response["msg"];
                count = servers[0]["count"];
                show_servers();
                generate_pager();
            }
        }
    );
}

//分页显示
function generate_pager() {
    if (count != 0 && count > PAGE_STEP) {
        var p = parseInt(get_href_v("p"));
        if (isNaN(p))
            p = 1;
        var pages = Math.ceil(count / PAGE_STEP);
        if (p > pages)
            p = pages;
        var min_p = Math.max(2, p - 10);
        if (p == pages)
            var max_p = pages;
        else
            max_p = Math.min(p + 10, pages);
        var first_surfix = "";
        var last_prefix = "";
        if (min_p > 2)
            first_surfix = "...";
        if (max_p < pages - 2)
            last_prefix = "...";
        if (p < 2) {
            var prev = "<li class=\"disabled\"><a href=\"#\">&larr;</a></li>";
            var first_page = "<li class=\"active\"><a href=\"#\">1</a></li>";
        }
        else {
            prev = "<li><a href=\"" + set_href_v("p", p - 1) + "\">&larr;</a></li>";
            first_page = "<li><a href=\"" + set_href_v("p", "1") + "\">1" + first_surfix + "</a></li>";
        }
        if (p >= pages) {
            var next = "<li class=\"disabled\"><a href=\"#\">&rarr;</a></li>";
            var last_page = "<li class=\"active\"><a href=\"#\">" + pages + "</a></li>";
        }
        else {
            next = "<li><a href=\"" + set_href_v("p", p + 1) + "\">&rarr;</a></li>";
            last_page = "<li><a href=\"" + set_href_v("p", pages) + "\">" + last_prefix + pages + "</a></li>";
        }
        added = "<ul class=\"pagination\">" + prev + first_page;
        for (i = min_p; i < max_p; i++) {
            if (p == i)
                added += "<li class=\"active\"><a href=\"#\">" + i + "</a></li>";
            else
                added += "<li><a href=\"" + set_href_v("p", i) + "\">" + i + "</a></li>";
        }
        added += last_page + next + "</ul>";
    }
    else
        added = "";
    $("div#server_pager").html(added);
}

$(function () {
        $("div[name=prod_list]").on('click', 'li a', function () {
                set_btn_txt($("div[name=prod_list]").find("button[name=s]"), $(this).attr("pid"), $(this).text(), true, true);
            }
        );
        $("div[name=branch_list]").on('click', 'li a', function () {
                set_btn_txt($("div[name=branch_list]").find("button[name=s]"), $(this).attr("pid"), $(this).text(), false, true);
            }
        );
        $("div[name=ver_list]").on('click', 'li a', function () {
                set_btn_txt($("div[name=ver_list]").find("button[name=s]"), $(this).attr("pid"), $(this).text(), false, false);
            }
        );
    }
);
