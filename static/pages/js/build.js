
var p_list = [];
var m_list = [];
var v_list = [];
var b_list = [];
var detail_list = {};
var deploy_servers = {};
var open_details = [];
var open_servers = [];
var v_count = 0;
var current_prod = "";
var current_bid = "0";
var current_branch = "";
var PAGE_STEP = 20;
var update_timer = null;
$(document).ready(function () {
    window_height = $(window).height();
    build_div_offset = $("div#builds_div").offset().top;
    build_div_height = window_height - build_div_offset - 80;
    $("div#builds_div").css("height", build_div_height);
    load_page();
    update_timer = setInterval(update, 30000);
});

function add_build(id, version, bm, time, status, certified) {
    td_bgc = "";
    stat = get_status_text(status);
    if (certified == "Y") {
        c_b_c = "btn-success";
        c_b_t = "质量已认证";
    }
    else {
        c_b_c = "btn-default";
        c_b_t = "质量待认证";
    }
    added = "<tr><td class=\"text-center\"><table width=\"100%\" class=\"table-bordered\"><thead><tr><th width=\"20%\">版本：" + version + "</th>";
    added += "<th width=\"17%\">状态：" + stat + "</th>";
    added += "<th width=\"18%\">编译：" + bm + "</th><th width=\"30%\">时间：" + time + "</th>";
    added += "<th width=\"15%\" class=\"text-right\"><button class=\"btn " + c_b_c + "\" name=\"certify\" bid=\"" + id + "\" onclick=\"certify_build(this);\">" + c_b_t + "</button></th>";
    added += "</tr></thead><tbody><tr><td colspan=\"5\"><div class=\"panel panel-info\" style=\"margin-bottom: 0;\">";
    added += "<div class=\"panel-heading\" align=\"center\" type=\"detail\" bid=\"" + id + "\" onclick=\"collapse_panel(this);\">";
    detail_i = open_details.indexOf(id.toString());
    if (detail_i > -1) {
        added += "<h4 class=\"panel-title\" name=\"panel_title\">－ 详细信息</h4></div><div name=\"panel_body\" class=\"panel-collapse collapse in\" aria-expanded=\"true\">"
    }
    else {
        added += "<h4 class=\"panel-title\" name=\"panel_title\">＋ 详细信息</h4></div><div name=\"panel_body\" class=\"panel-collapse collapse\">";
    }
    added += "<div class=\"panel-body\" name=\"body_content\"></div></div></div></td></tr><tr><td colspan=\"5\"><div class=\"panel panel-success\" style=\"margin-bottom: 0;\">";
    added += "<div class=\"panel-heading\" align=\"center\" type=\"server\" bid=\"" + id + "\" onclick=\"collapse_panel(this);\">";
    server_i = open_servers.indexOf(id.toString());
    if (server_i > -1) {
        added += "<h4 class=\"panel-title\" name=\"panel_title\">－ 部署服务器状态</h4></div><div name=\"panel_body\" class=\"panel-collapse collapse in\" aria-expanded=\"true\">";
    }
    else {
        added += "<h4 class=\"panel-title\" name=\"panel_title\">＋ 部署服务器状态</h4></div><div name=\"panel_body\" class=\"panel-collapse collapse\">";
    }
    added += "<div class=\"panel-body\" name=\"body_content\"></div></div></div></td></tr></tbody></table></td></tr>";
    $("tbody[name=build_list]").append(added);
    if (detail_i > -1) {
        obj = $("div[bid=" + open_details[detail_i] + "][type=detail]");
        populate_detail(obj);
    }
    if (server_i > -1) {
        obj = $("div[bid=" + open_servers[server_i] + "][type=server]");
        populate_servers(obj);
    }
}

function certify_build(obj) {
    bid = $(obj).attr("bid");
    $.get("build/?a=ctb&bid=" + bid,
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
            }
            else {
                toggle_dis_rm_button(response["msg"], $(obj), null, "质量已认证", "质量待认证");
            }
        }
    );
}

