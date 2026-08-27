#include "MainWindow.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFrame>
#include <QStandardPaths>

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    setWindowTitle("Convertidor mp3 y mp4 - Media (C++ Edition)");
    resize(900, 620);
    setMinimumSize(850, 580);

    downloadFolder = QDir::currentPath();
    isDownloading = false;

    downloadProcess = new QProcess(this);
    connect(downloadProcess, &QProcess::readyReadStandardOutput, this, &MainWindow::onProcessOutput);
    connect(downloadProcess, &QProcess::readyReadStandardError, this, &MainWindow::onProcessError);
    connect(downloadProcess,
            static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
            this, &MainWindow::onProcessFinished);

    setupUI();
    applyDarkTheme();

    log("[Sistema] Iniciando motor C++...");
    log("[Sistema] Verificando componentes...");
}

MainWindow::~MainWindow() {
    if (downloadProcess->state() == QProcess::Running) {
        downloadProcess->kill();
    }
}

void MainWindow::setupUI() {
    QWidget *centralWidget = new QWidget(this);
    QHBoxLayout *mainLayout = new QHBoxLayout(centralWidget);
    mainLayout->setContentsMargins(0, 0, 0, 0);
    mainLayout->setSpacing(0);
    setCentralWidget(centralWidget);

    // ========== SIDEBAR ==========
    QFrame *sidebar = new QFrame();
    sidebar->setFixedWidth(230);
    sidebar->setStyleSheet("background-color: #121216;");
    QVBoxLayout *sidebarLayout = new QVBoxLayout(sidebar);
    sidebarLayout->setContentsMargins(20, 25, 20, 15);

    QLabel *titleLabel = new QLabel("Media");
    titleLabel->setStyleSheet("font-size: 18px; font-weight: bold; color: white;");
    sidebarLayout->addWidget(titleLabel);

    QLabel *subtitleLabel = new QLabel("Convertidor mp3 y mp4");
    subtitleLabel->setStyleSheet("font-size: 11px; color: #888888;");
    sidebarLayout->addWidget(subtitleLabel);
    sidebarLayout->addSpacing(20);

    statusBadge = new QLabel("Verificando sistema...");
    statusBadge->setAlignment(Qt::AlignCenter);
    statusBadge->setStyleSheet("background-color: #2C2415; color: #F39C12; padding: 5px; border-radius: 8px; font-weight: bold;");
    sidebarLayout->addWidget(statusBadge);
    sidebarLayout->addSpacing(20);

    QLabel *platformsInfo = new QLabel("Soporta:\nYouTube - TikTok\nInstagram - X - Reddit\nY +1000 sitios mas!");
    platformsInfo->setStyleSheet("color: #888888; font-size: 11px;");
    sidebarLayout->addWidget(platformsInfo);

    sidebarLayout->addStretch();

    QPushButton *historyBtn = new QPushButton("Ver Historial");
    historyBtn->setStyleSheet("QPushButton { background-color: #2d2d30; color: white; border: none; padding: 10px; border-radius: 8px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #3e3e42; }");
    connect(historyBtn, &QPushButton::clicked, this, &MainWindow::showHistory);
    sidebarLayout->addWidget(historyBtn);

    QPushButton *githubBtn = new QPushButton("Ver codigo en GitHub");
    githubBtn->setStyleSheet("QPushButton { background-color: #24292e; color: white; border: none; padding: 10px; border-radius: 8px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #40464e; }");
    connect(githubBtn, &QPushButton::clicked, this, &MainWindow::openGitHub);
    sidebarLayout->addWidget(githubBtn);

    QPushButton *donateBtn = new QPushButton("Invitame un cafe");
    donateBtn->setStyleSheet("QPushButton { background-color: #FF5F5F; color: white; border: none; padding: 10px; border-radius: 8px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #E04848; }");
    connect(donateBtn, &QPushButton::clicked, this, &MainWindow::openDonation);
    sidebarLayout->addWidget(donateBtn);

    QLabel *footer = new QLabel("Hecho con amor en C++ y 0 anuncios");
    footer->setStyleSheet("color: #555555; font-size: 10px;");
    sidebarLayout->addWidget(footer);

    mainLayout->addWidget(sidebar);

    // ========== MAIN PANEL ==========
    QWidget *mainPanel = new QWidget();
    QVBoxLayout *panelLayout = new QVBoxLayout(mainPanel);
    panelLayout->setContentsMargins(20, 20, 20, 20);
    panelLayout->setSpacing(15);

    // CARD 1: URL y Carpeta
    QFrame *cardInput = new QFrame();
    cardInput->setStyleSheet("background-color: #1e1e24; border-radius: 12px; padding: 15px;");
    QVBoxLayout *cardInputLayout = new QVBoxLayout(cardInput);

    QLabel *urlTitle = new QLabel("Enlace del Video o Playlist");
    urlTitle->setStyleSheet("color: white; font-weight: bold; font-size: 13px;");
    cardInputLayout->addWidget(urlTitle);

    urlEntry = new QLineEdit();
    urlEntry->setPlaceholderText("https://...");
    urlEntry->setFixedHeight(38);
    urlEntry->setStyleSheet("QLineEdit { background-color: #2d2d30; color: white; border: 1px solid #3e3e42; border-radius: 6px; padding: 5px 10px; font-size: 14px; }");
    cardInputLayout->addWidget(urlEntry);

    QHBoxLayout *folderLayout = new QHBoxLayout();
    QLabel *folderIcon = new QLabel("Guardar en:");
    folderIcon->setStyleSheet("color: #aaaaaa;");
    folderPathLabel = new QLabel(downloadFolder);
    folderPathLabel->setStyleSheet("color: #888888;");
    QPushButton *folderBtn = new QPushButton("Elegir");
    folderBtn->setFixedWidth(80);
    folderBtn->setStyleSheet("QPushButton { background-color: #2d2d30; color: white; border-radius: 6px; padding: 5px; } QPushButton:hover { background-color: #3e3e42; }");
    connect(folderBtn, &QPushButton::clicked, this, &MainWindow::onChooseFolderClicked);

    folderLayout->addWidget(folderIcon);
    folderLayout->addWidget(folderPathLabel, 1);
    folderLayout->addWidget(folderBtn);
    cardInputLayout->addLayout(folderLayout);
    panelLayout->addWidget(cardInput);

    // CARD 2: Opciones
    QFrame *cardOptions = new QFrame();
    cardOptions->setObjectName("cardOptions");
    cardOptions->setStyleSheet(
        "#cardOptions { background-color: #1e1e24; border-radius: 12px; }"
        );

    QVBoxLayout *cardOptionsLayout = new QVBoxLayout(cardOptions);
    cardOptionsLayout->setContentsMargins(15, 15, 15, 15);
    cardOptionsLayout->setSpacing(10);

    QLabel *fmtTitle = new QLabel("Formato de Salida");
    fmtTitle->setStyleSheet("color: white; font-weight: bold; font-size: 13px; background: transparent;");
    cardOptionsLayout->addWidget(fmtTitle);

    formatCombo = new QComboBox();
    formatCombo->addItems({"MP4 (Video + Audio)", "MP4 (Sin Audio)", "MP3 (Solo Audio)"});
    formatCombo->setFixedHeight(36);
    formatCombo->setStyleSheet(
        "QComboBox { background-color: #2d2d30; color: white; border: 1px solid #3e3e42; border-radius: 6px; padding: 5px 10px; }"
        "QComboBox::drop-down { border: none; }"
        );
    connect(formatCombo, QOverload<int>::of(&QComboBox::currentIndexChanged), this, [this]() {
        updateQualityOptions(formatCombo->currentText());
    });
    cardOptionsLayout->addWidget(formatCombo);

    QLabel *qualityTitle = new QLabel("Calidad");
    qualityTitle->setStyleSheet("color: white; font-weight: bold; font-size: 13px; background: transparent;");
    cardOptionsLayout->addWidget(qualityTitle);

    qualityCombo = new QComboBox();
    qualityCombo->setFixedHeight(36);
    qualityCombo->setStyleSheet(
        "QComboBox { background-color: #2d2d30; color: white; border: 1px solid #3e3e42; border-radius: 6px; padding: 5px 10px; }"
        "QComboBox::drop-down { border: none; }"
        );
    cardOptionsLayout->addWidget(qualityCombo);

    updateQualityOptions(formatCombo->currentText());

    // --- CHECKBOXES FIX ---
    QWidget *switchesContainer = new QWidget();
    switchesContainer->setStyleSheet("background: transparent;");
    QHBoxLayout *switchesLayout = new QHBoxLayout(switchesContainer);
    switchesLayout->setContentsMargins(0, 5, 0, 0);
    switchesLayout->setSpacing(15);

    subtitlesCheck = new QCheckBox("Subtítulos (si disponible)");
    thumbnailCheck = new QCheckBox("Miniatura (si disponible)");

    // Estilo aislado solo para los CheckBoxes
    QString checkStyle =
        "QCheckBox {"
        "   color: #FFFFFF !important;"
        "   font-size: 12px;"
        "   font-weight: normal;"
        "   spacing: 6px;"
        "   background: transparent;"
        "}"
        "QCheckBox::indicator {"
        "   width: 16px;"
        "   height: 16px;"
        "   border-radius: 4px;"
        "   border: 1px solid #555555;"
        "   background-color: #2d2d30;"
        "}"
        "QCheckBox::indicator:hover {"
        "   border: 1px solid #6C5CE7;"
        "}"
        "QCheckBox::indicator:checked {"
        "   background-color: #6C5CE7;"
        "   border: 1px solid #6C5CE7;"
        "}";

    subtitlesCheck->setStyleSheet(checkStyle);
    thumbnailCheck->setStyleSheet(checkStyle);

    switchesLayout->addWidget(subtitlesCheck);
    switchesLayout->addWidget(thumbnailCheck);
    switchesLayout->addStretch();

    cardOptionsLayout->addWidget(switchesContainer);
    panelLayout->addWidget(cardOptions);
    // CARD 3: Accion y Consola
    QFrame *cardAction = new QFrame();
    cardAction->setStyleSheet("background-color: #1e1e24; border-radius: 12px; padding: 15px;");
    QVBoxLayout *cardActionLayout = new QVBoxLayout(cardAction);

    QHBoxLayout *btnLayout = new QHBoxLayout();
    downloadBtn = new QPushButton("INICIAR DESCARGA");
    downloadBtn->setFixedHeight(46);
    downloadBtn->setStyleSheet("QPushButton { background-color: #1DB954; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 14px; } QPushButton:hover { background-color: #179B45; } QPushButton:disabled { background-color: #555555; }");
    connect(downloadBtn, &QPushButton::clicked, this, &MainWindow::onDownloadClicked);

    cancelBtn = new QPushButton("CANCELAR");
    cancelBtn->setFixedHeight(46);
    cancelBtn->setEnabled(false);
    cancelBtn->setStyleSheet("QPushButton { background-color: #E74C3C; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 14px; } QPushButton:hover { background-color: #C0392B; } QPushButton:disabled { background-color: #555555; }");
    connect(cancelBtn, &QPushButton::clicked, this, &MainWindow::onCancelClicked);

    btnLayout->addWidget(downloadBtn);
    btnLayout->addWidget(cancelBtn);
    cardActionLayout->addLayout(btnLayout);

    statusText = new QTextEdit();
    statusText->setReadOnly(true);
    statusText->setFixedHeight(120);
    statusText->setStyleSheet("QTextEdit { background-color: #0F0F12; color: #aaaaaa; border: 1px solid #2d2d30; border-radius: 6px; font-family: 'Consolas'; font-size: 11px; }");
    cardActionLayout->addWidget(statusText);
    panelLayout->addWidget(cardAction);

    mainLayout->addWidget(mainPanel, 1);
}

