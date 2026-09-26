#include <QApplication>
#include <QIcon>
#include "MainWindow.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    app.setApplicationName("Media Converter");
    app.setApplicationVersion("3.0.0");
    app.setOrganizationName("Media");
    app.setWindowIcon(QIcon(":/resources/ico.ico"));

    MainWindow window;
    window.setWindowIcon(QIcon(":/resources/ico.ico"));
    window.show();

    return app.exec();
}