function collapse_panel(obj) {
    panel_title = $(obj).find("h4[name=panel_title]").text();
    panel_identifier = panel_title.substr(2);
    if (panel_title[0] == "－") {
        $(obj).parent().find("div[name=panel_body]").collapse("hide");
        panel_title = "＋" + panel_title.substr(1);
        bid = $(obj).attr("bid");
        if (panel_identifier == "详细信息") {
            index = open_details.indexOf(bid);
            if (index > -1) {
                open_details.splice(index, 1);
            }
        }
        else {
            index = open_servers.indexOf(bid);
            if (index > -1) {
                open_servers.splice(index, 1);
            }
        }
    }
    else {
        $(obj).parent().find("div[name=panel_body]").collapse("show");
        panel_title = "－" + panel_title.substr(1);
        bid = $(obj).attr("bid");
        if (panel_identifier == "详细信息") {
            index = open_details.indexOf(bid);
            if (index == -1) {
                open_details.push(bid);
            }
            if (detail_list[bid] == undefined) {
                $.get("view/?a=gbd&bid=" + bid, function (data, status) {
                        response = JSON.parse(data);
                        if (response["status"] == "FAILED") {
                            BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                            return false;
                        }
                        else {
                            detail_list[bid] = response["msg"];
                            populate_detail(obj);
                        }
                    }
                );
            }
            else
                populate_detail(obj);
        }
        else {
            index = open_servers.indexOf(bid);
            if (index == -1) {
                open_servers.push(bid);
            }
            if (deploy_servers[bid] == undefined) {
                $.get("view/?a=bds&bid=" + bid, function (data, status) {
                        response = JSON.parse(data);
                        if (response["status"] == "FAILED") {
                            BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                            return false;
                        }
                        else {
                            deploy_servers[bid] = response["msg"];
                            populate_servers(obj);
                        }
                    }
                );
            }
        }
    }
    $(obj).find("h4[name=panel_title]").text(panel_title);
}

function get_status_text(s) {
    r = s;
    switch (r) {
        case "B":
            r = "<font color=\"blue\">正在编译...</font>";
            break;
        case "W":
            r = "<font color=\"black\">正在等待...</font>";
            break;
        case "D":
            r = "<font color=\"green\">编译完成</font>";
            break;
        case "F":
            r = "<font color=\"red\">编译失败</font>";
            break;
        case "O":
            r = "<font color=\"blue\"><i>下载代码...</i></font>";
            break;
        default:
            break;
    }
    return r;
}

function populate_detail(obj) {
    if ($(obj).parent().find("div[name=panel_body]").find("div[name=body_content]").html() == "") {
        bid = $(obj).attr("bid");
        if (detail_list[bid] == undefined) {
            return false;
        }
        else {
            detail = detail_list[bid];
            builds = detail["builds"];
            bm = detail["build_master"];
            bt = detail["build_time"];
            desc = detail["descript"];
            s = detail["status"];
            c = detail["certified"];
            s = get_status_text(s);
            switch (c) {
                case "N":
                    c = "<font color=\"blue\">未验证</font>";
                    break;
                case "Y":
                    c = "<font color=\"green\">已验证</font>";
                    break;
                default:
                    break;
            }
            added = "<table class=\"table table-striped\" style=\"margin-bottom: 0px;\"><tbody><tr><td width=\"10%\">创建人：</td><td width=\"15%\">" + bm + "</td><td width=\"10%\">时间：</td><td width=\"15%\">" + bt + "</td>";
            added += "<td width=\"10%\">状态：</td><td width=\"15%\">" + s + "</td><td width=\"10%\">验证：</td><td width=\"15%\">" + c + "</td></tr>";
            added += "<tr><td colspan=\"8\"><table class=\"table\" style=\"margin-bottom: 0px;\">";
            for (i in builds) {
                b = builds[i];
                b_s = get_status_text(b["status"]);
                added += "<tr><td width=\"15%\" class=\"vert-middle\">模块: " + b["module"] + "</td><td width=\"55%\" class=\"vert-middle\">代码版本: " + b["rev"] + "</td>";
                added += "<td width=\"18%\" class=\"vert-middle\">状态: " + b_s + "</td>";
                added += "<td width=\"12%\" class=\"vert-middle\"><button class=\"btn btn-primary\"  value=\"" + b["url"] + "\" onclick=build_details(this)>编译详情</button></td></tr>";
            }
            added += "</table></td></tr><tr><td>注释：</td><td colspan=\"7\">" + desc + "</td></tr></tbody></table>";
            $(obj).parent().find("div[name=panel_body]").find("div[name=body_content]").html(added);
        }
    }
}

