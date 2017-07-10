function logout() {
    $.get("login/?a=lot",
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "注销出错", message: response["msg"]});
                return false;
            }
            else {
                window.location.reload();
            }
        }
    );
}

function show_recover() {
    $("div#RecoverModal").modal("show");
}

function recover() {
    u = $("div#RecoverModal").find(":text[name=username]").val();
    if (u.length == 0) {
        BootstrapDialog.show({title: "信息不足", message: "请填写登录用户名或账号邮件地址"});
        return false;
    }
    $.get("user/?a=rep&u=" + u,
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "执行出错", message: response["msg"]});
                return false;
            }
            else {
                BootstrapDialog.show({title: "申请成功", message: response["msg"]});
                $("div#RecoverModal").modal("hide");
                $("div#LoginModal").modal("hide");
                return true;
            }
        }
    );
}

function show_login() {
    $("div#LoginModal").modal("show");
}

function login() {
    username = $("div#LoginModal").find(":text[name=username]").val();
    password = $("div#LoginModal").find(":password[name=password]").val();
    if (username.length == 0) {
        BootstrapDialog.show({title: "信息不足", message: "请填写登录用户名"});
        return false;
    }
    if (password.length == 0) {
        BootstrapDialog.show({title: "信息不足", message: "请填写密码"});
        return false;
    }
    $.get("login/?a=log&u=" + username + "&p=" + $.md5(password),
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "登录出错", message: response["msg"]});
                return false;
            }
            else {
                if (response["status"] == "FALSE") {
                    BootstrapDialog.show({title: "登录失败", message: response["msg"]});
                    return false;
                }
                else {
                    window.location.reload();
                }
            }
        }
    );
}

function new_login() {
    username = $("div#LoginModal").find(":text[name=new_username]").val();
    password = $("div#LoginModal").find(":password[name=new_password]").val();
    password_c = $("div#LoginModal").find(":password[name=new_confirm]").val();
    email = $("div#LoginModal").find(":text[name=new_email]").val();
    display = $("div#LoginModal").find(":text[name=new_display]").val();
    empty = "";
    if (username == undefined || username.length == 0) {
        empty += "用户名 ";
    }
    if (password == undefined || password.length == 0) {
        empty += "密码 ";
    }
    if (email == undefined || email.length == 0) {
        empty += "邮件地址";
    }
    if (empty.length > 0) {
        BootstrapDialog.show({title: "信息不全", message: "请补齐以下信息：" + empty});
        return false;
    }
    if (password.length < 8) {
        BootstrapDialog.show({title: "密码长度不足", message: "请使用至少8位密码"});
        return false;
    }
    if (password != password_c) {
        BootstrapDialog.show({title: "确认密码不符", message: "确认密码不符，请重新输入"});
        return false;
    }
    if (display == undefined || display.length == 0) {
        display = username;
    }
    password = $.md5(password);
    newuser = {"username": username, "password": password, "email": email, "display": display};
    $.post("login/?a=nwu", newuser,
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "注册失败", message: response["msg"]});
                return false;
            }
            else {
                window.location.reload();
            }
        }
    );
}

function bsConfirm(question) {
    var defer = $.Deferred();
    BootstrapDialog.show({
        type: BootstrapDialog.TYPE_PRIMARY,
        title: '等待确认',
        message: question,
        closeByBackdrop: false,
        closeByKeyboard: false,
        draggable: true,
        buttons: [{
            label: '是',
            action: function (dialog) {
                defer.resolve(true);
                dialog.close();
            }
        }, {
            label: '否',
            action: function (dialog) {
                defer.resolve(false);
                dialog.close();
            }
        }],
        close: function (dialog) {
            dialog.remove();
        }
    });
    return defer.promise();
}

function get_href_v(key) {
    if (key == undefined || key.length < 1)
        return null;
    href = window.location.href;
    key_eq = key + "=";
    value = null;
    if (href.indexOf("?" + key_eq) > 0)
        value = href.substring(href.indexOf("?" + key_eq)).split('&')[0].substring(key_eq.length + 1);
    if (href.indexOf("&" + key_eq) > 0)
        value = href.substring(href.indexOf("&" + key_eq) + 1).split('&')[0].substring(key_eq.length);
    if (value != null && value.length > 0 && value[value.length - 1] == "#")
        value = value.substring(0, value.length - 1);
    return value;
}

