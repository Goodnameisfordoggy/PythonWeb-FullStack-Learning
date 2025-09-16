import API from './api.js'

async function handleOrderCreateBtnOnclick(formID) {
    console.log("handleOrderCreateBtnOnclick")
    const form = document.querySelector(formID);
    if (!form) {
        alert('未找到表单');
        return;
    }
    const formData = new FormData(form);

    try {
        // 等待 createOrder 完成，接收成功返回的值（即上面 return 的 data）
        const successData = await API.createOrder(formData);
        if (successData) {
            clearForm()
            showOrderCreateSuccessModal()
        }
    } catch (error) {
        // 统一处理所有错误（网络错误 + 业务错误）
        alert(error.message || '创建订单失败，请稍后重试');
    }
}

function showOrderCreateSuccessModal() {
    console.log('showOrderCreateSuccessModal')
    // 获取弹窗元素
    const modal = document.getElementById('baseModal');
    const modalTitle = modal.querySelector('#baseModalLabel'); // 标题元素
    const modalBody = modal.querySelector('.modal-body');         // 内容元素
    const confirmBtn = modal.querySelector('#confirm');       // 确认按钮

    // 创建 bootstrap 弹窗实例，或复用已有弹窗
    const bootstrapModal = bootstrap.Modal.getInstance(modal) || new bootstrap.Modal(modal);
    
    // 设置弹窗文本
    modalTitle.textContent = '成功';
    modalBody.textContent = `您的订单创建成功！`;
    confirmBtn.textContent = '返回订单列表'

    // 绑定确认按钮的点击事件
    confirmBtn.onclick = function() {
        bootstrapModal.hide();
        location.href = '/order/list'
    };

    // 显示弹窗
    bootstrapModal.show();
}

// 清空表单内容的函数
function clearForm() {
    // 获取表单元素
    const form = document.querySelector('#form1');
    if (!form) return; // 表单不存在则退出
    
    // 1. 使用原生reset()方法重置表单（会恢复到初始状态）
    form.reset();
    
    // 2. 单独处理滑块显示值（保持与滑块实际值同步）
    const rangeInput = document.getElementById('count-range');
    const valueDisplay = document.getElementById('count-value');
    if (rangeInput && valueDisplay) {
        // 重置滑块到最小值（或你希望的默认值）
        rangeInput.value = rangeInput.min || 1;
        // 同步更新显示文本
        valueDisplay.textContent = rangeInput.value;
    }
}
    

// 获取滑块和显示元素
const rangeInput = document.getElementById('count-range');
const valueDisplay = document.getElementById('count-value');

// 定义更新显示的函数
function updateDisplay() {
    // 将滑块当前值更新到显示区域
    valueDisplay.textContent = rangeInput.value;
}

// 初始化显示（页面加载时）
updateDisplay();

// 监听滑块变化事件，实时更新显示
rangeInput.addEventListener('input', updateDisplay);


window.showOrderCreateSuccessModal = showOrderCreateSuccessModal
window.handleOrderCreateBtnOnclick = handleOrderCreateBtnOnclick