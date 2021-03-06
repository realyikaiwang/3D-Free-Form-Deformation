import sys
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
                             QApplication, QInputDialog, QMessageBox, QMainWindow, QAction, QFileDialog)
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from VtkModel import VtkModel
import vtk
import gc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 800)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.gridlayout = QtWidgets.QGridLayout(self.centralWidget)
        self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)
        MainWindow.setCentralWidget(self.vtkWidget)


class SimpleView(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.createActions()
        self.createMenus()
        # self.initUI()
        self.filename = "zxh-ape.obj"
        self.initVTK()
        self.showAll()

    def initVTK(self, dots=5):
        self.ren = vtk.vtkRenderer()
        self.ui.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()
        self.dots = dots
        self.dot_xyz = [None, None, None]

        self.model = VtkModel(ren=self.ren, iren=self.iren,
                              filename=self.filename, xl=dots-1, yl=dots-1, zl=dots - 1)

    def showAll(self):
        self.iren.Initialize()
        self.show()

    def createActions(self):
        self.load_obj_Action = QAction(
            'Load .OBJ', self, triggered=self.load_obj)
        self.load_image_Action = QAction(
            'Load .PNG', self, triggered=self.load_image)
        self.load_ffd_Action = QAction(
            'Load .FFD', self, triggered=self.load_ffd)
        self.save_obj_Action = QAction(
            'Save .OBJ', self, triggered=self.save_obj)
        self.save_ffd_Action = QAction(
            'Save .FFD', self, triggered=self.save_ffd)
        self.reset_Action = QAction('Reset', self, triggered=self.slot_reset)
        self.color_Action = QAction('Color', self, triggered=self.slot_color)
        self.quit_Action = QAction(
            'Quit', self, triggered=QApplication.instance().quit)
        self.select_Action = QAction(
            'Select Dot', self, triggered=self.slot_select)
        self.xyz_Action = QAction('Set XYZ', self, triggered=self.slot_xyz)
        self.resize_Action = QAction(
            'Resize', self, triggered=self.slot_resize)
        self.dots_Action = QAction("Dots", self, triggered=self.slot_dots)

    def createMenus(self):
        self.menuBar().setNativeMenuBar(False)
        self.loadMenu = self.menuBar().addMenu('Load')
        self.saveMenu = self.menuBar().addMenu('Save')
        self.modifyMenu = self.menuBar().addMenu('Modify')
        self.resetMenu = self.menuBar().addMenu('Reset')
        self.loadMenu.addAction(self.load_obj_Action)
        self.loadMenu.addAction(self.load_image_Action)
        self.loadMenu.addAction(self.load_ffd_Action)
        self.saveMenu.addAction(self.save_obj_Action)
        self.saveMenu.addAction(self.save_ffd_Action)
        self.resetMenu.addAction(self.reset_Action)
        self.resetMenu.addAction(self.dots_Action)
        self.resetMenu.addAction(self.quit_Action)
        self.modifyMenu.addAction(self.color_Action)
        self.modifyMenu.addAction(self.resize_Action)
        self.modifyMenu.addAction(self.select_Action)
        self.modifyMenu.addAction(self.xyz_Action)

    def load_obj(self):
        """导入 .obj文件"""
        filename, ok = QFileDialog.getOpenFileName(self, 'Load .OBJ', '')
        if ok:
            self.filename = filename
            self.initVTK()
            self.showAll()
            print("Done Load OBJ")
        # return

    def load_image(self):
        """ 调用 PRNet 接口，3D重建人脸 """
        reply = QMessageBox.warning(self, 'Message',
                                    "The Function isn't for Windows Platform!", QMessageBox.Yes |
                                    QMessageBox.No, QMessageBox.No)

        return

    def load_ffd(self):
        """ 导入 ffd 文件，用self.model.sphereQt函数依次设置点位移 """

        filename, ok = QFileDialog.getOpenFileName(self, 'Load .FFD', '')
        if ok:

            self.model.ffd.load_cp(filename)
            for x in range(len(self.model.ffd.control_points)):
                for y in range(len(self.model.ffd.control_points[x])):
                    for z in range(len(self.model.ffd.control_points[x][y])):
                        x_loc_new, y_loc_new, z_loc_new = self.model.ffd.new_control_points_location[
                            x][y][z]
                        x_loc_old, y_loc_old, z_loc_old = self.model.ffd.control_points_location[
                            x][y][z]
                        print(1)
                        if (x_loc_old != x_loc_new) or (y_loc_old != y_loc_new) or (z_loc_old != z_loc_new):
                            print(2)
                            self.model.sphereQt(
                                (x, y, z), self.model.ffd.new_control_points_location[x][y][z])

            print("Done Load FFD")
        return

    def save_obj(self):
        """保存 .obj文件"""
        filename, ok = QFileDialog.getSaveFileName(self, 'Save .OBJ', '')
        if ok:
            f = open(filename, 'w')
            vertices = self.model.data.GetPoints()
            pointdata = self.model.data.GetPointData().GetScalars()
            num_of_vertices = vertices.GetNumberOfPoints()
            for i in range(num_of_vertices):
                x, y, z = vertices.GetPoint(i)
                f.write('v '+str(x)+' '+str(y)+' '+str(z)+' ')
                if pointdata.GetNumberOfTuples() > 0:
                    r, g, b = pointdata.GetTuple3(i)
                    f.write(str(r/255)+' '+str(g/255)+' '+str(b/255)+'\n')
                else:
                    f.write('\n')
            num_of_faces = self.model.data.GetNumberOfCells()
            for i in range(num_of_faces):
                f.write('f')
                for j in range(self.model.data.GetCell(i).GetNumberOfPoints()):
                    f.write(
                        ' ' + str(self.model.data.GetCell(i).GetPointIds().GetId(j)+1))
                f.write('\n')
            f.close()
            print("Done Save OBJ")
            return

    def save_ffd(self):
        """保存 .ffd文件"""
        filename, ok = QFileDialog.getSaveFileName(self, 'Save .FFD', '')
        #filename= QFileDialog.getSaveFileName(self, 'Save .FFD', '')
        # print(filename)
        if ok:
            self.model.ffd.save_cp(filename)
            print("Done Save FFD")
            return

    def slot_color(self):
        """ 上色功能槽函数 """
        reply = QMessageBox.question(self, 'Message',
                                     "The Function Only for OBJ with RGB\n Information. Are You Sure?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.model.color()

    def slot_dots(self):
        """ 点阵设置槽函数 """
        DOTS, ok = QInputDialog.getInt(
            self, "DOTS SETTING", "Set the number of dots by edge: ", 5, 2, 8, 1)
        if ok:
            self.initVTK(dots=DOTS)
            self.showAll()

    def slot_reset(self):
        """ 重置功能槽函数 """
        self.initVTK()
        self.showAll()

    def slot_select(self):
        """ 选择控制点功能槽函数 """
        x, ok = QInputDialog.getInt(self, "SELCT DOT X", "0 is the leftmost, %d is the rightmost initially:" % (
            self.dots-1), 0, 0, self.dots-1, 1)
        if ok:
            self.dot_xyz[0] = x
            y, ok = QInputDialog.getInt(self, "SELCT DOT Y", "0 is the most far away from you, %d is the closest initially:" % (
                self.dots-1), 0, 0, self.dots-1, 1)
            if ok:
                self.dot_xyz[1] = y
                z, ok = QInputDialog.getInt(self, "SELCT DOT Z", "0 is the bottom, %d is the top:" % (
                    self.dots-1), 0, 0, self.dots-1, 1)
                if ok:
                    self.dot_xyz[2] = z

    def slot_xyz(self):
        """ 设置控制点位移槽函数 """
        if not(self.dot_xyz[0] is None or self.dot_xyz[1] is None or self.dot_xyz[2] is None):
            x, ok = QInputDialog.getDouble(
                self, "Setting X", "Set X:", 0, -10, 10, 0.01)
            if ok:
                y, ok = QInputDialog.getDouble(
                    self, "Setting Y", "Set Y:", 0, -10, 10, 0.01)
                if ok:
                    z, ok = QInputDialog.getDouble(
                        self, "Setting Z", "Set Z:", 0, -10, 10, 0.01)
                    if ok:
                        self.model.sphereQt(self.dot_xyz, (x, y, z))

    def slot_resize(self):
        """ 减采样槽函数，但仅针对Triangle PolyData """
        reply = QMessageBox.question(self, 'Message',
                                     "The Function Only for Triangle PolyData. Are You Sure?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            RESIZE, ok = QInputDialog.getInt(
                self, "RESIZE", "Input value from 1 to 100（%）: ", 100, 1, 100, 5)
            if ok:
                print(RESIZE)
                RESIZE = RESIZE / 100
                self.model.resize(RESIZE)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleView()
    window.show()
    window.iren.Initialize()  # Need this line to actually show the render inside Qt
    sys.exit(app.exec_())
