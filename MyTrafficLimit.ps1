#Requires -RunAsAdministrator

### 网速控制工具
# Windows Home版本缺乏某些必要的功能，此脚本虽然可执行不报错，但不能在该版本上正常生效。
# 即使Windows Home版本使用网传脚本启用本地组策略编辑功能，该脚本也不能正常生效。

# 限速：
Register-ScheduledJob -Name "MyTrafficLimit" -ScriptBlock{
    # 不限速时间段：20:00-22:00, 06:00-09:00, 12:00-13:00
    if( ((get-random -inputobject (0..1)) -eq 0) `
        -or ( ((Get-Date -Format "HH:mm").CompareTo("20:00") -eq 1) -and ((Get-Date -Format "HH:mm").CompareTo("22:00") -eq -1) ) `
        -or ( ((Get-Date -Format "HH:mm").CompareTo("06:00") -eq 1) -and ((Get-Date -Format "HH:mm").CompareTo("09:00") -eq -1) ) `
        -or ( ((Get-Date -Format "HH:mm").CompareTo("12:00") -eq 1) -and ((Get-Date -Format "HH:mm").CompareTo("13:00") -eq -1) ) `
    ){ # 1/2概率不限速
        Set-NetQosPolicy -Name "MyTrafficLimit" -ThrottleRateActionBitsPerSecond 20GB
    }else{  # 限速
        Set-NetQosPolicy -Name "MyTrafficLimit" -ThrottleRateActionBitsPerSecond 15KB
        if($? -eq $false){
            New-NetQosPolicy -Name "MyTrafficLimit" -ThrottleRateActionBitsPerSecond 15KB

            ## 不限速白名单
            New-NetQosPolicy -Name "MyTrafficLimit_org" -URIMatchCondition "https://*.org" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # .org类网站
            New-NetQosPolicy -Name "MyTrafficLimit_edu.cn" -URIMatchCondition "https://*.edu.cn" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 各教育类网站
            New-NetQosPolicy -Name "MyTrafficLimit_gov.cn" -URIMatchCondition "https://*.gov.cn" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 各政府类网站
            New-NetQosPolicy -Name "MyTrafficLimit_cnki.net" -URIMatchCondition "https://*.cnki.net" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 中国知网
            New-NetQosPolicy -Name "MyTrafficLimit_eudic.net" -URIMatchCondition "https://*.eudic.net" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 欧陆词典
            New-NetQosPolicy -Name "MyTrafficLimit_fenbi.com" -URIMatchCondition "https://*.fenbi.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 粉笔网
            New-NetQosPolicy -Name "MyTrafficLimit_github.com" -URIMatchCondition "https://*.github.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # GitHub
            New-NetQosPolicy -Name "MyTrafficLimit_gitlab.com" -URIMatchCondition "https://*.gitlab.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # GitLab
            New-NetQosPolicy -Name "MyTrafficLimit_google.cn" -URIMatchCondition "https://*.google.cn" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # google.cn
            New-NetQosPolicy -Name "MyTrafficLimit_google.com" -URIMatchCondition "https://*.google.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # google.com
            New-NetQosPolicy -Name "MyTrafficLimit_jianguoyun.com" -URIMatchCondition "https://*.jianguoyun.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 坚果云
            New-NetQosPolicy -Name "MyTrafficLimit_live.com" -URIMatchCondition "https://*.live.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 微软账户
            New-NetQosPolicy -Name "MyTrafficLimit_runoob.com" -URIMatchCondition "https://*.runoob.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 菜鸟教程
            New-NetQosPolicy -Name "MyTrafficLimit_suishouxie.com" -URIMatchCondition "https://*.suishouxie.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 随手写
            New-NetQosPolicy -Name "MyTrafficLimit_unipus.cn" -URIMatchCondition "https://*.unipus.cn" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # U校园
            New-NetQosPolicy -Name "MyTrafficLimit_chsi.com.cn" -URIMatchCondition "https://*.chsi.com.cn" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 学信网

            New-NetQosPolicy -Name "MyTrafficLimit_dasai.lanqiao.cn" -URIMatchCondition "https://dasai.lanqiao.cn" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 蓝桥杯大赛
            New-NetQosPolicy -Name "MyTrafficLimit_fanyi.youdao.com" -URIMatchCondition "https://fanyi.youdao.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 有道翻译
            New-NetQosPolicy -Name "MyTrafficLimit_learn.microsoft.com" -URIMatchCondition "https://learn.microsoft.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # Microsoft Learn
            New-NetQosPolicy -Name "MyTrafficLimit_wenku.baidu.com" -URIMatchCondition "https://wenku.baidu.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 5GB # 百度文库
        }
    }
} -Trigger (    # 每一分钟执行一次
    New-JobTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval '00:01:00' -RepeatIndefinitely
)

# 查看限速状态
#Get-NetQosPolicy -Name "MyTrafficLimit"

# 移除限速任务：
#Unregister-ScheduledJob "MyTrafficLimit"
#Remove-NetQosPolicy -Name "MyTrafficLimit*"


# Ref: https://www.cnblogs.com/fong/p/10029348.html