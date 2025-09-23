import API from './api.js'
import { deleteUser } from "./api.js";

function showUserDeleteConfirmModal(userId, userName) {
    console.log('showUserDeleteConfirmModal')
    // 获取弹窗元素
    const modal = document.getElementById('baseModal');
    const modalTitle = modal.querySelector('#baseModalLabel'); // 标题元素
    const modalBody = modal.querySelector('.modal-body');         // 内容元素
    const confirmBtn = modal.querySelector('#confirm');       // 确认按钮

    // 创建 bootstrap 弹窗实例，或复用已有弹窗
    const bootstrapModal = bootstrap.Modal.getInstance(modal) || new bootstrap.Modal(modal);
    
    // 设置弹窗文本
    modalTitle.textContent = '确认删除'; // 标题
    modalBody.textContent = `确定要删除用户 "${userName}" 吗？`; // 内容

    // 绑定确认按钮的点击事件
    confirmBtn.onclick = async function() {
        const successData = await deleteUser(userId); // 执行删除逻辑
        if (successData) {
            // 关闭弹窗（使用 Bootstrap API）
            bootstrapModal.hide();
            location.reload()
        }
    };

    // 显示弹窗
    bootstrapModal.show();
}

function showUserRestoreConfirmModal(userId, userName) {
    console.log('showUserRestoreConfirmModal')
    // 获取弹窗元素
    const modal = document.getElementById('baseModal');
    const modalTitle = modal.querySelector('#baseModalLabel');
    const modalBody = modal.querySelector('.modal-body');
    const confirmBtn = modal.querySelector('#confirm');

    // 创建 bootstrap 弹窗实例，或复用已有弹窗
    const bootstrapModal = bootstrap.Modal.getInstance(modal) || new bootstrap.Modal(modal);
    
    // 设置弹窗文本
    modalTitle.textContent = '恢复用户';
    modalBody.textContent = `确定要恢复用户 "${userName}" 吗？`;

    // 绑定确认按钮的点击事件
    confirmBtn.onclick = async function() {
        const successData = await API.restoreUser(userId);
        if (successData) {
            // 关闭弹窗（使用 Bootstrap API）
            bootstrapModal.hide();
            location.reload()
        }
    };

    // 显示弹窗
    bootstrapModal.show();
}

window.showUserDeleteConfirmModal = showUserDeleteConfirmModal;
window.showUserRestoreConfirmModal = showUserRestoreConfirmModal