import "./style.css";
import { getHealth } from "./api";

const app = document.querySelector("#app");

app.innerHTML = `
  <main class="card">
    <h1 class="title">AviAI 前端</h1>
    <p class="desc">最小可运行页面，用于联调后端 FastAPI。</p>
    <button id="check-btn" class="btn">检查后端状态</button>
    <pre id="output" class="output">点击按钮后显示接口返回结果...</pre>
  </main>
`;

const button = document.querySelector("#check-btn");
const output = document.querySelector("#output");

button.addEventListener("click", async () => {
  button.disabled = true;
  output.textContent = "请求中...";
  try {
    const data = await getHealth();
    output.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    output.textContent = `请求失败: ${error.message}`;
  } finally {
    button.disabled = false;
  }
});
