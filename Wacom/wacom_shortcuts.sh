#!/usr/bin/bash

# Linux平台Wacom数位板快捷键触发脚本

# Wacom CTL 472
device="Wacom One by Wacom S Pen stylus"
defaultArea=(0 0 15200 9500)

# 获取显示器分辨率和基轴坐标
# 输入：显示器编号0,1,...
# 输出: 显示器size_x size_y baseAxisOfMonitor_x baseAxisOfMonitor_y
getMonitorInfo(){
	local monitorsInfo=$(xrandr --listmonitors)
	echo "$monitorsInfo" | while read line;do
		monitor=($line)
		local monitorID=${monitor%:*}
		#notify-send ${monitor%:*}
		if [ $monitorID -eq $1 ];then
			# 显示器分辨率
			size_x=${monitor[2]%%/*}
			local temp=${monitor[2]#*x}
			size_y=${temp%/*}

			# 显示器起始坐标
			baseAxisOfMonitor=(`echo ${monitor[2]#*+} | tr '+' ' '`)
			baseAxisOfMonitor_x=${baseAxisOfMonitor[0]}
			baseAxisOfMonitor_y=${baseAxisOfMonitor[1]}

			# 返回显示器参数值
			temp=($size_x $size_y $baseAxisOfMonitor_x $baseAxisOfMonitor_y)
			echo ${temp[@]}
			return 0	# 读取显示器参数成功
		fi
	done
	return 1	# 读取显示器参数失败
}

# 设置数位板感应区域
# 输入：屏幕大小size_x size_y
# 输出：感应区域area_x area_y
getDeviceArea(){
	size_x=$1
	size_y=$2
	defaultArea_x=${defaultArea[2]}
	defaultArea_y=${defaultArea[3]}
	#notify-send $defaultArea_x
	newArea_y=$((defaultArea_x * size_y / size_x))
	if [  $newArea_y -le $defaultArea_y ];then 	# 宽屏
		#notify-send $newArea_y
		temp=($defaultArea_x $newArea_y)
		echo ${temp[@]}
		return 0
	else 	# 窄屏
		newArea_x=$((size_x * defaultArea_y / size_y))
		#notify-send $newArea_x
		temp=($newArea_x $defaultArea_y)
		echo ${temp[@]}
		return 0
	fi
	return 1
}

# 参数：编号1,2,3,...
setDevice(){
	# 获取显示器ID
	monitorID=`cat $(dirname $(readlink -f "$0"))/Wacom-HEAD.tmp`
	if [ $? != 0 ];then monitorID=0;fi
	#notify-send monitorID:$monitorID

	# 获取显示器参数信息
	monitorInfo=($(getMonitorInfo $monitorID))
	size_x=${monitorInfo[0]}
	size_y=${monitorInfo[1]}
	baseAxisOfMonitor_x=${monitorInfo[2]}
	baseAxisOfMonitor_y=${monitorInfo[3]}

	if [ $1 -eq 1 ];then 	# 显示器0, 全屏映射
		monitorID=0
		monitorInfo=($(getMonitorInfo $monitorID))	# 获取显示器的分辨率
		size_x=${monitorInfo[0]}
		size_y=${monitorInfo[1]}
		deviceArea=($(getDeviceArea $size_x $size_y))	# 根据显示器大小计算数位板感应区域
		area_x=${deviceArea[0]}
		area_y=${deviceArea[1]}
		#notify-send $size_x $size_y
		#notify-send $area_x $area_y

		xsetwacom set "$device" MapToOutput HEAD-${monitorID} \
		&& xsetwacom set "$device" Rotate none \
		&& xsetwacom set "$device" Area 0 0 $area_x $area_y \
		&& notify-send "Ctrl+Alt+1: HEAD-${monitorID}屏幕，数位板不旋转, 全屏映射" \
		&& echo $monitorID > $(dirname $(readlink -f "$0"))/Wacom-HEAD.tmp 	# 写入显示器选择文件
	elif [ "$1" == "m1" ];then 	# 显示器1, 全屏映射
		monitorID=1
		monitorInfo=($(getMonitorInfo $monitorID))	# 获取显示器的分辨率
		size_x=${monitorInfo[0]}
		size_y=${monitorInfo[1]}
		deviceArea=($(getDeviceArea $size_x $size_y))	# 根据显示器大小计算数位板感应区域
		area_x=${deviceArea[0]}
		area_y=${deviceArea[1]}

		xsetwacom set "$device" MapToOutput HEAD-${monitorID} \
		&& xsetwacom set "$device" Rotate none \
		&& xsetwacom set "$device" Area 0 0 $area_x $area_y \
		&& notify-send "Ctrl+Shift+1: HEAD-${monitorID}屏幕，数位板不旋转, 全屏映射" \
		&& echo $monitorID > $(dirname $(readlink -f "$0"))/Wacom-HEAD.tmp 	# 写入显示器选择文件
	elif [ $1 -eq 2 ];then 	# 右半屏映射
		# 计算显示器映射区域
		size_x=$((size_x / 2))
		basePoint_x=$((size_x+baseAxisOfMonitor_x))

		# 计算数位板感应区
		deviceArea=($(getDeviceArea $size_y $size_x))
		area_x=${deviceArea[0]}
		area_y=${deviceArea[1]}
		#notify-send $area_x $area_y

		xsetwacom set "$device" Rotate ccw && \
		xsetwacom set "$device" MapToOutput ${size_x}x${size_y}+${basePoint_x}+${baseAxisOfMonitor_y} && \
		xsetwacom set "$device" Area 0 0 $area_x $area_y && \
		notify-send "Ctrl+Alt+2: 数位板顺时针旋转, 右半屏映射"
	elif [ $1 -eq 3 ];then 	# 左半屏映射
		# 计算映射区域
		size_x=$((size_x / 2))
		deviceArea=($(getDeviceArea $size_y $size_x))
		area_x=${deviceArea[0]}
		area_y=${deviceArea[1]}

		xsetwacom set "$device" Rotate ccw && \
		xsetwacom set "$device" MapToOutput ${size_x}x${size_y}+${baseAxisOfMonitor_x}+${baseAxisOfMonitor_y} && \
		xsetwacom set "$device" Area 0 0 $area_x $area_y && \
		notify-send "Ctrl+Alt+3: 数位板顺时针旋转, 左半屏映射"
	elif [ $1 -eq 4 ];then
		newSize_x=$((size_x/2))
		newSize_y=$((newSize_x * defaultArea[3] / defaultArea[2]))
		basePoint_x=$((newSize_x/2 + baseAxisOfMonitor_x))
		basePoint_y=$(((size_y-newSize_y)/2 + baseAxisOfMonitor_y))
		
		xsetwacom set "$device" Rotate none \
		&& xsetwacom set "$device" MapToOutput ${newSize_x}x${newSize_y}+${basePoint_x}+${basePoint_y} \
		&& xsetwacom set "$device" Area 0 0 ${defaultArea[2]} ${defaultArea[3]} \
		&& notify-send "Ctrl+Alt+4: 数位板不旋转, 居中1/2宽度, Area全区域"
	elif [ $1 -eq 5 ];then
		newSize_x=$((size_x/2))
		newSize_y=$((newSize_x * defaultArea[3] / defaultArea[2]))
		basePoint_x=$((newSize_x + baseAxisOfMonitor_x))
		basePoint_y=$(((size_y-newSize_y)/2 + baseAxisOfMonitor_y))

		xsetwacom set "$device" Rotate none \
		&& xsetwacom set "$device" MapToOutput ${newSize_x}x${newSize_y}+${basePoint_x}+${basePoint_y} \
		&& xsetwacom set "$device" Area 0 0 ${defaultArea[2]} ${defaultArea[3]} \
		&& notify-send "Ctrl+Alt+5: 数位板不旋转, 居右1/2宽度, Area全区域"
	elif [ $1 -eq 6 ];then
		newSize_x=$((size_x/2))
		newSize_y=$((newSize_x * defaultArea[3] / defaultArea[2]))
		basePoint_y=$(((size_y-newSize_y)/2 + baseAxisOfMonitor_y))

		xsetwacom set "$device" Rotate none \
		&& xsetwacom set "$device" MapToOutput ${newSize_x}x${newSize_y}+${baseAxisOfMonitor_x}+${basePoint_y} \
		&& xsetwacom set "$device" Area 0 0 ${defaultArea[2]} ${defaultArea[3]} \
		&& notify-send "Ctrl+Alt+6: 数位板不旋转, 居左1/2宽度, Area全区域"
	elif [ $1 -eq 7 ];then
		newSize_x=$((size_x/2 + size_x * 2 / 100))	# 1/2宽度放大2%
		newSize_y=$((newSize_x * defaultArea[3] / defaultArea[2]))

		xsetwacom set "$device" Rotate none \
		&& xsetwacom set "$device" MapToOutput ${newSize_x}x${newSize_y}+${baseAxisOfMonitor_x}+${baseAxisOfMonitor_y} \
		&& xsetwacom set "$device" Area 0 0 ${defaultArea[2]} ${defaultArea[3]} \
		&& notify-send "Ctrl+Alt+7: 数位板不旋转, 左上略大于1/2宽度, Area全区域"
	elif [ $1 -eq 8 ];then
		newSize_x=$((size_x/2 + size_x * 2 / 100))
		newSize_y=$((newSize_x * defaultArea[3] / defaultArea[2]))
		basePoint_y=$((size_y-newSize_y + baseAxisOfMonitor_y))

		xsetwacom set "$device" Rotate none \
		&& xsetwacom set "$device" MapToOutput ${newSize_x}x${newSize_y}+${baseAxisOfMonitor_x}+${basePoint_y} \
		&& xsetwacom set "$device" Area 0 0 ${defaultArea[2]} ${defaultArea[3]} \
		&& notify-send "Ctrl+Alt+8: 数位板不旋转, 左下略大于1/2宽度, Area全区域"
	elif [ $1 -eq 9 ];then
		newSize_x=$((size_x/2 + size_x * 2 / 100))
		newSize_y=$((newSize_x * defaultArea[3] / defaultArea[2]))
		basePoint_x=$((size_x-newSize_x + baseAxisOfMonitor_x))

		xsetwacom set "$device" Rotate none \
		&& xsetwacom set "$device" MapToOutput ${newSize_x}x${newSize_y}+${basePoint_x}+${baseAxisOfMonitor_y} \
		&& xsetwacom set "$device" Area 0 0 ${defaultArea[2]} ${defaultArea[3]} \
		&& notify-send "Ctrl+Alt+9: 数位板不旋转, 右上略大于1/2宽度, Area全区域"
	elif [ $1 -eq 0 ];then
		newSize_x=$((size_x/2 + size_x * 2 / 100))
		newSize_y=$((newSize_x * defaultArea[3] / defaultArea[2]))
		basePoint_x=$((size_x-newSize_x + baseAxisOfMonitor_x))
		basePoint_y=$((size_y-newSize_y + baseAxisOfMonitor_y))

		xsetwacom set "$device" Rotate none \
		&& xsetwacom set "$device" MapToOutput ${newSize_x}x${newSize_y}+${basePoint_x}+${basePoint_y} \
		&& xsetwacom set "$device" Area 0 0 ${defaultArea[2]} ${defaultArea[3]} \
		&& notify-send "Ctrl+Alt+0: 数位板不旋转, 右下略大于1/2宽度, Area全区域"
	fi
}

setDevice $1