function set_href_v(key, value, s) {
    if (key == undefined || key.length < 1)
        return null;
    if (s == undefined || s == null || s.length == 0) {
        href = window.location.href;
    }
    else {
        href = s;
    }
    if (href[href.length - 1] == "#")
        href = href.substring(0, href.length - 1);
    key_eq = key + "=";
    start = href.indexOf("?" + key_eq);
    if (start < 0) {
        start = href.indexOf("&" + key_eq);
    }
    if (start < 0) {
        mark = href.indexOf("?") < 0 ? "?" : "&";
        href += mark + key_eq + value;
        return href;
    }
    else {
        prefix = href.substring(0, start + 1 + key_eq.length);
        tail = href.substring(start + 1 + key_eq.length);
        next_key = tail.indexOf("&");
        if (next_key < 0) {
            return prefix + value;
        }
        else {
            surfix = tail.substring(next_key);
            return prefix + value + surfix;
        }
    }
}

function toggle_dis_rm_button(active, dis, rm, dis_Y_title, dis_N_title, dis_Y_class, dis_N_class) {
    title = {"Y": "已启用", "N": "已禁用"};
    if (dis_Y_title != undefined && dis_Y_title != null) {
        title["Y"] = dis_Y_title;
    }
    if (dis_N_title != undefined && dis_N_title != null) {
        title["N"] = dis_N_title;
    }
    dis_class = {"Y": "btn-success", "N": "btn-default"};
    if (dis_Y_class != undefined && dis_Y_class != null) {
        dis_class["Y"] = dis_Y_class
    }
    if (dis_N_class != undefined && dis_N_class != null) {
        dis_class["N"] = dis_N_class
    }
    if (active == "Y") {
        if (dis != undefined && dis != null && $(dis) != undefined) {
            $(dis).removeClass(dis_class["N"]);
            $(dis).addClass(dis_class["Y"]);
            $(dis).text(title["Y"]);
        }
        if (rm != undefined && rm != null && $(rm) != undefined) {
            $(rm).removeClass("btn-danger");
            $(rm).addClass("btn-default");
            $(rm).attr("disabled", "true");
        }
    }
    else {
        if (dis != undefined && dis != null && $(dis) != undefined) {
            $(dis).removeClass(dis_class["Y"]);
            $(dis).addClass(dis_class["N"]);
            $(dis).text(title["N"]);
        }
        if (rm != undefined && rm != null && $(rm) != undefined) {
            $(rm).removeClass("btn-default");
            $(rm).addClass("btn-danger");
            $(rm).removeAttr("disabled");
        }
    }
}

function toggle_modal(obj, action) {
    var top_p = ($(window).height() - $(obj).height()) / 2;
    var left = ($("body").width() - $(obj).width()) / 2;
    var scrollTop = $(document).scrollTop();
    var scrollLeft = $(document).scrollLeft();
    $(obj).css({position: 'absolute', 'top': top_p + scrollTop, 'left': left + scrollLeft});
    if (action == "show")
        $(obj).show();
    else
        $(obj).hide();
}

function add_dropdown_list(mode, list, id, title, obj, extra) {
    if (list != undefined) {
        c_id = "0";
        s_p = title;
        o_s = "<ul class=\"dropdown-menu\" role=\"menu\" aria-labelledby=\"dropdownMenu\">";
        o_e = "</ul>";
        s = "";
        o = "";
        if (extra == undefined) {
            extra = "";
        }
        for (index in list) {
            l_item = list[index];
            if (id == l_item["id"].toString()) {
                c_id = l_item["id"].toString();
                s_p = l_item["name"];
                s = "<li><a href=\"#\" pid=\"" + c_id + "\">" + s_p + "</a></li><li class=\"divider\"></li>";
            }
            else {
                o += "<li><a href=\"#\" pid=\"" + l_item["id"].toString() + "\">" + l_item["name"] + "</a></li>";
            }
        }
        added = "<button type=\"button\" class=\"btn btn-default dropdown-toggle\" name=\"" + mode + "\" data-toggle=\"dropdown\" pid=\"" + c_id + "\">" + s_p + "<span class=\"caret\"></span></button>" + o_s + s + extra + o + o_e;
        $(obj).html(added);
    }
}
