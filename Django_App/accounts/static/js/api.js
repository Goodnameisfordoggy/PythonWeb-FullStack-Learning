// 从cookie中获取CSRF令牌（Django默认会设置csrftoken cookie）
function getCookie(name) {
    let cookieValue = null;
    // 检查浏览器是否存在Cookie
    if (document.cookie && document.cookie !== '') {
        // 按";"分割，得到单个Cookie的数组（浏览器Cookie格式："key1=value1; key2=value2"）
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // 检查当前Cookie的键是否与目标名称完全匹配
            // 逻辑：Cookie格式为"name=value"，截取前"name.length + 1"个字符（包含"="），判断是否等于"name="
            // 避免部分匹配（例如"csrftoken_test"误匹配"csrftoken"）
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                // 若匹配成功，截取"name="之后的部分作为Cookie值，并解码URI（防止值中包含特殊字符）
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


export async function createOrder(formData) {
    try {
        // 发送请求
        const response = await fetch(`/api/accounts/order/create/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            body: formData, // 将表单数据作为请求
        })
        // 解析后端返回的 JSON 响应体
        const data = await response.json();
        // 处理解析后的业务数据
        if (data.success) {
            return data;
        } else {
            throw new Error(data.error || '创建订单失败');  // 业务失败：抛出后端返回的 error 信息
        }
    } catch (error) {
        // 捕获所有错误：网络错误（如断网）、业务错误（如创建失败）
        console.error('Qaq出错了!', error);
        throw error;
    }
}


export async function deleteOrder(orderIdentity) {
    try {
        const response = await fetch(`/api/accounts/order/delete/${orderIdentity}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken,
            },
        })
        // 解析后端返回的 JSON 响应体
        const data = await response.json();
        // 处理解析后的业务数据
        if (data.success) {
            return data;
        } else {
            throw new Error(data.error || '订单删除失败');
        }
    } catch (error) {
        console.error('Qaq出错了!', error);
        throw error;
    }
}


export async function deleteUser(userId) {
    try {
        const response = await fetch(`/api/accounts/user/delete/${userId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken,
            },
        })
        // 解析后端返回的 JSON 响应体
        const data = await response.json();
        // 处理解析后的业务数据
        if (data.success) {
            return data;
        } else {
            throw new Error(data.error || '用户删除失败');
        }
    } catch (error) {
        console.error('Qaq出错了!', error);
        throw error;
    }
}


export async function restoreUser(userId) {
    try {
        const response = await fetch(`/api/accounts/user/restore/${userId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
        })
        // 解析后端返回的 JSON 响应体
        const data = await response.json();
        // 处理解析后的业务数据
        if (data.success) {
            return data;
        } else {
            throw new Error(data.error || '用户恢复失败');
        }
    } catch (error) {
        console.error('Qaq出错了!', error);
        throw error;
    }
}

export async function login(loginData) {
    try {
        const response = await fetch(`/api/accounts/login/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData),
          // credentials: 'include' // 携带 cookie（用于 Django Session 认证，跨域/同域均建议保留）
        })
        // 解析后端返回的 JSON 响应体
        const data = await response.json();
        // 处理解析后的业务数据
        if (data.success) {
            return data;
        } else {
            throw new Error(data.error || '登录失败');
        }
    } catch (error) {
        console.error('Qaq出错了!', error);
        throw error;
    }
}

export async function logoutAccount(userId) {
    try {
        const response = await fetch(`/api/accounts/user/logout/${userId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
        })
        // 解析后端返回的 JSON 响应体
        const data = await response.json();
        // 处理解析后的业务数据
        if (data.success) {
            return data;
        } else {
            throw new Error(data.error || '退出登录失败');
        }
    } catch (error) {
        console.error('Qaq出错了!', error);
        throw error;
    }
}


const API = {
    createOrder,
    deleteOrder,
    deleteUser,
    restoreUser,
    login,
    logoutAccount,
};
export default API;