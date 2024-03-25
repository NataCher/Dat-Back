import sys
from PyQt5.QtWidgets import QApplication, QFileSystemModel, QTreeView, QWidget, QVBoxLayout


class BackupSystem(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.tree_view = QTreeView()
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(""))
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setSelectionMode(QTreeView.MultiSelection)
        self.tree_view.setHeaderHidden(True)

        layout.addWidget(self.tree_view)
        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    window = BackupSystem()
    window.setWindowTitle('Backup System')
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