function populate_servers(obj) {
    if ($(obj).parent().find("div[name=panel_body]").find("div[name=body_content]").html() == "") {
        bid = $(obj).attr("bid");
        if (deploy_servers[bid] == undefined) {
            return false;
        }
        else {
            added = "<table class =\"table\"><tbody><tr><td><div class=\"alert alert-info\" style=\"margin-bottom: 0px;\"><table class=\"table\" style=\"margin-bottom: 0px;\"><tr>";
            added += "<td width=\"20%\" class=\"text-center\">服务器</td><td width=\"15%\" class=\"text-center\">用户</td><td width=\"35%\" class=\"text-center\">部署时间</td>";
            added += "<td width=\"15%\" class=\"text-center\">状态</td><td width=\"15%\" class=\"text-center\">服务</td></tr></table></div></td></tr>";
            for (index in deploy_servers[bid]) {
                server = deploy_servers[bid][index];
                sname = server["server"];
                time = server["time"];
                username = server["username"];
                desc = server["desc"];
                s = server["status"];
                o = server["on"];
                switch (s) {
                    case "D":
                        s_info = "<font color=\"blue\">部署中...</font>";
                        s_class = " class=\"alert alert-info\"";
                        break;
                    case "F":
                        s_info = "<font color=\"red\">部署失败</font>";
                        s_class = " class=\"alert alert-danger\"";
                        break;
                    case "T":
                        s_info = "<font color=\"blue\"><i>测试中...</i></font>";
                        s_class = " class=\"alert alert-info\"";
                        break;
                    case "Y":
                        s_info = "<font color=\"green\">部署成功</font>";
                        s_class = " class=\"alert alert-success\"";
                        break;
                    default:
                        s_info = s;
                        s_class = "";
                        break;
                }
                switch (o) {
                    case "N":
                        o = "<font color=\"blue\">已更换</font>";
                        break;
                    case "Y":
                        o = "<font color=\"green\">运行中</font>";
                        break;
                    default:
                        break;
                }
                added += "<tr><td><div" + s_class + " style=\"margin-bottom: 0px;\"><table class=\"table\" style=\"margin-bottom: 0px;\"><tbody><tr><td width=\"20%\" class=\"text-center\">" + sname + "</td>";
                added += "<td width=\"15%\" class=\"text-center\">" + username + "</td><td width=\"35%\" class=\"text-center\">" + time + "</td><td width=\"15%\" class=\"text-center\">" + s + "</td>";
                added += "<td width=\"15%\" class=\"text-center\">" + o + "</td></tr></tbody></table></div></td></tr>";
            }
            added += "</tbody></table>";
            $(obj).parent().find("div[name=panel_body]").find("div[name=body_content]").html(added);
        }
    }
}

function populate_prods() {
    pid = get_href_v("pid");
    if (pid == null) {
        pid = "0";
    }
    add_dropdown_list("prod", p_list, pid, "请选择产品", $("div[name=prod_list]"));
    current_prod = $("div[name=prod_list]").find("button[name=prod]").text();
}

function load_page() {
    pid = get_href_v("pid");
    bid = get_href_v("bid");
    p = get_href_v("p");
    if (pid == null) {
        pid = "";
    }
    else {
        pid = "&pid=" + pid;
    }
    if (bid != null) {
        current_bid = bid;
        bid = "&bid=" + bid;
    }
    else
        bid = "";
    if (p != null)
        p = "&p=" + p;
    else
        p = "";
    toggle_modal($("div#builds-loading"), "show");
    $.get('view/?a=lop' + pid + bid + p, function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
            }
            else {
                p_list = response["msg"]["p_list"];
                b_list = response["msg"]["br_list"];
                v_list = response["msg"]["bu_list"];
                v_count = response["msg"]["bu_count"];
                m_list = response["msg"]["module_list"];
                PAGE_STEP = response["msg"]["page_step"];
                current_bid = response["msg"]["cbid"];
                populate_prods();
                populate_branchs();
                populate_builds();
                generate_pager();
                toggle_modal($("div#builds-loading"), "hide");
            }
        }
    );
}

