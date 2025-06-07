@echo off
echo 🚀 智能餐厅系统 v1.0.0 - 推送到GitHub
echo ================================================

echo.
echo 🔍 检查Git状态...
git status

echo.
echo 📋 当前分支和标签信息:
git branch -a
git tag

echo.
echo 🌐 远程仓库信息:
git remote -v

echo.
echo 🔄 尝试推送代码到GitHub...
echo 如果遇到网络问题，请检查：
echo 1. 网络连接是否正常
echo 2. 是否需要设置代理
echo 3. GitHub是否可以访问

echo.
echo 📤 推送master分支...
git push -u origin master

if %errorlevel% equ 0 (
    echo ✅ 代码推送成功！
    echo.
    echo 🏷️  推送标签 v1.0.0...
    git push origin v1.0.0
    
    if %errorlevel% equ 0 (
        echo ✅ 标签推送成功！
        echo.
        echo 🎉 智能餐厅系统 v1.0.0 已成功发布到GitHub！
        echo 📍 仓库地址: https://github.com/chenguo6666/SmartRestaurant
        echo 🏷️  版本标签: v1.0.0
    ) else (
        echo ❌ 标签推送失败，请手动执行: git push origin v1.0.0
    )
) else (
    echo ❌ 代码推送失败
    echo.
    echo 🔧 可能的解决方案:
    echo 1. 检查网络连接
    echo 2. 如果在国内，可能需要配置代理：
    echo    git config --global http.proxy http://127.0.0.1:7890
    echo    git config --global https.proxy http://127.0.0.1:7890
    echo 3. 或者使用SSH方式：
    echo    git remote set-url origin git@github.com:chenguo6666/SmartRestaurant.git
    echo 4. 稍后重试: git push -u origin master
)

echo.
echo 📝 完成情况总结:
echo ================================
echo ✅ 本地Git仓库已初始化
echo ✅ 所有文件已提交到本地仓库
echo ✅ v1.0.0标签已创建
echo ✅ 远程仓库地址已配置
echo ⏳ 等待网络推送完成...

echo.
echo 📋 手动推送命令（如果需要）:
echo git push -u origin master
echo git push origin v1.0.0

pause 