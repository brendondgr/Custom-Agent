conda env list | findstr torch_audio >nul
if errorlevel 1 (
    conda create -n torch_audio python=3.10 -y
)

conda activate torch_audio

pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/xpu

pip3 install -r requirements.txt