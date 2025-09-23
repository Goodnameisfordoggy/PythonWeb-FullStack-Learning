import API from "./api.js";

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 获取元素
    const editButtons = document.querySelectorAll('.edit-btn');
    const avatarEdit = document.getElementById('change-avatar');
    const avatarInput = document.getElementById('avatar-input');
    const avatarImg = document.getElementById('avatar-img');
    const logoutBtn = document.getElementById('logout-btn');
    const deleteAccountBtn = document.getElementById('delete-account-btn');
    const confirmModal = new bootstrap.Modal(document.getElementById('confirm-modal'));
    const confirmActionBtn = document.getElementById('confirm-action');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const alert = document.getElementById('alert');
    const bindBtns = document.querySelectorAll('.bind-btn');
    const unbindBtns = document.querySelectorAll('.unbind-btn');

    // 编辑按钮点击事件
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');

            // 特殊处理个人简介
            if (targetId === 'bio') {
                const displayElement = document.getElementById('bio-display');
                const inputElement = document.getElementById('bio-input');

                if (this.innerHTML.includes('编辑')) {
                    // 切换到编辑模式
                    displayElement.style.display = 'none';
                    inputElement.style.display = 'block';
                    this.innerHTML = '<i class="fas fa-save"></i> 保存';
                } else {
                    // 保存编辑
                    displayElement.textContent = inputElement.value;
                    displayElement.style.display = 'block';
                    inputElement.style.display = 'none';
                    this.innerHTML = '<i class="fas fa-edit"></i> 编辑';
                    showAlert('个人简介已更新');
                }
                return;
        }

        const targetElement = document.getElementById(targetId);

        if (targetElement.hasAttribute('readonly')) {
            // 切换到编辑模式
            targetElement.removeAttribute('readonly');
            targetElement.focus();

            // 密码特殊处理
            if (targetId === 'password') {
                targetElement.value = '';
            }

            this.innerHTML = '<i class="fas fa-save"></i> 保存';
        } else {
            // 保存编辑
            targetElement.setAttribute('readonly', true);

            // 密码特殊处理
            if (targetId === 'password') {
                targetElement.value = '••••••••';
            }

            this.innerHTML = '<i class="fas fa-edit"></i> 编辑';
            showAlert(`${getLabelText(targetId)}已更新`);
        }
    });
});

    // 头像更换
    avatarEdit.addEventListener('click', function() {
        avatarInput.click();
    });

    avatarInput.addEventListener('change', function(e) {
        if (e.target.files && e.target.files[0]) {
            const reader = new FileReader();

            reader.onload = function(e) {
                avatarImg.src = e.target.result;
                showAlert('头像已更新');
            }

            reader.readAsDataURL(e.target.files[0]);
        }
    });

    // 退出登录
    logoutBtn.addEventListener('click', function () {
        const userId = this.dataset.userid;
        console.log(userId)
        modalTitle.textContent = '确认退出登录';
        modalBody.textContent = '您确定要退出当前登录吗？';
        confirmModal.show();

        confirmActionBtn.onclick = async function () {
            const successData = await API.logoutAccount(userId)
            confirmModal.hide();
            if (successData) {
                showAlert('已成功退出登录');
                location.href = '/login'
            } else {
                showAlert('登出失败，请重试');
            }
        };
    });

    // 注销账号
    deleteAccountBtn.addEventListener('click', function() {
        modalTitle.textContent = '确认注销账号';
        modalBody.textContent = '警告：注销账号后，所有数据将被永久删除，且无法恢复。您确定要继续吗？';
        confirmModal.show();

        confirmActionBtn.onclick = function() {
            confirmModal.hide();
            showAlert('账号已成功注销');
            // 实际应用中这里会跳转到注册页或首页
            setTimeout(() => {
                alert('跳转到首页');
            }, 1000);
        };
    });

    // 社交账号绑定
    bindBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const social = this.getAttribute('data-social');
            const socialName = social === 'qq' ? 'QQ' : social;

            // 模拟绑定过程
            this.classList.remove('bind-btn', 'btn-outline-primary');
            this.classList.add('unbind-btn', 'btn-outline-danger');
            this.textContent = '解绑';
            this.parentElement.querySelector('span').textContent = `${socialName}已绑定`;

            showAlert(`${socialName}账号绑定成功`);
        });
    });

    // 社交账号解绑
    unbindBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const social = this.getAttribute('data-social');
            const socialName = social === 'wechat' ? '微信' : social;

            // 模拟解绑过程
            this.classList.remove('unbind-btn', 'btn-outline-danger');
            this.classList.add('bind-btn', 'btn-outline-primary');
            this.textContent = '绑定';
            this.parentElement.querySelector('span').textContent = `${socialName}未绑定`;

            showAlert(`${socialName}账号解绑成功`);
        });
    });

    // 显示提示消息
    function showAlert(message) {
        alert.textContent = message;
        alert.style.display = 'block';

        setTimeout(() => {
            alert.style.display = 'none';
        }, 3000);
    }

    // 获取标签文本
    function getLabelText(fieldId) {
        const labels = {
            'username': '用户名',
            'password': '密码',
            'phone': '手机号',
            'email': '邮箱'
        };
        return labels[fieldId] || fieldId;
    }
});