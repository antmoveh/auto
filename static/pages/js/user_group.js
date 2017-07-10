var group = {};
var user_group = {};

$(document).ready(function () {
    load_page();
});

function load_page() {
    $.get("user_group/?a=ugp", function (data, status) {
            var response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                group = response["msg"]["group"];
                user_group = response["msg"]["user_group"];
                populate_info();
            }
        }
    );
}

function populate_info() {
    var added = "<table class=\"table table-bordered\" name=\"host\"><tbody>";
    for (var key in group) {
        added += "<tr><td width=\"10%\"><button class=\"btn btn-default\" type=\"button\" onclick=\"del_obj(this);\" gid=" + key + ">" + group[key] + "&nbsp;&nbsp;&nbsp;&nbsp;<b><font color=\"red\">x</font></b></button></td>";
        added += "<td width=\"90%\"><div class=\"group_\" style=\"min-height: 35px; overflow:auto;\" gid=" + key + ">&nbsp;" + user(key) + "</div></td></tr>"
    }
    added += "</tbody></table>";
    $("div#group").append(added);
    drags();
}

function user(key) {
    var added = "";
    if (user_group[key].length > 0) {
        for (var i in user_group[key]) {
            added += "<div class=\"user_\" draggable=\"true\" uid=" + user_group[key][i][0] + ">" + user_group[key][i][1] + "</div>";
        }
    }
    return added;
}

function drags() {
    var user_ = $(".user_");
    var group_ = $(".group_");
    var eleDrag = null;
    for (var i = 0; i < user_.length; i++) {
        user_[i].ondragstart = function (ev) {
            ev.dataTransfer.effectAllowed = "move";
            ev.dataTransfer.setData("text", ev.target.innerHTML);
            ev.dataTransfer.setDragImage(ev.target, 0, 0);
            eleDrag = ev.target;
            return true;
        };
        user_[i].ondragend = function (ev) {
            ev.dataTransfer.clearData("text");
            eleDrag = null;
            return false
        };
    }
    for (var i = 0; i < group_.length; i++) {
        group_[i].ondragover = function (ev) {
            ev.preventDefault();
            return true;
        };
        group_[i].ondragleave = function (ev) {
            this.style.boxShadow = "";
            return true;
        };
        group_[i].ondragenter = function (ev) {
            this.style.boxShadow = "0px 0px 10px 10px #F5F5DC inset";
            return true;
        };
        group_[i].ondrop = function (ev) {
            if (eleDrag) {
                this.appendChild(eleDrag);
            }
            this.style.boxShadow = "";
            var uid = $(eleDrag).attr("uid");
            var gid = $(this).attr("gid");
            move_user(uid, gid);
            return false;
        };
    }
}

function show_add_group() {
    $("div#GroupModal").modal("show");
}

function add_group() {
    var group_name = $("#GroupModal").find(":text[name=groupname]").val();
    if (group_name == "") {
        BootstrapDialog.show({title: "执行出错！", message: "分组名不能为空"});
        return false;
    }
    $.get("user_group/?a=agu&gn=" + group_name, function (data, status) {
            var response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                window.location = "?m=user_group";
                return true;
            }
        }
    );
}

function del_obj(obj) {
    var gid = $(obj).attr("gid");
    bsConfirm("是否确定删除该分组？").then(function (r) {
        if (r) {
            $.get("user_group/?a=dgu&gid=" + gid, function (data, status) {
                var response = JSON.parse(data);
                if (response["status"] == "FAILED") {
                    BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                    return false;
                }
                else {
                    $(obj).parent().parent().remove();
                    return true;
                }
            });
        }
        else
            return false;
    });
}

function move_user(uid, gid) {
    $.get("user_group/?a=mug&uid=" + uid + "&gid=" + gid, function (data, status) {
            var response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错！", message: response["msg"]});
                return false;
            }
            else {
                return true;
            }
        }
    );
}
