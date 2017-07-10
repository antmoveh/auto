var case_list = [];
var confs = [];
var confs_info = {};
var result_list = [];

$(document).ready(function () {
    get_test_conf();
    get_caselist();
});

function get_caselist() {
    if (case_list.length == 0) {
        $.get('autotest/?a=gcl', function (data, status) {
                response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                    return false;
                }
                else {
                    case_list = response["msg"];
                    script_lists();
                    populate_lists();
                }
            }
        );
    }
}

function get_test_conf() {
    var cid = get_href_v("cid");
    if (cid == null)
        cid = "";
    else
        cid = "&cid=" + cid;
    $.get("autotest/?a=gtc" + cid, function (data, status) {
            var response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                confs = response["msg"]["confs"];
                confs_info = response["msg"]["confs_info"];
                show_conf_list();
                populate_conf_info();
            }
        }
    );
}

function script_lists() {
    if (case_list.length > 0) {
        var l_s = "<table width=\"100%\" class=\"table-bordered\"><tbody>";
        var l_e = "</tbody></table>";
        var counter = 0;
        var added = "";
        for (var c_l in case_list) {
            var c = case_list[c_l];
            var cid = c[0].toString();
            var cname = c[1].toString();
            var prefix = "";
            var surfix = "";
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
            added += prefix + "<td width=\"20%\" style=\"vertical-align: top;\"><div class=\"panel panel-info\" style=\"margin-bottom: 0px;\"><div class=\"panel-heading\" align=\"center\" name=\"ph\" cid=\"" + cid + "\">";
            added += "<div class=\"input-group\"><span class=\"input-group-addon\"><input type=\"checkbox\" name=\"check_box\" cid=\"" + cid + "\" value=\"" + cname + "\"></span>";
            added += "<span class=\"input-group-addon\">" + cname + "</span></div></div>";
            added += "</div></td>" + surfix;
        }
        added = l_s + added + l_e;
        $("div[name=script_list]").html(added);
    }
}


function populate_lists() {
    if (case_list.length > 0) {
        var l_s = "<table width=\"100%\" class=\"table-bordered\"><tbody>";
        var l_e = "</tbody></table>";
        var counter = 0;
        var added = "";
        for (var c_l in case_list) {
            var c = case_list[c_l];
            var cid = c[0].toString();
            var cname = c[1].toString();
            var cdescription = c[2].toString();
            var cparam = c[3].toString();
            var ccall = c[4].toString();
            var prefix = "";
            var surfix = "";
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
            added += prefix + "<td width=\"20%\" style=\"vertical-align: top;\"><div class=\"panel panel-info\" style=\"margin-bottom: 0px;\"><div class=\"panel-heading\" align=\"center\" name=\"ph\" cid=\"" + cid + "\">";
            added += "<div class=\"input-group\"><span class=\"input-group-addon\"><input type=\"checkbox\" name=\"check_box\" cid=\"" + cid + "\" value=\"" + cname + "\"></span>";
            added += "<span class=\"input-group-addon\" onclick=\"collapse_panel(this);\">" + cname + "</span></div></div><div class=\"panel-collapse collapse\" name=\"pb\" cid=\"" + cid + "\">";
            added += "<div class=\"panel-body\" name=\"body_content\"><table class=\"table\" style=\"margin-bottom: 0px;\"><tbody>";
            added += "<tr><td><textarea disabled=\"disabled\" style=\"width: 100%; height: 101px;\" name=\"" + cid + "description\">" + cdescription + "</textarea></td></tr>";
            added += "<tr><td><textarea disabled=\"disabled\" style=\"width: 100%; height: 101px;\" name=\"" + cid + "param\">" + cparam + "</textarea></td></tr>";
            added += "<tr><td><textarea disabled=\"disabled\" style=\"width: 100%; height: 101px;\" name=\"" + cid + "call\">" + ccall + "</textarea></td></tr>";
            added += "</tbody></table></div></div></div></div></td>" + surfix;
        }
        added = l_s + added + l_e;
        $("div[name=case_list]").html(added);
    }
}

function collapse_panel(obj) {
    $(obj).parent().parent().parent().find("div[name=pb]").collapse('toggle');
}

function show_add_case() {
    $("div#CaseModal").find(":hidden[name=case_id]").attr("value", 0);
    $("div#CaseModal").find(":text[name=casename]").val("");
    $("div#CaseModal").find("textarea[name=description]").val("");
    $("div#CaseModal").find("textarea[name=param]").val("");
    $("div#CaseModal").find("textarea[name=call]").val("");
    $("div#CaseModal").modal('show');
}

