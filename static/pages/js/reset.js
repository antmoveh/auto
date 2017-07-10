function reset_password() {
    old_password = "12345678";
    password = $(":password[name=new_pass]").val();
    pass_confirm = $(":password[name=confirm]").val();
    if (password.length < 8) {
        BootstrapDialog.show({title: "密码长度不足", message: "密码长度应不少于8位"});
        return false;
    }
    if (pass_confirm != password) {
        BootstrapDialog.show({title: "密码设置错误", message: "确认密码与设置密码不相等"});
        return false;
    }
    old_password = $.md5(old_password);
    password = $.md5(password);
    $.get("?a=rpf&op=" + old_password + "&p=" + password,
        function (data, status) {
            response = JSON.parse(data);
            if (response["status"] == "FAILED") {
                BootstrapDialog.show({title: "登录出错", message: response["msg"]});
                return false;
            }
            else {
                document.location.href = "/";
            }
        }
    );
}
