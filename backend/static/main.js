document.addEventListener('DOMContentLoaded', () => {
  const uploadBtn = document.getElementById('uploadBtn');
  const imgInput   = document.getElementById('imgInput');
  const resultDiv  = document.getElementById('result');

  uploadBtn.addEventListener('click', async () => {
    if (!imgInput.files.length) {
      alert('이미지를 선택해주세요');
      return;
    }

    // 업로드
    const form = new FormData();
    form.append('file', imgInput.files[0]);

    const resp = await fetch('/infer', {
      method: 'POST',
      body: form
    });
    if (!resp.ok) {
      alert('서버 오류');
      return;
    }

    const data = await resp.json();
    const { labels, output_image } = data;

    // 라벨만 예쁘게 보여주기
    resultDiv.innerHTML = `
      <h2>감지된 객체 (${labels.length}개)</h2>
      <ul class="label-list">
        ${labels.map(name => `<li>${name}</li>`).join('')}
      </ul>
      <img src="/outputs/${output_image}" alt="결과 이미지" class="result-img"/>
    `;
  });
});