void MainWindow::applyDarkTheme() {
    this->setStyleSheet("QMainWindow { background-color: #121216; }");
}

void MainWindow::updateQualityOptions(const QString &format) {
    qualityCombo->clear();

    if (format.contains("MP3")) {
        qualityCombo->addItems({"320 kbps (Alta)", "256 kbps", "192 kbps", "128 kbps (Baja)"});
    } else {
        qualityCombo->addItems({"4K (2160p)", "1080p", "720p", "480p", "360p"});
    }
}

void MainWindow::log(const QString &message) {
    statusText->append(message);
    QScrollBar *scrollBar = statusText->verticalScrollBar();
    scrollBar->setValue(scrollBar->maximum());
}

void MainWindow::onDownloadClicked() {
    QString url = urlEntry->text().trimmed();
    if (url.isEmpty()) {
        log("Error: Debes ingresar una URL");
        return;
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        log("Error: La URL debe comenzar con http:// o https://");
        return;
    }

    isDownloading = true;
    downloadBtn->setEnabled(false);
    downloadBtn->setText("Procesando descarga...");
    cancelBtn->setEnabled(true);
    statusBadge->setText("Descargando...");
    statusBadge->setStyleSheet("background-color: #2C2815; color: #F1C40F; padding: 5px; border-radius: 8px; font-weight: bold;");

    statusText->clear();

    QString platform = detectPlatform(url);
    bool playlist = isPlaylist(url);

    if (playlist) {
        log("Playlist detectada! Descargando lista...");
    } else {
        log("Plataforma detectada: " + platform.toUpper());
    }

    QStringList arguments;

    if (!playlist) {
        arguments << "--no-playlist";
    }

    QString formatText = formatCombo->currentText();
    QString qualityText = qualityCombo->currentText();

    if (formatText.contains("MP3")) {
        QString audioQuality;
        if (qualityText.contains("320")) audioQuality = "0";
        else if (qualityText.contains("256")) audioQuality = "2";
        else if (qualityText.contains("192")) audioQuality = "4";
        else audioQuality = "5";

        arguments << "-x" << "--audio-format" << "mp3" << "--audio-quality" << audioQuality;
        log("Preparando MP3 - Calidad: " + qualityText);
    }
    else if (formatText.contains("Sin Audio")) {
        QString heightFilter;
        if (qualityText.contains("4K")) heightFilter = "2160";
        else if (qualityText.contains("1080")) heightFilter = "1080";
        else if (qualityText.contains("720")) heightFilter = "720";
        else if (qualityText.contains("480")) heightFilter = "480";
        else heightFilter = "360";

        arguments << "-f" << ("bestvideo[height<=" + heightFilter + "][ext=mp4]/bestvideo[height<=" + heightFilter + "]/bestvideo");
        log("Preparando MP4 sin audio - Calidad: " + qualityText);
    }
    else {
        QString heightFilter;
        if (qualityText.contains("4K")) heightFilter = "2160";
        else if (qualityText.contains("1080")) heightFilter = "1080";
        else if (qualityText.contains("720")) heightFilter = "720";
        else if (qualityText.contains("480")) heightFilter = "480";
        else heightFilter = "360";

        arguments << "-f" << ("best[height<=" + heightFilter + "][ext=mp4]/best[height<=" + heightFilter + "]/best");
        log("Preparando MP4 con audio - Calidad: " + qualityText);
    }

    if (subtitlesCheck->isChecked()) {
        arguments << "--write-sub" << "--sub-lang" << "es,en";
        log("Subtitulos activados");
    }

    if (thumbnailCheck->isChecked()) {
        arguments << "--write-thumbnail" << "--convert-thumbnails" << "jpg";
        log("Miniaturas activadas");
    }

    arguments << "-o" << (downloadFolder + "/%(title)s.%(ext)s");
    arguments << url;

    downloadProcess->start("yt-dlp", arguments);
    log("Iniciando descarga...");
}