function populate_branchs() {
    pid = get_href_v("pid");
    if (b_list.length < 1) {
        $("div[name=branch_list]").text("未找到版本列表");
        if (pid != null) {
            $("button[name=pop_branch_menu]").removeClass("disabled");
        }
        $("button[name=pop_build_menu]").addClass('disabled');
        current_branch = "";
        return;
    }
    bid = get_href_v("bid");
    if (bid == null) {
        bid = current_bid;
    }
    add_dropdown_list("branch", b_list, bid, "请选择版本", $("div[name=branch_list]"));
    if (bid != null && bid != "0") {
        for (i in b_list) {
            b = b_list[i];
            if (b["id"].toString() == bid) {
                $("div[name=branch_list]").append("&nbsp;&nbsp;&nbsp;&nbsp;GIT分支: " + b.git_branch);
                break;
            }
        }
    }
    current_branch = $("div[name=branch_list]").find("button[name=branch]").text();
    $("button[name=pop_branch_menu]").removeClass("disabled");
    $("button[name=pop_build_menu]").removeClass('disabled');
}

function get_builds() {
    pid = $("div[name=prod_list]").find("button[name=prod]").attr("pid");
    bid = $("div[name=branch_list]").find("button[name=branch]").attr("pid");
    p = parseInt(get_href_v("p"));
    if (isNaN(p)) {
        p = 1;
    }
    if (pid != undefined && pid != "0" && bid != undefined && bid != "0") {
        $.get('view/?a=gbu&pid=' + pid + '&bid=' + bid + '&p=' + p.toString(),
            function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                }
                else {
                    v_list = response["msg"]["builds"];
                    v_count = response["msg"]["count"];
                    PAGE_STEP = response["page_step"];
                    populate_builds();
                    generate_pager();
                }
            }
        );
    }
}

function update() {
    pid = get_href_v("pid");
    bid = get_href_v("bid");
    if (bid == null) {
        if (current_bid == "0") {
            return;
        }
        else {
            bid = current_bid;
        }
    }
    if (pid != null && bid != null && bid != "0") {
        p = parseInt(get_href_v("p"));
        if (isNaN(p)) {
            p = 1;
        }
        $.get('view/?a=gbu&pid=' + pid + '&bid=' + bid + '&p=' + p.toString(),
            function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                }
                else {
                    PAGE_STEP = response["msg"]["page_step"];
                    populate_builds();
                    generate_pager();
                }
            }
        );
    }
}

function build() {
    pid = get_href_v("pid");
    bid = get_href_v("bid");
    if (bid == null) {
        if (current_bid == "0") {
            return;
        }
        else {
            bid = current_bid;
        }
    }
    if (pid != null && bid != null && bid != "0") {
        u = $("div#BuildModal").find(":text[name=build_master]").attr("uid");
        desc = $("div#BuildModal").find("textarea[name=descript]").val();
        modules = [];
        $("div#BuildModal").find("div[name=module]").find(":checkbox[name=module]").each(
            function () {
                if ($(this).prop("checked")) {
                    modules.push($(this).attr("mid"));
                }
            }
        );
        $.post("build/?a=mkb&pid=" + pid + "&bid=" + bid + "&u=" + u, {
                "modules": JSON.stringify(modules),
                "desc": desc,
            },
            function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "OK") {
                    get_builds();
                    $("div#BuildModal").modal("hide");
                }
                else
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false
            }
        );
    }
}

function add_branch() {
    pid = get_href_v("pid");
    if (pid != null) {
        u = $("div#BranchModal").find(":text[name=username]").attr("uid");
        branch = $("div#BranchModal").find(":text[name=branch_name]").val();
        git_branch = $("div#BranchModal").find(":text[name=git_branch]").val();
        if (branch.length < 1) {
            BootstrapDialog.show({title: "信息不全", message: "请填写新版本名称"});
            return false;
        }
        $.get("build/?a=adb&pid=" + pid + "&b=" + branch + "&u=" + u + "&g_b=" + git_branch, function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "OK") {
                    location.reload();
                }
                else
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
        );
    }
}

function populate_builds() {
    $("tbody[name=build_list]").html("");
    if (v_list != undefined && v_list.length > 0) {
        for (i = 0; i < v_list.length; i++) {
            b = v_list[i];
            add_build(b["id"], b["version"], b["build_master"], b["time"], b["status"], b["certified"]);
        }
    }
}

