#include <QApplication>
#include "MainWindow.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    app.setApplicationName("Media Converter");
    app.setApplicationVersion("3.0.0");
    app.setOrganizationName("Media");

    MainWindow window;
    window.show();

    return app.exec();
}