function show_edit_case() {
    var i = 0;
    var cid = "";
    var cname = "";
    var description = "";
    var param = "";
    var call = "";
    $("#casetable").find(":checkbox[name=check_box]").each(function () {
        if ($(this).prop("checked")) {
            cid = $(this).attr("cid");
            cname = $(this).prop("value");
            description = $("#casetable").find("textarea[name=" + cid + "description]").val();
            param = $("#casetable").find("textarea[name=" + cid + "param]").val();
            call = $("#casetable").find("textarea[name=" + cid + "call]").val();
            i++;
        }
    });
    if (i == 1) {
        $("div#CaseModal").find(":hidden[name=case_id]").attr("value", cid);
        $("div#CaseModal").find(":text[name=casename]").val(cname);
        $("div#CaseModal").find("textarea[name=description]").val(description);
        $("div#CaseModal").find("textarea[name=param]").val(param);
        $("div#CaseModal").find("textarea[name=call]").val(call);
        $("div#CaseModal").modal('show');
    } else {
        BootstrapDialog.show({title: "执行出错！", message: "请选择一个用例编辑"});
    }
}

function add_case() {
    var cid = $("div#CaseModal").find(":hidden[name=case_id]").attr("value");
    var cname = $("div#CaseModal").find(":text[name=casename]").val();
    if (cname == "") {
        BootstrapDialog.show({title: "执行出错！", message: "用例名不能为空"});
        return false;
    }
    var description = $("div#CaseModal").find("textarea[name=description]").val();
    var cparam = $("div#CaseModal").find("textarea[name=param]").val();
    var ccall = $("div#CaseModal").find("textarea[name=call]").val();
    var request = {"cid": cid, "cname": cname, "description": description, "cparam": cparam, "ccall": ccall};
    $.post("autotest_script/?a=adc", {"request": JSON.stringify(request)},
        function (data, status) {
            var response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                window.location = "?m=test";
                return true;
            }
        });
}

function delete_case() {
    var index = 0;
    $("#casetable").find(":checkbox[name=check_box]").each(function () {
        if ($(this).prop("checked")) {
            index++;
        }
    });
    if (index == 0) {
        BootstrapDialog.show({title: "执行出错！", message: "至少选择一个用例"});
        return false;
    }
    bsConfirm("是否确定删除用例？").then(function (r) {
            if (r) {
                $("#casetable").find(":checkbox[name=check_box]").each(function () {
                    if ($(this).prop("checked")) {
                        var cid = $(this).attr("cid");
                        $.get("autotest_script/?a=dec&cid=" + cid,
                            function (data, status) {
                                var response = JSON.parse(data);
                                if (response["status"] == "FAILED") {
                                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                                    return false;
                                }
                                else {
                                    window.location = "?m=test";
                                    return true;
                                }
                            })
                    }
                });
            }
            else
                return false;
        }
    );
}

