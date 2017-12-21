layui.define(["layer","table","upload"], function(exports){
    var layer = layui.layer;
    var table = layui.table;
    var upload = layui.upload;
    //初始化加载表格数据
    (function loadBabyList(){
        table.render({
            elem:"#babyList",
            height:666,
            url:"/loadBabyList",
            page:true,//开启分页
            limits:[15,25,50],
            limit:15,
            cols:[[
                {title:"序号",width:60,fixed:"left",type:"numbers"},
                {field:"babyName",title:"宝贝名称",width:350,sort:true,fixed:"left",edit:"text"},
                {field:"babyUrl",title:"宝贝地址",sort:false,edit:"text"},
                {title:"操作",width:120,align:'center',toolbar:'#toolBar',fixed:'right'}
            ]]
        });
        $("#babyList + div").attr("spellcheck",false);//去掉网页的拼写检查
    })();

    //上传文件按钮
    upload.render({
        elem:"#importData",
        url:"/importData",
        accept:"file",
        exts:"db|json",
        multiple:false,
        done:function(res, index, upload){
            if(res){
                reloadBabyList();
                layer.msg("导入数据成功",{
                    time:1000,
                    icon:6
                });
            }
        },
        error:function(index, upload){
            layer.msg("出现错误,请重试",{
                  time:1000,
                  icon:5
             });
        }
    });

    //下载文件
    $("#exportData").on("click",function(){
        window.location.href = "/exportData";
    });

    //重载表格数据
    function reloadBabyList(){
        var val = $("#kd").val().trim();
        if(val === "建心" || val === "jianxin"){
            layer.msg("是个SB",{
              time:1500,
              icon:6
            });
            return false;
        }else if(val === "删库"){
            layer.confirm("真的要从新开始吗?!!",function(index){
                 $.ajax({
                    url:"/reset",
                    method:"GET",
                    success:function(data){
                        if(data){
                            layer.close(index);
                            window.location.href = "/";
                        }
                    }
                });
            });
        }else{//重载表格
            table.reload("babyList",{
                url:"/loadBabyList",
                where:{
                    kd:val
                },
                done:function(){
                    $("#kd").val("");
                }
            })
        }
    }

    //监听工具条
    table.on("tool",function(obj){
        var rowData = obj.data;
        var layEvent = obj.event;
        var tr = obj.tr;

        if(layEvent === "del"){//删除
            layer.confirm('真的要删除么', function(index){
                $.ajax({
                    url:"/delBaby",
                    method:"POST",
                    data:{
                        id:rowData["id"]
                    },
                    dataType:"json",
                    success:function(data){
                        reloadBabyList();
                        layer.close(index);
                    }
                });
            });
        }
    });

    //查询按钮
    $("#search").on("click",reloadBabyList);

    //添加宝贝按钮
    $("#addBaby").on("click",function(){
        var $babyName,$babyUrl,flag;
        layer.open({
            type:1,
            title:["加个宝贝",""],
            btn:'添加',
            id:"addBabyInfo",
            area:"380px",
            content:$("#tpl-addBaby").html(),
            yes:function(index,layero){
                $babyName = $("input[name='babyName']");
                $babyUrl = $("input[name='babyUrl']");
                if($babyName.val() === "" || $babyUrl.val() === ""){
                    layer.msg("宝贝名称和地址不能为空",{
                          time:1000,
                          icon:5
                     })
                     return false;
                }
                $.ajax({
                    url:"/addBaby",
                    dataType:"json",
                    method:"POST",
                    data:{
                        "babyName":$babyName.val(),
                        "babyUrl":$babyUrl.val()
                    },
                    success:function(data){
                        if(data){
                            flag = true;
                            $babyName.val("");
                            $babyUrl.val("");
                            layer.msg("添加成功",{
                                time:1000,
                                icon:6
                            });
                        }
                    }
                });
            },
            end:function(){
                if(flag){
                    reloadBabyList();
                }
            }
        });
    })

    //模块输出名 必须和use时的模块名一致
    exports('index',function(){});
});