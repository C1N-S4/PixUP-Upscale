from flask import Flask, render_template_string

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fotoğraf Kalitesi Artırma</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .blur-bg { backdrop-filter: blur(10px); }
        .comparison-slider { position: relative; width: 100%; aspect-ratio: 16 / 9; overflow: hidden; border-radius: 0.5rem; }
        .comparison-slider img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: contain; }
        .comparison-slider .before { clip-path: inset(0 100% 0 0); }
        .comparison-slider .slider { position: absolute; top: 0; bottom: 0; width: 4px; background: white; left: 50%; cursor: ew-resize; }
        .comparison-slider .slider::before { content: ''; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 40px; height: 40px; background: white; border-radius: 50%; box-shadow: 0 0 10px rgba(0,0,0,0.3); }
        .comparison-slider .slider::after { content: '↔'; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 20px; color: #333; }
        .flag-icon { width: 20px; height: 20px; display: inline-block; vertical-align: middle; margin-right: 5px; }
    </style>
</head>
<body class="bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-white min-h-screen flex items-center justify-center p-4 transition-colors duration-300">
    <div class="w-full max-w-4xl blur-bg bg-white/50 dark:bg-gray-800/50 rounded-xl shadow-2xl p-8">
        <div class="flex justify-between items-center mb-8">
            <h1 class="text-3xl font-bold text-center text-gray-800 dark:text-white" id="title">Fotoğraf Kalitesi Artırma</h1>
            <div class="flex space-x-4">
                <button id="theme-toggle" class="p-2 rounded-full bg-gray-200 dark:bg-gray-700">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                    </svg>
                </button>
                <select id="language-select" class="bg-gray-200 dark:bg-gray-700 rounded-md p-2">
                    <option value="tr">
                        <span class="flag-icon">🇹🇷</span>Türkçe
                    </option>
                    <option value="en">
                        <span class="flag-icon">🇬🇧</span>English
                    </option>
                    <option value="de">
                        <span class="flag-icon">🇩🇪</span>Deutsch
                    </option>
                    <option value="ru">
                        <span class="flag-icon">🇷🇺</span>Русский
                    </option>
                </select>
            </div>
        </div>
        <div class="space-y-6">
            <input type="file" id="file-upload" class="hidden" accept="image/*">
            <label for="file-upload" class="cursor-pointer flex items-center justify-center w-full px-6 py-3 border border-transparent text-lg font-medium rounded-md text-white bg-gray-700 hover:bg-gray-800 dark:bg-gray-600 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-all duration-300 ease-in-out">
                <span id="select-photo">Fotoğraf Seç</span>
            </label>
            <div id="selected-image" class="hidden">
                <p class="text-lg font-medium mb-2" id="selected-photo-text">Seçilen Fotoğraf:</p>
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden" style="aspect-ratio: 16/9;">
                    <img id="preview-image" src="" alt="Seçilen fotoğraf" class="w-full h-full object-contain">
                </div>
            </div>
            <div>
                <label class="block text-lg font-medium mb-2"><span id="upscale-factor">Upscale Faktörü:</span> <span id="factor-value" class="text-gray-600 dark:text-gray-400">2</span>x</label>
                <input type="range" id="factor-slider" min="2" max="8" step="2" value="2" class="w-full h-2 bg-gray-300 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer">
            </div>
            <button id="upscale-button" class="w-full bg-gray-700 hover:bg-gray-800 dark:bg-gray-600 dark:hover:bg-gray-700 text-white px-6 py-3 rounded-md text-lg font-medium transition-all duration-300 ease-in-out" disabled>
                <span id="enhance-quality">Kaliteyi Artır</span>
            </button>
            <div id="progress" class="hidden space-y-2">
                <p class="text-lg font-medium" id="processing">İşleniyor...</p>
                <div class="w-full bg-gray-300 dark:bg-gray-600 rounded-full h-3">
                    <div id="progress-bar" class="bg-gray-600 dark:bg-gray-400 h-3 rounded-full transition-all duration-300 ease-out" style="width: 0%"></div>
                </div>
            </div>
            <div id="comparison-container" class="hidden space-y-4">
                <div class="comparison-slider">
                    <img id="after-image" src="" alt="After" class="after">
                    <img id="before-image" src="" alt="Before" class="before">
                    <div class="slider"></div>
                    <div class="absolute bottom-2 left-2 bg-black bg-opacity-50 px-3 py-1 rounded-full text-sm text-white" id="before-text">Öncesi</div>
                    <div class="absolute bottom-2 right-2 bg-black bg-opacity-50 px-3 py-1 rounded-full text-sm text-white" id="after-text">Sonrası</div>
                </div>
                <button id="download-button" class="w-full bg-gray-700 hover:bg-gray-800 dark:bg-gray-600 dark:hover:bg-gray-700 text-white px-6 py-3 rounded-md text-lg font-medium transition-all duration-300 ease-in-out">
                    <span id="download-photo">İyileştirilmiş Fotoğrafı İndir</span>
                </button>
            </div>
        </div>
    </div>
    <script>
        const translations = {
            tr: {
                title: "Fotoğraf Kalitesi Artırma",
                selectPhoto: "Fotoğraf Seç",
                selectedPhotoText: "Seçilen Fotoğraf:",
                upscaleFactor: "Upscale Faktörü:",
                enhanceQuality: "Kaliteyi Artır",
                processing: "İşleniyor...",
                before: "Öncesi",
                after: "Sonrası",
                downloadPhoto: "İyileştirilmiş Fotoğrafı İndir"
            },
            en: {
                title: "Photo Quality Enhancement",
                selectPhoto: "Select Photo",
                selectedPhotoText: "Selected Photo:",
                upscaleFactor: "Upscale Factor:",
                enhanceQuality: "Enhance Quality",
                processing: "Processing...",
                before: "Before",
                after: "After",
                downloadPhoto: "Download Enhanced Photo"
            },
            de: {
                title: "Fotoqualiätsverbesserung",
                selectPhoto: "Foto auswählen",
                selectedPhotoText: "Ausgewähltes Foto:",
                upscaleFactor: "Vergrößerungsfaktor:",
                enhanceQuality: "Qualität verbessern",
                processing: "Verarbeitung...",
                before: "Vorher",
                after: "Nachher",
                downloadPhoto: "Verbessertes Foto herunterladen"
            },
            ru: {
                title: "Улучшение качества фото",
                selectPhoto: "Выбрать фото",
                selectedPhotoText: "Выбранное фото:",
                upscaleFactor: "Коэффициент увеличения:",
                enhanceQuality: "Улучшить качество",
                processing: "Обработка...",
                before: "До",
                after: "После",
                downloadPhoto: "Скачать улучшенное фото"
            }
        };

        function updateLanguage(lang) {
            document.getElementById('title').textContent = translations[lang].title;
            document.getElementById('select-photo').textContent = translations[lang].selectPhoto;
            document.getElementById('selected-photo-text').textContent = translations[lang].selectedPhotoText;
            document.getElementById('upscale-factor').textContent = translations[lang].upscaleFactor;
            document.getElementById('enhance-quality').textContent = translations[lang].enhanceQuality;
            document.getElementById('processing').textContent = translations[lang].processing;
            document.getElementById('before-text').textContent = translations[lang].before;
            document.getElementById('after-text').textContent = translations[lang].after;
            document.getElementById('download-photo').textContent = translations[lang].downloadPhoto;
        }

        document.getElementById('language-select').addEventListener('change', (e) => {
            updateLanguage(e.target.value);
        });

        document.getElementById('theme-toggle').addEventListener('click', () => {
            document.documentElement.classList.toggle('dark');
        });

        const fileUpload = document.getElementById('file-upload');
        const factorSlider = document.getElementById('factor-slider');
        const factorValue = document.getElementById('factor-value');
        const upscaleButton = document.getElementById('upscale-button');
        const progress = document.getElementById('progress');
        const progressBar = document.getElementById('progress-bar');
        const comparisonContainer = document.getElementById('comparison-container');
        const beforeImage = document.getElementById('before-image');
        const afterImage = document.getElementById('after-image');
        const slider = document.querySelector('.slider');
        const selectedImage = document.getElementById('selected-image');
        const previewImage = document.getElementById('preview-image');
        const downloadButton = document.getElementById('download-button');

        let originalImage = null;

        fileUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    originalImage = e.target.result;
                    beforeImage.src = originalImage;
                    previewImage.src = originalImage;
                    selectedImage.classList.remove('hidden');
                    upscaleButton.disabled = false;
                };
                reader.readAsDataURL(file);
            }
        });

        factorSlider.addEventListener('input', () => {
            factorValue.textContent = factorSlider.value;
        });

        function simulateUpscale(imageData, factor) {
            return new Promise((resolve) => {
                const img = new Image();
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    
                    // Basit bir keskinleştirme ve kontrast artırma simülasyonu
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const data = imageData.data;
                    for (let i = 0; i < data.length; i += 4) {
                        data[i] = Math.min(255, data[i] * 1.2);     // Red
                        data[i + 1] = Math.min(255, data[i + 1] * 1.2); // Green
                        data[i + 2] = Math.min(255, data[i + 2] * 1.2); // Blue
                    }
                    ctx.putImageData(imageData, 0, 0);
                    
                    resolve(canvas.toDataURL('image/jpeg', 0.95));
                };
                img.src = imageData;
            });
        }

        upscaleButton.addEventListener('click', async () => {
            if (!originalImage) return;

            progress.classList.remove('hidden');
            comparisonContainer.classList.add('hidden');
            let progressValue = 0;
            const progressInterval = setInterval(() => {
                progressValue = Math.min(progressValue + 10, 90);
                progressBar.style.width = `${progressValue}%`;
            }, 50);

            try {
                const upscaledImage = await simulateUpscale(originalImage, parseInt(factorSlider.value));
                afterImage.onload = () => {
                    comparisonContainer.classList.remove('hidden');
                    clearInterval(progressInterval);
                    progressBar.style.width = '100%';
                    setTimeout(() => {
                        progress.classList.add('hidden');
                        progressBar.style.width = '0%';
                    }, 500);
                };
                afterImage.src = upscaledImage;
            } catch (error) {
                console.error('Upscale error:', error);
                clearInterval(progressInterval);
                progress.classList.add('hidden');
            }
        });

        downloadButton.addEventListener('click', () => {
            const link = document.createElement('a');
            link.download = 'upscaled_image.jpg';
            link.href = afterImage.src;
            link.click();
        });

        let isDragging = false;

        slider.addEventListener('mousedown', startDragging);
        slider.addEventListener('touchstart', startDragging);

        function startDragging(e) {
            isDragging = true;
            document.addEventListener('mousemove', drag);
            document.addEventListener('touchmove', drag);
            document.addEventListener('mouseup', stopDragging);
            document.addEventListener('touchend', stopDragging);
        }

        function drag(e) {
            if (!isDragging) return;
            const rect = comparisonContainer.getBoundingClientRect();
            const x = (e.clientX || e.touches[0].clientX) - rect.left;
            const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));
            slider.style.left = `${percent}%`;
            beforeImage.style.clipPath = `inset(0 ${100 - percent}% 0 0)`;
        }

        function stopDragging() {
            isDragging = false;
            document.removeEventListener('mousemove', drag);
            document.removeEventListener('touchmove', drag);
            document.removeEventListener('mouseup', stopDragging);
            document.removeEventListener('touchend', stopDragging);
        }

        // Initialize with default language (Turkish)
        updateLanguage('tr');
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(debug=True)