void MainWindow::onCancelClicked() {
    if (isDownloading) {
        log("Cancelando descarga...");
        downloadProcess->kill();
    }
}

void MainWindow::onProcessOutput() {
    QByteArray output = downloadProcess->readAllStandardOutput();
    QString text = QString::fromUtf8(output);

    if (text.contains("Downloading") || text.contains("%")) {
        log(text.trimmed());
    }
}

void MainWindow::onProcessError() {
    QByteArray error = downloadProcess->readAllStandardError();
    QString errorText = QString::fromUtf8(error);
    if (!errorText.trimmed().isEmpty()) {
        log(errorText.trimmed());
    }
}

void MainWindow::onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus) {
    isDownloading = false;
    downloadBtn->setEnabled(true);
    downloadBtn->setText("INICIAR DESCARGA");
    cancelBtn->setEnabled(false);
    statusBadge->setText("Sistema Listo");
    statusBadge->setStyleSheet("background-color: #18281E; color: #2ECC71; padding: 5px; border-radius: 8px; font-weight: bold;");

    if (exitStatus == QProcess::CrashExit) {
        log("\nDescarga cancelada por el usuario.");
        return;
    }

    if (exitCode == 0) {
        log("\n" + QString("=").repeated(40));
        log("Descarga completada con exito!");
        log("Guardado en: " + downloadFolder);
        log(QString("=").repeated(40));

        saveToHistory(urlEntry->text(), "Video descargado", detectPlatform(urlEntry->text()));
    } else {
        log("\nError en la descarga (codigo: " + QString::number(exitCode) + ")");
    }
}