function generate_pager() {
    page_items = PAGE_STEP;
    if (v_count != 0 && v_list != undefined && v_count > page_items) {
        p = parseInt(get_href_v("p"));
        if (isNaN(p))
            p = 1;
        pages = Math.ceil(v_count / page_items);
        if (p > pages)
            p = pages;
        pid = get_href_v("pid");
        bid = get_href_v("bid");
        pager_href = set_href_v("pid", pid);
        pager_href = set_href_v("bid", bid, pager_href);
        min_p = Math.max(2, p - 10);
        if (p == pages)
            max_p = pages;
        else
            max_p = Math.min(p + 10, pages);
        first_surfix = "";
        last_prefix = "";
        if (min_p > 2)
            first_surfix = "...";
        if (max_p < pages - 2)
            last_prefix = "...";
        if (p < 2) {
            prev = "<li class=\"disabled\"><a href=\"#\">&larr;</a></li>";
            first_page = "<li class=\"active\"><a href=\"#\">1</a></li>";
        }
        else {
            prev = "<li><a href=\"" + set_href_v("p", p - 1, pager_href) + "\">&larr;</a></li>";
            first_page = "<li><a href=\"" + set_href_v("p", "1", pager_href) + "\">1" + first_surfix + "</a></li>";
        }
        if (p >= pages) {
            next = "<li class=\"disabled\"><a href=\"#\">&rarr;</a></li>";
            last_page = "<li class=\"active\"><a href=\"#\">" + pages + "</a></li>";
        }
        else {
            next = "<li><a href=\"" + set_href_v("p", p + 1, pager_href) + "\">&rarr;</a></li>";
            last_page = "<li><a href=\"" + set_href_v("p", pages, pager_href) + "\">" + last_prefix + pages + "</a></li>";
        }
        added = "<ul class=\"pagination\">" + prev + first_page;
        for (i = min_p; i < max_p; i++) {
            if (p == i)
                added += "<li class=\"active\"><a href=\"#\">" + i + "</a></li>";
            else
                added += "<li><a href=\"" + set_href_v("p", i, pager_href) + "\">" + i + "</a></li>";
        }
        added += last_page + next + "</ul>";
    }
    else
        added = "";
    $("div#build_pager").html(added);
}

function build_pop() {
    pid = get_href_v("pid");
    bid = get_href_v("bid");
    if (bid == null) {
        if (current_bid == "0") {
            return;
        }
        else {
            bid = current_bid;
        }
    }
    if (pid != null && bid != null && bid != "0") {
        $("div#BuildModal").find("div[name=prod]").text(current_prod);
        $("div#BuildModal").find("div[name=branch]").text(current_branch);
        added = "<table class=\"table table-bordered\" style=\"margin-bottom: 0px;\">";
        for (i in m_list) {
            module = m_list[i];
            if (i % 5 == 0) {
                added += "<tr>";
            }
            added += "<td width=\"20%\" class=\"text-center\"><label>" + module["name"] + "<br><input type=\"checkbox\" name=\"module\" mid=\"" + module["id"] + "\" checked></label></td>";
            if (i % 5 == 4) {
                added += "</tr>";
            }
        }
        if (i % 5 != 4) {
            added += "</tr>";
        }
        added += "</table>";
        $("div#BuildModal").find("div[name=module]").html(added);
        $("div#BuildModal").modal("show");
    }
}

function branch_pop() {
    pid = get_href_v("pid");
    if (pid != null) {
        $("div#BranchModal").find("div[name=prod]").text(current_prod);
        $("div#BranchModal").modal("show");
    }
}

function build_details(obj) {
    var url = $(obj).attr("value");
    $.get("view/?a=bdd&url=" + url,
        function (data, status) {
            var response = JSON.parse(data);
            $("#build_details").find("div[name=area_body]").html(response["msg"]);
            $("#build_details").modal("show");
            return true;
        }
    )
}

$(function () {
        $("div[name=prod_list]").on('click', 'li a', function () {
                pid = $(this).attr("pid");
                c_pid = get_href_v("pid");
                if (pid != c_pid)
                    document.location.href = "?m=build&pid=" + pid;
            }
        );
        $("div[name=branch_list]").on('click', 'li a', function () {
                pid = get_href_v("pid");
                bid = $(this).attr("pid");
                c_bid = get_href_v("bid");
                if (bid != c_bid)
                    document.location.href = "?m=build&pid=" + pid + "&bid=" + $(this).attr("pid");
            }
        );
    }
);
