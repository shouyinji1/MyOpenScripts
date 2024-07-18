#Requires -RunAsAdministrator

### 网速控制工具
# Windows Home版本缺乏某些必要的功能，此脚本虽然可执行不报错，但不能在该版本上正常生效。
# 即使Windows Home版本使用网传脚本启用本地组策略编辑功能，该脚本也不能正常生效。

# 限速：
Register-ScheduledJob -Name "MyTrafficLimit" -ScriptBlock{
    # 不限速时段：20:00-22:00
    if( ( ((Get-Date -Format "HH:mm").CompareTo("20:00") -eq 1) -and ((Get-Date -Format "HH:mm").CompareTo("22:00") -eq -1) ) ){ # 不限速时段
        Remove-NetQosPolicy -Name "MyTrafficLimit*"
    }else{  # 限速
        # 检验规则是否已经生效过
        Set-NetQosPolicy -Name "MyTrafficLimit_xueqiu" -URIMatchCondition "https://xueqiu.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 1KB # 雪球
        if($? -eq $false){  # 没有生效过，是第一次创建规则
            ## 限速黑名单
            New-NetQosPolicy -Name "MyTrafficLimit_xueqiu" -URIMatchCondition "https://xueqiu.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 1KB # 雪球
            New-NetQosPolicy -Name "MyTrafficLimit_eastmoney" -URIMatchCondition "https://www.eastmoney.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 1KB # 东方财富
            New-NetQosPolicy -Name "MyTrafficLimit_bilibili" -URIMatchCondition "https://www.bilibili.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 1KB # Bilibili
            New-NetQosPolicy -Name "MyTrafficLimit_tieba" -URIMatchCondition "https://tieba.baidu.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 1KB # 百度贴吧
            New-NetQosPolicy -Name "MyTrafficLimit_haokan" -URIMatchCondition "https://haokan.baidu.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 1KB # 百度好看视频
            New-NetQosPolicy -Name "MyTrafficLimit_douban" -URIMatchCondition "https://www.douban.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 1KB # 豆瓣
            New-NetQosPolicy -Name "MyTrafficLimit_www.weibo.com" -URIMatchCondition "https://www.weibo.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 1KB # 微博电脑网页
            New-NetQosPolicy -Name "MyTrafficLimit_m.weibo.com" -URIMatchCondition "https://m.weibo.com" -URIRecursiveMatchCondition $true -ThrottleRateActionBitsPerSecond 1KB # 微博手机网页
        }
    }
} -Trigger (    # 每一分钟执行一次
    New-JobTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval '00:01:00' -RepeatIndefinitely
)

# 查看限速状态
#Get-NetQosPolicy -Name "MyTrafficLimit*"

# 移除限速任务：
#Unregister-ScheduledJob "MyTrafficLimit"
#Remove-NetQosPolicy -Name "MyTrafficLimit*"


# Ref: https://www.cnblogs.com/fong/p/10029348.html