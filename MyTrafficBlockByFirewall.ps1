#Requires -RunAsAdministrator

### 网络访问控制工具

# 限制访问：
Register-ScheduledJob -Name "MyTrafficBlock" -ScriptBlock{
    # 不限制时段：06:00-23:00
    if( ( ((Get-Date -Format "HH:mm").CompareTo("06:00") -eq 1) -and ((Get-Date -Format "HH:mm").CompareTo("23:00") -eq -1) ) ){ # 不限制时段
        netsh advfirewall firewall delete rule name="MyBlock"
    }else{  # 限制主动访问
        # 检验规则是否已经生效过
        Netsh advfirewall firewall show rule name="MyBlock"
        if($? -eq $false){  # 没有生效过，是第一次创建规则
            # 随手写
            netsh advfirewall firewall add rule name="MyBlock" dir=out action=allow remoteip=101.132.163.77

            # 屏蔽所有IP
            netsh advfirewall firewall add rule name="MyBlock" dir=out action=block remoteip=any
        }
    }
} -Trigger (    # 每一分钟执行一次
    New-JobTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval '00:01:00' -RepeatIndefinitely
)


# 移除限速任务：
#Unregister-ScheduledJob "MyTrafficBlock"
#netsh advfirewall firewall delete rule name="MyBlock"