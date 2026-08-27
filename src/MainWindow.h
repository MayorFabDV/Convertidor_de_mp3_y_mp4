#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QLineEdit>
#include <QPushButton>
#include <QTextEdit>
#include <QLabel>
#include <QCheckBox>
#include <QComboBox>
#include <QProcess>
#include <QJsonArray>
#include <QJsonObject>
#include <QJsonDocument>
#include <QFile>
#include <QDir>
#include <QDateTime>
#include <QDesktopServices>
#include <QUrl>
#include <QFileDialog>
#include <QMessageBox>
#include <QScrollBar>

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void onDownloadClicked();
    void onCancelClicked();
    void onChooseFolderClicked();
    void showHistory();
    void openGitHub();
    void openDonation();
    void onProcessOutput();
    void onProcessError();
    void onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus);

private:
    void setupUI();
    void applyDarkTheme();
    void updateQualityOptions(const QString &format);
    void saveToHistory(const QString &url, const QString &title, const QString &platform);
    void log(const QString &message);
    QString getHistoryFilePath();
    QString detectPlatform(const QString &url);
    bool isPlaylist(const QString &url);

    QLabel *statusBadge;
    QLineEdit *urlEntry;
    QLabel *folderPathLabel;
    QComboBox *formatCombo;
    QComboBox *qualityCombo;
    QCheckBox *subtitlesCheck;
    QCheckBox *thumbnailCheck;
    QPushButton *downloadBtn;
    QPushButton *cancelBtn;
    QTextEdit *statusText;

    QProcess *downloadProcess;
    QString downloadFolder;
    bool isDownloading;
};

#endif // MAINWINDOW_H