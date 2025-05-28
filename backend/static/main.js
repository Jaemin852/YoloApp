document.addEventListener('DOMContentLoaded', () => {
  const uploadBtn   = document.getElementById('uploadBtn');
  const imgInput    = document.getElementById('imgInput');
  const modelSelect = document.getElementById('modelSelect');
  const resultDiv   = document.getElementById('result');

  // 1) 지원 모델 목록 불러와 select 에 넣기
  fetch('/models')
    .then(r => r.json())
    .then(data => {
      data.models.forEach(name => {
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name + (name === data.default ? ' (기본)' : '');
        modelSelect.append(opt);
      });
      modelSelect.value = data.default;
    });

  // 2) 업로드 & 추론
  uploadBtn.addEventListener('click', async () => {
    if (!imgInput.files.length) return alert('이미지를 선택해주세요');

    const form = new FormData();
    form.append('file', imgInput.files[0]);

    // 선택한 모델 쿼리 파라미터로 추가
    const modelName = modelSelect.value;
    const url = `/infer?model=${encodeURIComponent(modelName)}`;

    const resp = await fetch(url, { method: 'POST', body: form });
    if (!resp.ok) {
      const err = await resp.json();
      return alert('서버 오류: ' + (err.error || resp.status));
    }

    const { labels, output_image } = await resp.json();

    // 결과 렌더링
    resultDiv.innerHTML = `
      <h2>감지된 객체 (${labels.length}개)</h2>
      <ul class="label-list">
        ${labels.map(n => `<li>${n}</li>`).join('')}
      </ul>
      <img src="/outputs/${output_image}" class="result-img"/>
    `;
  });
});
