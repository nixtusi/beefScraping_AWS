FROM public.ecr.aws/lambda/python:3.8

# 必要ライブラリのインストール
RUN yum install -y \
    atk cups-libs gtk3 libXcomposite alsa-lib libXcursor libXdamage \
    libXext libXi libXrandr libXScrnSaver libXtst pango at-spi2-atk \
    libXt xorg-x11-server-Xvfb xorg-x11-xauth dbus-glib dbus-glib-devel \
    nss mesa-libgbm unzip curl

# 指定バージョンの headless-chromium と chromedriver をダウンロード
RUN curl -Lo /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/86.0.4240.22/chromedriver_linux64.zip && \
    curl -Lo /tmp/headless-chromium.zip https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-57/stable-headless-chromium-amazonlinux-2.zip && \
    unzip /tmp/chromedriver.zip -d /opt/ && \
    unzip /tmp/headless-chromium.zip -d /opt/ && \
    chmod +x /opt/chromedriver /opt/headless-chromium && \
    rm -f /tmp/chromedriver.zip /tmp/headless-chromium.zip

# 実行パスを設定
ENV PATH="/opt:${PATH}"

# 必要なPythonライブラリをインストール
COPY requirements.txt ./
RUN python3.8 -m pip install -r requirements.txt -t .

# アプリ本体をコピー
COPY app.py ./

# Lambdaのハンドラー指定
CMD ["app.lambda_handler"]