void MainWindow::onChooseFolderClicked() {
    QString folder = QFileDialog::getExistingDirectory(this, "Seleccionar Carpeta");
    if (!folder.isEmpty()) {
        downloadFolder = folder;
        folderPathLabel->setText(folder.length() > 45 ? folder.left(42) + "..." : folder);
        log("Carpeta seleccionada: " + folder);
    }
}

void MainWindow::showHistory() {
    QString historyFile = getHistoryFilePath();
    QFile file(historyFile);

    QMessageBox msgBox(this);
    msgBox.setWindowTitle("Historial de Descargas");
    msgBox.setText("Historial de descargas");

    if (!file.exists()) {
        msgBox.setInformativeText("No hay historial aun.\nDescarga algo para verlo aqui!");
        msgBox.exec();
        return;
    }

    if (file.open(QIODevice::ReadOnly)) {
        QByteArray data = file.readAll();
        QJsonDocument doc = QJsonDocument::fromJson(data);
        QJsonArray history = doc.array();

        QString historyText;
        if (history.isEmpty()) {
            historyText = "No hay descargas recientes.\nDescarga algo para verlo aqui!";
        } else {
            for (int i = 0; i < qMin(50, history.size()); ++i) {
                QJsonObject entry = history[i].toObject();
                historyText += entry["fecha"].toString() + " | " + entry["plataforma"].toString() + "\n";
                historyText += entry["titulo"].toString() + "\n";
                historyText += entry["url"].toString() + "\n";
                historyText += QString("-").repeated(45) + "\n";
            }
        }

        msgBox.setInformativeText(historyText);
        msgBox.exec();
        file.close();
    }
}

