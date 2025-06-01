document.addEventListener('DOMContentLoaded', () => {
  const uploadBtn    = document.getElementById('uploadBtn');
  const imgInput     = document.getElementById('imgInput');
  const modelSelect  = document.getElementById('modelSelect');
  const resultDiv    = document.getElementById('result');
  const historyBtn   = document.getElementById('historyBtn');
  const historySec   = document.getElementById('history-section');
  const historyCont  = document.getElementById('history-container');

  // 1) 지원 모델 목록 불러와 <select>에 넣기
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

  // 2) 업로드 & 탐지 버튼 클릭
  uploadBtn.addEventListener('click', async () => {
    if (!imgInput.files.length) {
      alert('이미지를 선택해주세요');
      return;
    }

    const form = new FormData();
    form.append('file', imgInput.files[0]);

    const modelName = modelSelect.value;
    const url = `/infer?model=${encodeURIComponent(modelName)}`;

    const resp = await fetch(url, { method: 'POST', body: form });
    if (!resp.ok) {
      const err = await resp.json();
      return alert('서버 오류: ' + (err.error || resp.status));
    }

    const { labels, output_image } = await resp.json();

    resultDiv.innerHTML = `
      <h2>감지된 객체 (${labels.length}개)</h2>
      <ul class="label-list">
        ${labels.map(n => `<li>${n}</li>`).join('')}
      </ul>
      <img src="/outputs/${output_image}" class="result-img"/>
    `;

    // 결과 보여줄 때 이력 섹션은 숨겨두기
    historySec.classList.add('hidden');
  });

  // 3) 이력 보기 버튼 클릭
  historyBtn.addEventListener('click', () => {
    // 이미 보여지고 있으면 숨기기
    if (!historySec.classList.contains('hidden')) {
      historySec.classList.add('hidden');
      return;
    }
    loadHistory();
  });

  // 4) /history 호출하여 테이블 그리기
  async function loadHistory() {
    try {
      const resp = await fetch('/history');
      if (!resp.ok) {
        alert('이력 로딩 중 오류');
        return;
      }
      const data = await resp.json();
      renderHistoryTable(data.history);
      historySec.classList.remove('hidden');
      // 스크롤해서 이력 영역으로 이동
      historySec.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
      console.error(err);
      alert('이력 로딩 중 네트워크 오류');
    }
  }

  // 5) 테이블 렌더링 함수
  function renderHistoryTable(records) {
    if (!records.length) {
      historyCont.innerHTML = '<p class="no-history">저장된 이력이 없습니다.</p>';
      return;
    }

    let html = `
      <table class="history-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>시간 (UTC)</th>
            <th>모델</th>
            <th>파일명</th>
            <th>라벨</th>
          </tr>
        </thead>
        <tbody>
    `;
    records.forEach(rec => {
      html += `
        <tr>
          <td>${rec.id}</td>
          <td>${new Date(rec.timestamp).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })}</td>
          <td>${rec.model}</td>
          <td>${rec.filename}</td>
          <td>
            <ul class="history-label-list">
              ${rec.labels.map(l => `<li>${l}</li>`).join('')}
            </ul>
          </td>
        </tr>
      `;
    });
    html += `
        </tbody>
      </table>
    `;
    historyCont.innerHTML = html;
  }
});
