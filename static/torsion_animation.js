/**
 * Анимация кручения образца для лабораторной работы №4
 * Авторы: Коваленко Кирилл, Артем Иокерс, группа ИН-31
 */

class TorsionAnimation {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.options = {
      width: options.width || 400,
      height: options.height || 300,
      duration: options.duration || 3000,
      maxAngle: options.maxAngle || 360,
      showForce: options.showForce || true,
      showDeformation: options.showDeformation || true,
      ...options,
    };

    this.isAnimating = false;
    this.currentAngle = 0;
    this.animationFrame = null;
    this.startTime = null;

    this.createCanvas();
    this.setupAnimation();
  }

  createCanvas() {
    // Очистка контейнера
    this.container.innerHTML = "";

    // Создание canvas
    this.canvas = document.createElement("canvas");
    this.canvas.width = this.options.width;
    this.canvas.height = this.options.height;
    this.canvas.style.border = "2px solid #3498db";
    this.canvas.style.borderRadius = "10px";
    this.canvas.style.backgroundColor = "#f8f9fa";

    this.ctx = this.canvas.getContext("2d");
    this.container.appendChild(this.canvas);

    // Добавление контролов
    this.createControls();
  }

  createControls() {
    const controlsDiv = document.createElement("div");
    controlsDiv.style.marginTop = "10px";
    controlsDiv.style.textAlign = "center";

    // Информационная панель
    this.infoDiv = document.createElement("div");
    this.infoDiv.style.margin = "10px 0";
    this.infoDiv.style.fontSize = "14px";
    this.infoDiv.style.color = "#2c3e50";
    this.infoDiv.innerHTML = "Готов к запуску анимации";

    controlsDiv.appendChild(this.infoDiv);
    this.container.appendChild(controlsDiv);
  }

  setupAnimation() {
    // Инициальная отрисовка
    this.drawFrame(0);
  }

  start(materialData = {}) {
    if (this.isAnimating) return;

    this.isAnimating = true;
    this.startTime = performance.now();
    this.materialData = materialData;

    this.infoDiv.innerHTML = `
            <div style="color: #27ae60; font-weight: bold;">🔄 Выполняется кручение образца...</div>
            <div style="font-size: 12px; margin-top: 5px;">
                Материал: ${materialData.material || "Сталь"} | 
                Момент: ${materialData.moment || 1000} Н·мм | 
                Угол: ${materialData.angle || 10}°
            </div>
        `;

    this.animate();
  }

  stop(finalResult = null) {
    this.isAnimating = false;
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }

    if (finalResult) {
      // Показать реальные результаты
      this.infoDiv.innerHTML = `
                <div style="color: #27ae60; font-weight: bold;">✅ Эксперимент завершен</div>
                <div style="font-size: 12px; margin-top: 5px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: left;">
                    <div><strong>Материал:</strong> ${finalResult.material}</div>
                    <div><strong>G_эфф:</strong> ${finalResult.G_eff} МПа</div>
                    <div><strong>Угол:</strong> ${finalResult.angle}°</div>
                    <div><strong>Момент:</strong> ${finalResult.moment} Н·мм</div>
                </div>
            `;

      // Установить финальное состояние анимации
      this.currentAngle = finalResult.angle;
      this.materialData = finalResult;
      this.drawFrame(this.currentAngle);
    } else {
      this.infoDiv.innerHTML = `
                <div style="color: #2980b9; font-weight: bold;">✅ Расчет завершен</div>
                <div style="font-size: 12px; margin-top: 5px;">
                    Финальный угол поворота: ${this.currentAngle.toFixed(1)}°
                </div>
            `;
    }
  }

  animate() {
    if (!this.isAnimating) return;

    const currentTime = performance.now();
    const elapsed = currentTime - this.startTime;
    const progress = Math.min(elapsed / this.options.duration, 1);

    // Эasing функция для плавности
    const easeInOutCubic = (t) =>
      t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
    const easedProgress = easeInOutCubic(progress);

    // Вычисление текущего угла
    const targetAngle = this.materialData?.angle || 45;
    this.currentAngle = targetAngle * easedProgress;

    // Отрисовка кадра
    this.drawFrame(this.currentAngle);

    // Обновление информации
    if (this.isAnimating) {
      this.infoDiv.innerHTML = `
                <div style="color: #27ae60; font-weight: bold;">🔄 Выполняется кручение образца...</div>
                <div style="font-size: 12px; margin-top: 5px;">
                    Материал: ${this.materialData?.material || "Сталь"} | 
                    Момент: ${this.materialData?.moment || 1000} Н·мм | 
                    Текущий угол: ${this.currentAngle.toFixed(
                      1
                    )}° / ${targetAngle}°
                </div>
                <div style="width: 100%; background: #ecf0f1; height: 6px; border-radius: 3px; margin-top: 5px;">
                    <div style="width: ${
                      progress * 100
                    }%; background: linear-gradient(90deg, #3498db, #2ecc71); height: 100%; border-radius: 3px; transition: width 0.1s;"></div>
                </div>
            `;
    }

    if (progress < 1) {
      this.animationFrame = requestAnimationFrame(() => this.animate());
    } else {
      this.stop();
    }
  }

  drawFrame(angle) {
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;

    // Очистка canvas
    ctx.clearRect(0, 0, width, height);

    // Центр образца
    const centerX = width / 2;
    const centerY = height / 2;
    const cylinderWidth = 200;
    const cylinderHeight = 40;

    // Цвета в зависимости от материала
    const materialColors = {
      Сталь: { main: "#7f8c8d", stress: "#e74c3c" },
      Чугун: { main: "#95a5a6", stress: "#d35400" },
      Дерево: { main: "#8b4513", stress: "#f39c12" },
    };

    const colors =
      materialColors[this.materialData?.material] || materialColors["Сталь"];

    // Рисование основания (неподвижная часть)
    ctx.fillStyle = "#34495e";
    ctx.fillRect(
      centerX - cylinderWidth / 2 - 20,
      centerY - cylinderHeight / 2 - 10,
      20,
      cylinderHeight + 20
    );

    // Рисование образца с деформацией
    this.drawDeformedCylinder(
      centerX,
      centerY,
      cylinderWidth,
      cylinderHeight,
      angle,
      colors
    );

    // Рисование зажима (подвижная часть)
    ctx.save();
    ctx.translate(centerX + cylinderWidth / 2, centerY);
    ctx.rotate((angle * Math.PI) / 180);
    ctx.fillStyle = "#2c3e50";
    ctx.fillRect(0, -cylinderHeight / 2 - 10, 20, cylinderHeight + 20);

    // Стрелка поворота
    this.drawRotationArrow(0, 0, 60, angle, "#e74c3c");
    ctx.restore();

    // Индикаторы напряжения
    if (this.options.showDeformation) {
      this.drawStressIndicators(
        centerX,
        centerY,
        cylinderWidth,
        cylinderHeight,
        angle,
        colors.stress
      );
    }

    // Момент силы
    if (this.options.showForce) {
      this.drawMomentVector(centerX + cylinderWidth / 2 + 50, centerY, angle);
    }

    // Сетка деформации
    this.drawDeformationGrid(
      centerX,
      centerY,
      cylinderWidth,
      cylinderHeight,
      angle
    );

    // Угол и данные
    this.drawAngleDisplay(centerX, centerY - cylinderHeight / 2 - 60, angle);
  }

  drawDeformedCylinder(x, y, width, height, angle, colors) {
    const ctx = this.ctx;
    const segments = 20;
    const segmentWidth = width / segments;

    for (let i = 0; i < segments; i++) {
      const segmentX = x - width / 2 + i * segmentWidth;
      const deformation = (i / segments) * angle;
      const intensity = Math.abs(deformation) / 45; // Нормализация к максимальному углу

      ctx.save();
      ctx.translate(segmentX + segmentWidth / 2, y);
      ctx.rotate((deformation * Math.PI) / 180);

      // Цвет зависит от деформации
      const r = Math.floor(127 + intensity * 128);
      const g = Math.floor(140 - intensity * 80);
      const b = Math.floor(141 - intensity * 100);

      ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
      ctx.fillRect(-segmentWidth / 2, -height / 2, segmentWidth, height);

      // Граница сегмента
      ctx.strokeStyle = colors.main;
      ctx.lineWidth = 1;
      ctx.strokeRect(-segmentWidth / 2, -height / 2, segmentWidth, height);

      ctx.restore();
    }
  }

  drawRotationArrow(x, y, radius, angle, color) {
    const ctx = this.ctx;

    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, (angle * Math.PI) / 180);
    ctx.stroke();

    // Стрелка
    if (angle > 5) {
      const arrowAngle = (angle * Math.PI) / 180;
      const arrowX = x + radius * Math.cos(arrowAngle);
      const arrowY = y + radius * Math.sin(arrowAngle);

      ctx.beginPath();
      ctx.moveTo(arrowX, arrowY);
      ctx.lineTo(
        arrowX - 10 * Math.cos(arrowAngle - 0.3),
        arrowY - 10 * Math.sin(arrowAngle - 0.3)
      );
      ctx.moveTo(arrowX, arrowY);
      ctx.lineTo(
        arrowX - 10 * Math.cos(arrowAngle + 0.3),
        arrowY - 10 * Math.sin(arrowAngle + 0.3)
      );
      ctx.stroke();
    }
  }

  drawStressIndicators(x, y, width, height, angle, color) {
    const ctx = this.ctx;
    const intensity = Math.abs(angle) / 45;

    // Цветовые индикаторы напряжения
    for (let i = 0; i < 5; i++) {
      const alpha = intensity * (1 - i * 0.15);
      if (alpha > 0) {
        ctx.strokeStyle =
          color +
          Math.floor(alpha * 255)
            .toString(16)
            .padStart(2, "0");
        ctx.lineWidth = 2;
        ctx.strokeRect(
          x - width / 2 - 5 - i * 3,
          y - height / 2 - 5 - i * 3,
          width + 10 + i * 6,
          height + 10 + i * 6
        );
      }
    }
  }

  drawMomentVector(x, y, angle) {
    const ctx = this.ctx;
    const moment = this.materialData?.moment || 1000;
    const scale = moment / 2000; // Масштабирование

    ctx.strokeStyle = "#e67e22";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + 40 * scale, y);
    ctx.stroke();

    // Подпись
    ctx.fillStyle = "#e67e22";
    ctx.font = "12px Arial";
    ctx.fillText(`M = ${moment} Н·мм`, x + 45 * scale, y - 10);
  }

  drawDeformationGrid(x, y, width, height, angle) {
    const ctx = this.ctx;
    const gridSize = 20;

    ctx.strokeStyle = "#bdc3c7";
    ctx.lineWidth = 0.5;

    // Вертикальные линии с деформацией
    for (let i = 0; i <= width; i += gridSize) {
      const lineX = x - width / 2 + i;
      const deformation = (i / width) * angle * 0.1;

      ctx.beginPath();
      ctx.moveTo(lineX, y - height / 2);
      ctx.lineTo(lineX + deformation, y + height / 2);
      ctx.stroke();
    }

    // Горизонтальные линии
    for (let i = 0; i <= height; i += gridSize) {
      const lineY = y - height / 2 + i;
      ctx.beginPath();
      ctx.moveTo(x - width / 2, lineY);
      ctx.lineTo(x + width / 2, lineY);
      ctx.stroke();
    }
  }

  drawAngleDisplay(x, y, angle) {
    const ctx = this.ctx;

    // Фон для текста
    ctx.fillStyle = "rgba(52, 152, 219, 0.9)";
    ctx.fillRect(x - 50, y - 15, 100, 30);

    // Текст угла
    ctx.fillStyle = "white";
    ctx.font = "bold 16px Arial";
    ctx.textAlign = "center";
    ctx.fillText(`θ = ${angle.toFixed(1)}°`, x, y + 5);

    ctx.textAlign = "left"; // Сброс выравнивания
  }
}

// Глобальная переменная для анимации
let torsionAnimator = null;

// Функции для интеграции с веб-приложением
function initTorsionAnimation(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  torsionAnimator = new TorsionAnimation(containerId, {
    width: 450,
    height: 250,
    duration: 2500,
  });

  return torsionAnimator;
}

function startTorsionAnimation(materialData) {
  if (torsionAnimator) {
    torsionAnimator.start(materialData);
  }
}

function stopTorsionAnimation(finalResult = null) {
  if (torsionAnimator) {
    torsionAnimator.stop(finalResult);
  }
}