void MainWindow::openGitHub() {
    QDesktopServices::openUrl(QUrl("https://github.com/MayorFabDV/Convertidor_de_mp3_y_mp4"));
    log("Abriendo repositorio en tu navegador...");
}

void MainWindow::openDonation() {
    QDesktopServices::openUrl(QUrl("https://ko-fi.com/bafyam"));
    log("Gracias por considerar apoyar el proyecto!");
}

void MainWindow::saveToHistory(const QString &url, const QString &title, const QString &platform) {
    QString historyFile = getHistoryFilePath();
    QDir dir = QFileInfo(historyFile).dir();
    if (!dir.exists()) {
        dir.mkpath(".");
    }

    QJsonArray history;
    QFile file(historyFile);

    if (file.exists() && file.open(QIODevice::ReadOnly)) {
        QByteArray data = file.readAll();
        QJsonDocument doc = QJsonDocument::fromJson(data);
        history = doc.array();
        file.close();
    }

    QJsonObject newEntry;
    newEntry["fecha"] = QDateTime::currentDateTime().toString("dd/MM/yyyy hh:mm");
    newEntry["plataforma"] = platform.toUpper();
    newEntry["titulo"] = title.length() > 60 ? title.left(60) + "..." : title;
    newEntry["url"] = url;

    history.prepend(newEntry);

    while (history.size() > 50) {
        history.removeLast();
    }

    QJsonDocument doc(history);
    if (file.open(QIODevice::WriteOnly)) {
        file.write(doc.toJson(QJsonDocument::Indented));
        file.close();
    }
}

QString MainWindow::getHistoryFilePath() {
    return QDir::homePath() + "/.bafyam_media/historial.json";
}

QString MainWindow::detectPlatform(const QString &url) {
    QString urlLower = url.toLower();
    if (urlLower.contains("music.youtube.com")) return "youtube_music";
    if (urlLower.contains("tiktok.com")) return "tiktok";
    if (urlLower.contains("instagram.com")) return "instagram";
    if (urlLower.contains("facebook.com") || urlLower.contains("fb.watch")) return "facebook";
    if (urlLower.contains("twitter.com") || urlLower.contains("x.com")) return "twitter";
    if (urlLower.contains("reddit.com") || urlLower.contains("redd.it")) return "reddit";
    if (urlLower.contains("twitch.tv")) return "twitch";
    if (urlLower.contains("vimeo.com")) return "vimeo";
    if (urlLower.contains("soundcloud.com")) return "soundcloud";
    if (urlLower.contains("youtube.com") || urlLower.contains("youtu.be")) return "youtube";
    return "universal";
}

bool MainWindow::isPlaylist(const QString &url) {
    return url.toLower().contains("playlist") || url.toLower().contains("list=");
}