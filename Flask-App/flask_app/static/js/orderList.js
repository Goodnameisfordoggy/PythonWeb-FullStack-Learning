import API from './api.js'

function showOrderDeleteConfirmModal(itemID, orderIdentity) {

    console.log('showOrderDeleteConfirmModal')
    // 获取弹窗元素
    const modal = document.getElementById('baseModal');
    const modalTitle = modal.querySelector('#baseModalLabel'); // 标题元素
    const modalBody = modal.querySelector('.modal-body');         // 内容元素
    const confirmBtn = modal.querySelector('#confirm');       // 确认按钮

    // 创建 bootstrap 弹窗实例，或复用已有弹窗
    const bootstrapModal = bootstrap.Modal.getInstance(modal) || new bootstrap.Modal(modal);

    // 设置弹窗文本
    modalTitle.textContent = '删除订单'; // 标题
    modalBody.textContent = `确定要删除订单${itemID}吗？`; // 内容

    // 绑定确认按钮的点击事件
    confirmBtn.onclick = async function() {
        const successData = await API.deleteOrder(orderIdentity); // 执行删除逻辑
        if (successData) {
            // 关闭弹窗（使用 Bootstrap API）
            bootstrapModal.hide();
            location.reload()
        }
    };

    // 显示弹窗
    bootstrapModal.show();
}


window.showOrderDeleteConfirmModal = showOrderDeleteConfirmModal