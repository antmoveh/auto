/* spig.js */
//右键菜单
jQuery(document).ready(function ($) {
    $("#spig").mousedown(function (e) {
        if (e.which == 3) {
            showMessage("秘密通道:<br />私聊管理员并发送验证码ekWA62uG，有惊喜哦", 10000);
        }
    });
    $("#spig").bind("contextmenu", function (e) {
        return false;
    });
});

//鼠标在消息上时
jQuery(document).ready(function ($) {
    $("#message").hover(function () {
        $("#message").fadeTo("100", 1);
    });
});


//鼠标在上方时
jQuery(document).ready(function ($) {
    //$(".mumu").jrumble({rangeX: 2,rangeY: 2,rangeRot: 1});
    $(".mumu").mouseover(function () {
        $(".mumu").fadeTo("300", 0.3);
        msgs = ["我隐身了，你看不到我", "我会隐身哦！嘿嘿！", "别动手动脚的，把手拿开！", "把手拿开我才出来！"];
        var i = Math.floor(Math.random() * msgs.length);
        showMessage(msgs[i]);
    });
    $(".mumu").mouseout(function () {
        $(".mumu").fadeTo("300", 1)
    });
});

//开始
jQuery(document).ready(function ($) {
    if (isindex) { //如果是主页
        var now = (new Date()).getHours();
        if (now > 0 && now <= 6) {
            showMessage(visitor + ' 你是夜猫子呀？还不睡觉，明天起的来么你？', 6000);
        } else if (now > 6 && now <= 11) {
            showMessage(visitor + ' 早上好，早起的鸟儿有虫吃噢！早起的虫儿被鸟吃，你是鸟儿还是虫儿？嘻嘻！', 6000);
        } else if (now > 11 && now <= 14) {
            showMessage(visitor + ' 中午了，吃饭了么？不要饿着了，饿死了谁来挺我呀！', 6000);
        } else if (now > 14 && now <= 18) {
            showMessage(visitor + ' 中午的时光真难熬！还好有你在！', 6000);
        } else {
            showMessage(visitor + ' 快来逗我玩吧！', 6000);
        }
    }
    else {
        showMessage('欢迎' + visitor + '来到代码笔记《' + title + '》', 6000);
    }
    $(".spig").animate({
            top: $(".spig").offset().top + 300,
            left: document.body.offsetWidth - 160
        },
        {
            queue: false,
            duration: 1000
        });
});

//鼠标在某些元素上方时
jQuery(document).ready(function ($) {
    $('#LoginModal').mouseover(function () {
        showMessage('注册之后联系管理员分配权限哦');
    });
    $('#prev-page').mouseover(function () {
        showMessage('要翻到上一页吗?');
    });
    $('#next-page').mouseover(function () {
        showMessage('要翻到下一页吗?');
    });
});

//execdb.html
jQuery(document).ready(function ($) {
    $('div[name=dbs_list]').delegate('label input', 'mouseover', function () {
        $.get('hint_login/?a=gdb&did=' + $(this).attr("dbid"), function (data, status) {
                var response = JSON.parse(data);
                showMyMessage(response['msg']);
            }
        );
    })
});


//无聊讲点什么
jQuery(document).ready(function ($) {

    window.setInterval(function () {
        msgs = ["陪我聊天吧！", "好无聊哦，你都不陪我玩！", "我可爱吧！嘻嘻!~^_^!~~", "谁淫荡呀?~谁淫荡?，你淫荡呀!~~你淫荡！~~", "从前有座山，山上有座庙，庙里有个老和尚给小和尚讲故事，讲：“从前有座……”",
            "【项目环境】配置服务器地址及其Tomcat位置哦", "【产品&部署】配置产品的编译工程及部署步骤", "【数据库】为产品添加数据库信息", "【配置文件】编辑产品的配置文件", "【编译】选择分支编译版本哦",
            "【部署】将编译好的版本部署到服务器上", "【测试】自动化脚本维护及测试", "【用户】编辑个人信息及订阅邮件", "【分组管理】管理员用的模块哦", "小提示：不会的时候看下别人配置哦",
            "有任何疑难问题请联系管理员QQ1758867257", "千万级表ALTER要要几十分到数小时,请做好准备", "数十万表ALTER仅仅一分钟哦", "部署步骤选强制关闭Tomcat是Kill操作", "配置编译工程一定要与jenkins工程名一致",
            ""];
        var i = Math.floor(Math.random() * msgs.length);
        showMessage(msgs[i], 10000);
    }, 15000);
});

