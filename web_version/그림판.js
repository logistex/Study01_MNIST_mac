// 2026-08-06 19:14 KST 생성
//
// 캔버스에 마우스나 손가락으로 그리는 부분만 맡는다.
//
// 데스크톱 버전(app.py)은 화면 캔버스와 PIL 이미지에 같은 내용을 두 번
// 그려야 했다. 화면 화소를 직접 읽는 방법이 운영체제마다 달라서였다.
// 브라우저에서는 getImageData 로 캔버스를 그대로 읽을 수 있어 한 번만 그린다.
//
// 포인터 이벤트를 쓰면 마우스와 터치를 같은 코드로 처리할 수 있다.
// 터치로 그릴 때 화면이 따라 스크롤되지 않도록 CSS 에서 touch-action 을 끈다.

export function 그림판만들기(캔버스, { 붓굵기 = 18, 그리기끝남 = () => {} } = {}) {
  const 붓 = 캔버스.getContext("2d", { willReadFrequently: true });
  let 그리는중포인터 = null;
  let 뭔가그렸나 = false;

  function 바탕칠하기() {
    붓.fillStyle = "black";
    붓.fillRect(0, 0, 캔버스.width, 캔버스.height);
  }

  function 좌표구하기(사건) {
    const 상자 = 캔버스.getBoundingClientRect();
    // 화면에 표시된 크기와 캔버스 해상도가 다를 수 있어 비율로 환산한다.
    return {
      가로: (사건.clientX - 상자.left) * (캔버스.width / 상자.width),
      세로: (사건.clientY - 상자.top) * (캔버스.height / 상자.height),
    };
  }

  붓.lineCap = "round";
  붓.lineJoin = "round";
  붓.strokeStyle = "white";
  붓.fillStyle = "white";
  붓.lineWidth = 붓굵기;
  바탕칠하기();

  캔버스.addEventListener("pointerdown", (사건) => {
    if (사건.button !== 0) return;
    // 이미 다른 손가락(포인터)으로 그리는 중이면 무시한다. 그러지 않으면
    // 두 번째 손가락의 pointerdown 이 경로를 리셋해 두 손가락 사이에
    // 선이 그어진다.
    if (그리는중포인터 !== null) return;
    사건.preventDefault();
    캔버스.setPointerCapture(사건.pointerId);
    그리는중포인터 = 사건.pointerId;
    뭔가그렸나 = true;

    const { 가로, 세로 } = 좌표구하기(사건);
    // 점 하나만 찍었을 때도 보이도록 원을 그린다.
    붓.fillStyle = "white";
    붓.beginPath();
    붓.arc(가로, 세로, 붓굵기 / 2, 0, Math.PI * 2);
    붓.fill();

    붓.beginPath();
    붓.moveTo(가로, 세로);
  });

  캔버스.addEventListener("pointermove", (사건) => {
    if (사건.pointerId !== 그리는중포인터) return;
    사건.preventDefault();
    const { 가로, 세로 } = 좌표구하기(사건);
    붓.lineTo(가로, 세로);
    붓.stroke();
    붓.beginPath();
    붓.moveTo(가로, 세로);
  });

  function 그리기멈춤(사건) {
    if (사건.pointerId !== 그리는중포인터) return;
    사건.preventDefault();
    그리는중포인터 = null;
    그리기끝남();
  }

  캔버스.addEventListener("pointerup", 그리기멈춤);
  캔버스.addEventListener("pointercancel", 그리기멈춤);
  캔버스.addEventListener("pointerleave", 그리기멈춤);

  return {
    지우기() {
      바탕칠하기();
      뭔가그렸나 = false;
    },
    밝기읽기() {
      return 붓.getImageData(0, 0, 캔버스.width, 캔버스.height);
    },
    비었나() {
      return !뭔가그렸나;
    },
  };
}
