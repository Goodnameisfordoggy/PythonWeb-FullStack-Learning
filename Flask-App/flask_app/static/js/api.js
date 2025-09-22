function createOrder(formData) {
    // 发送请求
    return fetch(`/order/create`, {
        method: 'POST',
        body: formData, // 将表单数据作为请求
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('网络响应不正常');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            return data;
        } else {
            // 请求成功但业务失败的情况
            throw new Error(data.message || '创建订单失败');
        }
    })
    .catch(error => {
        console.error('创建订单时出错:', error);
        throw error;
    });
}

function deleteOrder(orderIdentity) {
    // 使用 DELETE 方法
    return fetch(`/order/delete/${orderIdentity}`, {method: 'DELETE' })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return data;
        }
    })
    .catch(error => {
        console.error('请求失败：', error)
    })
}

function deleteUser(userId) {
    // 使用 DELETE 方法
    return fetch(`/user/delete/${userId}`, {method: 'DELETE'})
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return data;
        }
    })
    .catch(error => {
        console.error('请求失败：', error)
    })
}

function restoreUser(userId) {
    return fetch(`/user/restore/${userId}`, {method: 'POST'})
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return data;
        }
    })
    .catch(error => {
        console.error('请求失败：', error)
    })
}

function logoutAccount(userId) {
    return fetch(`/user/logout/${userId}`, {
        method: 'POST',
        body: JSON.stringify({ user_identity: userId }) 
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return data;
        }
    })
    .catch(error => {
        console.error('请求失败：', error)
    })
}

const API = {
    createOrder,
    deleteOrder,
    deleteUser,
    restoreUser,
    logoutAccount,
};
export default API;