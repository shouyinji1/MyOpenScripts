#Requires -RunAsAdministrator

### 网络访问控制工具

# 限制访问：
Register-ScheduledJob -Name "MyTrafficLimit" -ScriptBlock{
    # 不限制时段：20:00-22:00
    if( ( ((Get-Date -Format "HH:mm").CompareTo("20:00") -eq 1) -and ((Get-Date -Format "HH:mm").CompareTo("22:00") -eq -1) ) ){ # 不限速时段
        netsh advfirewall firewall delete rule name="MyLimit"
    }else{  # 限制主动访问
        # 检验规则是否已经生效过
        Netsh advfirewall firewall show rule name="MyLimit"
        if($? -eq $false){  # 没有生效过，是第一次创建规则
            # 百度贴吧：tieba.baidu.com
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=183.240.98.129

            # 好看视频：haokan.baidu.com
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c20:5022:1d2e:0:ff:b0cf:a7ea
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.109.81.22
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.109.81.217
            
            # 东方财富：www.eastmoney.com
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=180.178.245.240
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=36.156.181.92
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=180.178.245.236
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=36.156.181.91
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.27.234
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=120.195.185.111
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=120.195.185.99
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=118.184.241.225
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=118.184.241.223
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=36.150.29.243
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=36.150.29.236
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=36.156.181.95
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=36.156.181.98
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=118.184.217.232
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=118.184.217.229
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c20:a12:105:3::3f4
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8720:800:3b:3::3ef
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c20:1213:10a:3::7f5
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c20:815:114:3::7fc
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c20:9c73:103:3::9
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c20:aa51:23:3::3f3

            # 雪球：xueqiu.com
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=60.205.172.136
        
            # Bilibili：www.bilibili.com
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c20:5624::56
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c28:202:8::195
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c28:202:8::196
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c28:202:8::199
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c20:5624::55
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c20:5624::57
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c28:202:8::202
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2409:8c20:5624::54
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=117.169.96.198
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=117.169.96.199
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.250.54
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.250.53
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=117.169.96.200
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=112.13.92.196
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=112.13.92.202
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.250.57
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=112.13.92.203
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=111.48.57.45
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=112.13.92.199
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.250.55
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=112.13.92.195
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.250.56
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=111.48.57.46
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=111.48.57.44
        
            # 豆瓣
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=140.143.177.206
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=120.53.130.158
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=81.70.124.99

            # digdig.io
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2606:4700:20::681a:425
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2606:4700:20::ac43:4a3b
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=2606:4700:20::681a:525
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=104.26.4.37
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=172.67.74.59
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=104.26.5.37

            # AcFun
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.231.200
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.231.194
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.231.199
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.231.198
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.231.197
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.231.195
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.231.196
            netsh advfirewall firewall add rule name="MyLimit" dir=out action=block remoteip=223.111.231.193
        }
    }
} -Trigger (    # 每一分钟执行一次
    New-JobTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval '00:01:00' -RepeatIndefinitely
)


# 移除限速任务：
#Unregister-ScheduledJob "MyTrafficLimit"
#netsh advfirewall firewall delete rule name="MyLimit"