function show_add_para() {
    var cid = $("#case_conf").find(":text[name=conf_name]").attr("pid");
    var case_list = "";
    $("#case_conf").find(":checkbox[name=check_box]").each(function () {
        if ($(this).prop("checked")) {
            case_list += $(this).attr("cid") + ",";
        }
    });
    if (case_list != "") {
        case_list = "&case_list=" + case_list;
    }
    $.get("autotest/?a=sap&cid=" + cid + case_list, function (data, status) {
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

function show_add_temp() {
    var cid = $("#case_conf").find(":text[name=conf_name]").attr("pid");
    $.get("autotest/?a=noy&cid=" + cid, function (data, status) {
            var response = JSON.parse(data);
            $("div#TempModal").find("p[name=hint]").html(response["msg"])
        }
    );
    $("div#TempModal").find(":text[name=file_pid]").attr("value", cid);
    $("div#TempModal").modal("show")
}

function show_conf_list() {
    var o_s = "<ul class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu\" style=\"height:545px;overflow:scroll\">";
    var o_e = "</ul>";
    var selected = "";
    var o = "";
    var pid = "0";
    var s_p = "匿名测试";
    var current_sid = get_href_v("cid");
    for (var index in confs) {
        var s = confs[index];
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
        o = "<li><a href=\"#\" pid=\"0\">匿名测试</a></li>" + o;
    }
    var added = "<button type=\"button\" class=\"btn btn-default dropdown-toggle col-lg-12\" name=\"servers\" data-toggle=\"dropdown\" pid=\"" + pid + "\">" + s_p + "<span class=\"caret\"></span></button>" + o_s + selected + o + o_e;
    $("div[name=test_conf]").html(added);
}

function populate_conf_info() {
    if (Object.keys(confs_info).length == 4) {
        $("#case_conf").find(":text[name=conf_name]").attr("pid", confs_info["id"]);
        $("#case_conf").find(":text[name=conf_name]").val(confs_info["name"]);
        var c_l = confs_info["case_list"];
        setTimeout(function () {
            $("#case_conf").find(":checkbox[name=check_box]").each(function () {
                if (c_l.indexOf($(this).attr("cid")) > -1) {
                    $(this).attr("checked", "true");
                }
            });
        }, 100);
    }
}

function delete_conf() {
    var cid = $("#case_conf").find(":text[name=conf_name]").attr("pid");
    if (cid == 0) {
        BootstrapDialog.show({title: "执行出错！", message: "请选择要删除的测试配置"});
        return false;
    }
    bsConfirm("是否确定删除测试配置？").then(function (r) {
        if (r) {
            $.get("autotest/?a=dc&cid=" + cid, function (data, status) {
                var response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                    return false;
                }
                else {
                    window.location = "?m=test";
                    return true;
                }
            });
        } else {
            return false;
        }
    });
}

function submit_action() {
    var cid = $("#case_conf").find(":text[name=conf_name]").attr("pid");
    var cname = $("#case_conf").find(":text[name=conf_name]").val();
    if (cname == "") {
        BootstrapDialog.show({title: "执行出错！", message: "名称不能为空"});
        return false;
    }
    var case_list = "";
    $("#case_conf").find(":checkbox[name=check_box]").each(function () {
        if ($(this).prop("checked")) {
            case_list += $(this).attr("cid") + ",";
        }
    });
    var request = {"cid": cid, "cname": cname, "case_list": case_list};
    toggle_modal($("div#loading"), "show");
    $.post("autotest/?a=sat", {
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
                if (cid == "0") {
                    window.location = "?m=test&cid=" + response["msg"]["cid"];
                }
                else {
                    BootstrapDialog.show({title: "执行成功", message: "执行成功"});
                }
                return true;
            }
        }
    );
}

function submit_area() {
    var cid = $("#case_conf").find(":text[name=conf_name]").attr("pid");
    var text = $("div#ParaModal").find("textarea#para_area").val();
    var request = {"cid": cid, "text": text};
    toggle_modal($("div#loading"), "show");
    $.post("autotest/?a=sae", {
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

function execute_action() {
    var cid = $("#case_conf").find(":text[name=conf_name]").attr("pid");
    var case_list = "";
    $("#case_conf").find(":checkbox[name=check_box]").each(function () {
        if ($(this).prop("checked")) {
            case_list += $(this).attr("cid") + ",";
        }
    });
    if (case_list != "") {
        case_list = "&case_list=" + case_list;
    }
    if (cid == 0 && case_list == "") {
        BootstrapDialog.show({title: "执行出错！", message: "匿名测试必须指定测试脚本"});
        return false;
    }
    toggle_modal($("div#loading"), "show");
    $.get("autotest_login/?a=eca&cid=" + cid + case_list, function (data, status) {
        var response = JSON.parse(data);
        toggle_modal($("div#loading"), "hide");
        if (response["status"] == "FAILED") {
            BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
            return false;
        }
        else {
            BootstrapDialog.show({title: "执行成功", message: response["msg"]});
            return true;
        }
    });
}

function show_result_list() {
    var cid = $("#case_conf").find(":text[name=conf_name]").attr("pid");
    $.get("autotest_login/?a=srl&cid=" + cid, function (data, status) {
        var response = JSON.parse(data);
        if (response["status"] == "FAILED") {
            BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
            return false;
        }
        else {
            result_list = response["msg"];
            generate_list(cid);
            return true;
        }
    });
    $("div#ResultModal").modal("show");
}

function show_result(cid, name) {
    $.get("autotest_login/?a=sr&cid=" + cid + "&name=" + name, function (data, status) {
        var response = JSON.parse(data);
        if (response["status"] == "FAILED") {
            BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
            return false;
        }
        else {
            $("div#ResultModal").find("textarea#right_content").val(response["msg"]);
            return true;
        }
    });
}

function generate_list(cid) {
    if (result_list.length > 0) {
        var body = "";
        for (var i = 0; i < result_list.length; i++) {
            body += "<li><button onclick=\"show_result(" + cid + ",'" + result_list[i] + "');\">" + result_list[i] + "</button></li><br>";
        }
        var htm = "<ul style=\"list-style-type:none\">" + body + "</ul>";
        $("div#ResultModal").find("div#left_name").html(htm);
    }
}

$(function () {
        $("div[name=test_conf]").on('click', 'li a', function () {
                var cid = $(this).attr("pid");
                var current_sid = get_href_v("cid");
                if (cid != current_sid) {
                    if (cid == "0")
                        window.location = "?m=test";
                    else
                        window.location = "?m=test&cid=" + cid;
                }
            }
        );

    }
);