//无聊动动
jQuery(document).ready(function ($) {
    window.setInterval(function () {
        msgs = ["乾坤大挪移！", "我飘过来了！~", "我飘过去了", "我得意地飘！~飘！~"];
        var i = Math.floor(Math.random() * msgs.length);
        s = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.75];
        var i1 = Math.floor(Math.random() * s.length);
        var i2 = Math.floor(Math.random() * s.length);
        $(".spig").animate({
                left: document.body.offsetWidth / 2 * (1 + s[i1]),
                top: document.body.offsetHeight / 2 * (1 + s[i1])
            },
            {
                duration: 2000,
                complete: showMessage(msgs[i])
            });
    }, 45000);
});

var spig_top = 50;
//滚动条移动
jQuery(document).ready(function ($) {
    var f = $(".spig").offset().top;
    $(window).scroll(function () {
        $(".spig").animate({
                top: $(window).scrollTop() + f + 300
            },
            {
                queue: false,
                duration: 1000
            });
    });
});

//鼠标点击时
jQuery(document).ready(function ($) {
    var stat_click = 0;
    $(".mumu").click(function () {
        if (!ismove) {
            stat_click++;
            if (stat_click > 4) {
                msgs = ["你有完没完呀？", "你已经摸我" + stat_click + "次了", "非礼呀！救命！OH，My ladygaga"];
                var i = Math.floor(Math.random() * msgs.length);
                //showMessage(msgs[i]);
            } else {
                msgs = ["筋斗云！~我飞！", "我跑呀跑呀跑！~~", "别摸我，大男人，有什么好摸的！", "惹不起你，我还躲不起你么？", "不要摸我了，我会告诉老婆来打你的！", "干嘛动我呀！小心我咬你！"];
                var i = Math.floor(Math.random() * msgs.length);
                //showMessage(msgs[i]);
            }
            s = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.75];
            var i1 = Math.floor(Math.random() * s.length);
            var i2 = Math.floor(Math.random() * s.length);
            $(".spig").animate({
                    left: document.body.offsetWidth / 2 * (1 + s[i1]),
                    top: document.body.offsetHeight / 2 * (1 + s[i1])
                },
                {
                    duration: 500,
                    complete: showMessage(msgs[i])
                });
        } else {
            ismove = false;
        }
    });
});
//显示消息函数 
function showMessage(a, b) {
    if (b == null) b = 10000;
    jQuery("#message").hide().stop();
    jQuery("#message").html(a);
    jQuery("#message").fadeIn();
    jQuery("#message").fadeTo("1", 1);
    jQuery("#message").fadeOut(b);
}
function showMyMessage(a, b) {
    if (b == null) b = 10000;
    jQuery("#mymessage").hide().stop();
    jQuery("#mymessage").html(a);
    jQuery("#mymessage").fadeIn();
    jQuery("#mymessage").fadeTo("1", 1);
    jQuery("#mymessage").fadeOut(b);
}

//拖动
var _move = false;
var ismove = false; //移动标记
var _x, _y; //鼠标离控件左上角的相对位置
jQuery(document).ready(function ($) {
    $("#spig").mousedown(function (e) {
        _move = true;
        _x = e.pageX - parseInt($("#spig").css("left"));
        _y = e.pageY - parseInt($("#spig").css("top"));
    });
    $(document).mousemove(function (e) {
        if (_move) {
            var x = e.pageX - _x;
            var y = e.pageY - _y;
            var wx = $(window).width() - $('#spig').width();
            var dy = $(document).height() - $('#spig').height();
            if (x >= 0 && x <= wx && y > 0 && y <= dy) {
                $("#spig").css({
                    top: y,
                    left: x
                }); //控件新位置
                ismove = true;
            }
        }
    }).mouseup(function () {
        _move = false;
    });
});
