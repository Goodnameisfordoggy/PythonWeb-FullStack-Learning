import {login} from "./api.js";

document.addEventListener("DOMContentLoaded", function() {
    const loginBtn = document.getElementById("loginBtn");
    const registerBtn = document.getElementById("registerBtn");

    loginBtn.addEventListener("click", handleLogin);
    registerBtn.href = "/register/";
})

async function handleLogin() {
    const loginData = {
      'role': document.getElementById('roleSelect').value.trim(),
      'mobile': document.getElementById('mobileInput').value.trim(),
      'pwd': document.getElementById('passwordInput').value.trim(),
    };

    if (!loginData.role) { alert('请选择用户角色'); return; }
    if (!loginData.mobile) { alert('请输入手机号'); return; }
    if (!loginData.pwd) { alert('请输入密码'); return; }
    console.log(loginData);

    try {
        // 发送POST请求到登录API
        const result = await login(loginData)
        // 处理响应
        if (result.success) {
            // 登录成功：
            // 存储用户信息到本地
            localStorage.setItem('userInfo', JSON.stringify(result.data.user_info));
            location.href = '/order/list/';
        } else {
            // document.getElementById('errorMsg').textContent = result.msg;
            alert(result.msg);
        }
    } catch (error) {
        console.error('网络错误详情：', error);
    }
}