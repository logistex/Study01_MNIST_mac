// 2026-08-06 19:14 KST 생성
//
// 그림판, 전처리, 모델을 엮어 화면에 결과를 표시한다.
// 기능은 데스크톱 버전(app.py)과 같다. 손을 떼면 바로 인식한다.

import { 모델불러오기, 예측하기 } from "./모델.js";
import { mnist형식으로변환, 밝기만뽑기, 정규화 } from "./전처리.js";
import { 그림판만들기 } from "./그림판.js";

const 붓굵기 = 18;        // 280px 캔버스를 28px 로 줄였을 때 MNIST 획 굵기와 비슷해지는 값
const 후보개수 = 3;

const 캔버스 = document.getElementById("그림판");
const 결과숫자칸 = document.getElementById("결과숫자");
const 확신도칸 = document.getElementById("확신도");
const 후보칸 = document.getElementById("후보목록");
const 지우기단추 = document.getElementById("지우기");
const 인식단추 = document.getElementById("인식하기");

let 모델 = null;

const 후보줄들 = [];
for (let 번호 = 0; 번호 < 후보개수; 번호++) {
  const 줄 = document.createElement("div");
  줄.className = "후보";
  줄.innerHTML = '<span class="후보숫자">-</span>'
               + '<span class="막대"><span class="막대채움"></span></span>'
               + '<span class="후보비율"></span>';
  후보칸.appendChild(줄);
  후보줄들.push({
    숫자: 줄.querySelector(".후보숫자"),
    채움: 줄.querySelector(".막대채움"),
    비율: 줄.querySelector(".후보비율"),
  });
}

function 결과비우기(안내) {
  결과숫자칸.textContent = "?";
  확신도칸.textContent = 안내;
  for (const 줄 of 후보줄들) {
    줄.숫자.textContent = "-";
    줄.채움.style.width = "0%";
    줄.비율.textContent = "";
  }
}

function 인식하기() {
  if (모델 === null) return;

  if (그림판.비었나()) {
    확신도칸.textContent = "아직 그린 내용이 없습니다.";
    return;
  }

  const 밝기 = 밝기만뽑기(그림판.밝기읽기());
  const 스물여덟 = mnist형식으로변환(밝기, 캔버스.width, 캔버스.height);
  if (스물여덟 === null) {
    확신도칸.textContent = "아직 그린 내용이 없습니다.";
    return;
  }

  const 확률 = 예측하기(정규화(스물여덟, 모델.평균, 모델.표준편차), 모델);

  const 순위 = Array.from(확률, (값, 숫자) => ({ 숫자, 값 }))
    .sort((앞, 뒤) => 뒤.값 - 앞.값)
    .slice(0, 후보개수);

  결과숫자칸.textContent = String(순위[0].숫자);
  확신도칸.textContent = `확신도 ${(순위[0].값 * 100).toFixed(1)}%`;

  순위.forEach((하나, 번호) => {
    후보줄들[번호].숫자.textContent = String(하나.숫자);
    후보줄들[번호].채움.style.width = `${Math.max(1, 하나.값 * 100)}%`;
    후보줄들[번호].비율.textContent = `${(하나.값 * 100).toFixed(1)}%`;
  });
}

const 그림판 = 그림판만들기(캔버스, { 붓굵기, 그리기끝남: 인식하기 });

지우기단추.addEventListener("click", () => {
  그림판.지우기();
  결과비우기("그림을 그리면 자동으로 인식합니다.");
});
인식단추.addEventListener("click", 인식하기);

결과비우기("모델을 불러오는 중입니다...");
지우기단추.disabled = true;
인식단추.disabled = true;

모델불러오기(".")
  .then((불러온것) => {
    모델 = 불러온것;
    지우기단추.disabled = false;
    인식단추.disabled = false;
    결과비우기("그림을 그리면 자동으로 인식합니다.");
  })
  .catch((오류) => {
    확신도칸.textContent = "모델을 불러오지 못했습니다. 로컬 서버로 열었는지 확인해 주세요.";
    console.error(오류);
  });
