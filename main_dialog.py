# -*- coding: utf-8 -*-

from __future__ import absolute_import

from builtins import zip

from osgeo import ogr

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.core import *

from .vfc_utils import *

from .qgis_utils.qgs import *
from .pygsf.spatial.rasters.geoarray import *
from .pygsf.spatial.rasters.io import *
from .pygsf.space_time.movements import *


class HelpDialog(QDialog):

    def __init__(self):

        QDialog.__init__(self)

        self.setWindowTitle("Help")

        self.dialog_layout = QVBoxLayout()
        self.setLayout(self.dialog_layout)

        self.help_widget = self.setup_help_widget()
        self.dialog_layout.addWidget(self.help_widget)

        self.adjustSize()

    def setup_help_widget(self):

        help_widget = QTextBrowser()
        url_path = "file:///{}/help/help.html".format(os.path.dirname(__file__))
        help_widget.setSource(QUrl(url_path))

        return help_widget


class MainDialog(QDialog):

    def __init__(self):

        QDialog.__init__(self)
        self.setup_ui()

    def setup_ui(self):

        self.setWindowTitle("VectorFieldCalc")
        
        self.dialog_layout = QVBoxLayout()
        self.setLayout(self.dialog_layout)
        
        self.input_raster_widget = self.setup_input_raster_widget()
        self.dialog_layout.addWidget(self.input_raster_widget)
        
        self.calculations_widget = self.setup_calculations_widget()
        self.dialog_layout.addWidget(self.calculations_widget)
        self.calculations_widget.setCurrentIndex(0)

        self.manage_widget = self.setup_manage_widget()
        self.dialog_layout.addWidget(self.manage_widget)

        self.adjustSize()

    def setup_input_raster_widget(self):
        
        inraster_groupbox = QGroupBox("Input rasters")
        inraster_layout = QFormLayout()

        self.inraster_x_comboBox = QComboBox()
        inraster_layout.addRow(QLabel("X-axis components"), self.inraster_x_comboBox)
        self.inraster_y_comboBox = QComboBox()
        inraster_layout.addRow(QLabel("Y-axis components"), self.inraster_y_comboBox)
                
        # append loaded mono-band raster layers to combo boxes

        monoband_raster_lyrs = loaded_monoband_raster_layers()
        self.monobands = layers_names_sources(monoband_raster_lyrs)
        for name, _ in self.monobands:
            self.inraster_x_comboBox.addItem(name)
            self.inraster_y_comboBox.addItem(name)
 
        inraster_groupbox.setLayout(inraster_layout)
               
        return inraster_groupbox

    def setup_vector_operators_widget(self):

        vectorfieldoperators_tab = QWidget()
        vectorfieldoperators_layout = QGridLayout()
        
        self.magnitude_calc_choice_checkBox = QCheckBox("Magnitude")
        vectorfieldoperators_layout.addWidget(self.magnitude_calc_choice_checkBox, 0, 0, 1, 1)
        
        self.magnitude_outraster_lineEdit = QLineEdit()
        self.magnitude_outraster_lineEdit.setPlaceholderText("magn.asc")
        vectorfieldoperators_layout.addWidget(self.magnitude_outraster_lineEdit, 0, 1, 1, 1)
        
        self.magnitude_set_outraster = QPushButton("...")
        self.magnitude_set_outraster.clicked.connect(self.select_output_rasterFile)
        vectorfieldoperators_layout.addWidget(self.magnitude_set_outraster, 0, 2, 1, 1)

        self.orientations_calc_choice_checkBox = QCheckBox("Orientations")
        vectorfieldoperators_layout.addWidget(self.orientations_calc_choice_checkBox, 1, 0, 1, 1)
        
        self.orientations_outraster_lineEdit = QLineEdit()
        self.orientations_outraster_lineEdit.setPlaceholderText("orient.asc")
        vectorfieldoperators_layout.addWidget(self.orientations_outraster_lineEdit, 1, 1, 1, 1)
        
        self.orientations_set_outraster = QPushButton("...")
        self.orientations_set_outraster.clicked.connect(self.select_output_rasterFile)
        vectorfieldoperators_layout.addWidget(self.orientations_set_outraster, 1, 2, 1, 1)
        
        self.divergence_calc_choice_checkBox = QCheckBox("Divergence")
        vectorfieldoperators_layout.addWidget(self.divergence_calc_choice_checkBox, 2, 0, 1, 1)
        
        self.divergence_outraster_lineEdit = QLineEdit()
        self.divergence_outraster_lineEdit.setPlaceholderText("div.asc")
        vectorfieldoperators_layout.addWidget(self.divergence_outraster_lineEdit, 2, 1, 1, 1)
        
        self.divergence_set_outraster = QPushButton("...")
        self.divergence_set_outraster.clicked.connect(self.select_output_rasterFile)
        vectorfieldoperators_layout.addWidget(self.divergence_set_outraster, 2, 2, 1, 1)
        
        self.curlmodule_calc_choice_checkBox = QCheckBox("Curl module")
        vectorfieldoperators_layout.addWidget(self.curlmodule_calc_choice_checkBox, 3, 0, 1, 1)
        
        self.curlmodule_outraster_lineEdit = QLineEdit()
        self.curlmodule_outraster_lineEdit.setPlaceholderText("curmod.asc")
        vectorfieldoperators_layout.addWidget(self.curlmodule_outraster_lineEdit, 3, 1, 1, 1)
        
        self.curlmodule_set_outraster = QPushButton("...")
        self.curlmodule_set_outraster.clicked.connect(self.select_output_rasterFile)
        vectorfieldoperators_layout.addWidget(self.curlmodule_set_outraster, 3, 2, 1, 1)
        
        self.calculate_results_vfop_pb = QPushButton("Calculate")
        self.calculate_results_vfop_pb.clicked.connect(self.calculate_vectorfieldops)
        vectorfieldoperators_layout.addWidget(self.calculate_results_vfop_pb, 4, 0, 1, 2)
        
        self.output_vfops_load_choice_checkBox = QCheckBox("Load output in project")
        vectorfieldoperators_layout.addWidget(self.output_vfops_load_choice_checkBox, 4, 2, 1, 1)
        
        vectorfieldoperators_tab.setLayout(vectorfieldoperators_layout)
        
        return vectorfieldoperators_tab
 
    def setup_magnitude_gradients_widget(self):
        
        magnitudegradients_tab = QWidget()
        magnitudegradients_layout = QGridLayout()
        
        self.gradient_x_calc_choice_checkBox = QCheckBox("X-axis")
        magnitudegradients_layout.addWidget(self.gradient_x_calc_choice_checkBox, 0, 0, 1, 1)
        
        self.gradient_x_outraster_lineEdit = QLineEdit()
        self.gradient_x_outraster_lineEdit.setPlaceholderText("grad_x.asc")
        magnitudegradients_layout.addWidget(self.gradient_x_outraster_lineEdit, 0, 1, 1, 1)
        
        self.gradient_x_set_outraster = QPushButton("...")
        self.gradient_x_set_outraster.clicked.connect(self.select_output_rasterFile)
        magnitudegradients_layout.addWidget(self.gradient_x_set_outraster, 0, 2, 1, 1)
        
        self.gradient_y_calc_choice_checkBox = QCheckBox("Y-axis")
        magnitudegradients_layout.addWidget(self.gradient_y_calc_choice_checkBox, 1, 0, 1, 1)
        
        self.gradient_y_outraster_lineEdit = QLineEdit()
        self.gradient_y_outraster_lineEdit.setPlaceholderText("grad_y.asc")
        magnitudegradients_layout.addWidget(self.gradient_y_outraster_lineEdit, 1, 1, 1, 1)
        
        self.gradient_y_set_outraster = QPushButton("...")
        self.gradient_y_set_outraster.clicked.connect(self.select_output_rasterFile)
        magnitudegradients_layout.addWidget(self.gradient_y_set_outraster, 1, 2, 1, 1)
         
        self.gradient_flowlines_calc_choice_checkBox = QCheckBox("Flowlines")
        magnitudegradients_layout.addWidget(self.gradient_flowlines_calc_choice_checkBox, 2, 0, 1, 1)
        
        self.gradient_flowlines_outraster_lineEdit = QLineEdit()
        self.gradient_flowlines_outraster_lineEdit.setPlaceholderText("grad_flw.asc")
        magnitudegradients_layout.addWidget(self.gradient_flowlines_outraster_lineEdit, 2, 1, 1, 1)
        
        self.gradient_flowlines_set_outraster = QPushButton("...")
        self.gradient_flowlines_set_outraster.clicked.connect(self.select_output_rasterFile)
        magnitudegradients_layout.addWidget(self.gradient_flowlines_set_outraster, 2, 2, 1, 1)
        
        self.calculate_results_grad_pb = QPushButton("Calculate")
        self.calculate_results_grad_pb.clicked.connect(self.calculate_vectorfieldgrads)
        magnitudegradients_layout.addWidget(self.calculate_results_grad_pb, 4, 0, 1, 2)
        
        self.output_grads_load_choice_checkBox = QCheckBox("Load output in project")
        magnitudegradients_layout.addWidget(self.output_grads_load_choice_checkBox, 4, 2, 1, 1)
     
        magnitudegradients_tab.setLayout(magnitudegradients_layout)
        
        return magnitudegradients_tab

    def setup_pathline_calculation_widget(self):

        pathline_tab = QWidget()
        pathline_layout = QGridLayout()

        pathline_layout.addWidget(QLabel("Input shapefile"), 0, 0, 1, 2)
        
        self.pathlines_inshapefile_input = QLineEdit()
        self.pathlines_inshapefile_input.setPlaceholderText("in_points.shp")
        pathline_layout.addWidget(self.pathlines_inshapefile_input, 0, 2, 1, 4)
        
        self.calc_pathlines_set_inshape = QPushButton("...")
        self.calc_pathlines_set_inshape.clicked.connect(self.select_input_vectorFile)
        pathline_layout.addWidget(self.calc_pathlines_set_inshape, 0, 6, 1, 1)

        pathline_layout.addWidget(QLabel("Time step"), 1, 0, 1, 1)
                
        self.pathlines_timestep_input = QLineEdit()
        self.pathlines_timestep_input.setPlaceholderText("0.1")
        pathline_layout.addWidget(self.pathlines_timestep_input, 1, 1, 1, 2)

        pathline_layout.addWidget(QLabel("Total time"), 1, 3, 1, 1)
        
        self.pathlines_totaltime_input = QLineEdit()
        self.pathlines_totaltime_input.setPlaceholderText("50")
        pathline_layout.addWidget(self.pathlines_totaltime_input, 1, 4, 1, 1)
        
        pathline_layout.addWidget(QLabel("Max error"), 1, 5, 1, 1)
        
        self.pathlines_stepmaxerror_input = QLineEdit()
        self.pathlines_stepmaxerror_input.setPlaceholderText("1e-6")
        pathline_layout.addWidget(self.pathlines_stepmaxerror_input, 1, 6, 1, 1)
                
        pathline_layout.addWidget(QLabel("Output shapefile"), 2, 0, 1, 2)
        
        self.pathlines_outshapefile_input = QLineEdit()
        self.pathlines_outshapefile_input.setPlaceholderText("pathline.shp")
        pathline_layout.addWidget(self.pathlines_outshapefile_input, 2, 2, 1, 4)
        
        self.calc_pathlines_set_outshape = QPushButton("...")
        self.calc_pathlines_set_outshape.clicked.connect(self.select_output_vectorFile)
        pathline_layout.addWidget(self.calc_pathlines_set_outshape, 2, 6, 1, 1)

        self.calculate_results_pathl_pb = QPushButton("Calculate")
        self.calculate_results_pathl_pb.clicked.connect(self.calculate_vectorfieldpathlines)
        pathline_layout.addWidget(self.calculate_results_pathl_pb, 3, 0, 1, 6)
        
        self.output_pathl_load_choice_checkBox = QCheckBox("Load output in project")
        pathline_layout.addWidget(self.output_pathl_load_choice_checkBox, 3, 6, 1, 1)


        pathline_tab.setLayout(pathline_layout)

        return pathline_tab

    def setup_calculations_widget(self):

        calculations_widget = QTabWidget()

        vectorfieldoperators_tab = self.setup_vector_operators_widget()
        calculations_widget.addTab(vectorfieldoperators_tab, "Vector field operators")

        magnitudegradients_tab = self.setup_magnitude_gradients_widget()
        calculations_widget.addTab(magnitudegradients_tab, "Magnitude gradients")

        pathline_tab = self.setup_pathline_calculation_widget()
        calculations_widget.addTab(pathline_tab, "Pathlines")

        return calculations_widget

    def setup_manage_widget(self):
        
        manage_window = QWidget()
        manage_layout = QHBoxLayout()
        manage_window.setLayout(manage_layout)

        self.about_pb = QPushButton("About")
        self.about_pb.clicked.connect(self.about)
        manage_layout.addWidget(self.about_pb)
                
        return manage_window

    def select_input_vectorFile(self):
        
        sender = self.sender()
            
        fileName, _ = QFileDialog.getOpenFileName(self, "Open shapefile", lastUsedDir(), "shp (*.shp *.SHP)")
        if not fileName:
            return
        setLastUsedDir(fileName)
    
        if sender == self.calc_pathlines_set_inshape:
            self.pathlines_inshapefile_input.setText(fileName)
    
    def select_output_rasterFile(self):
        # modified after RASTERCALC module by Barry Rowlingson

        sender = self.sender()
            
        fileName, _ = QFileDialog.getSaveFileName(self, "Save ESRI grid ascii file", lastUsedDir(), "asc (*.asc *.ASC)")
        if not fileName:
            return
          
        setLastUsedDir(fileName)
    
        if sender == self.magnitude_set_outraster:
            self.magnitude_outraster_lineEdit.setText(fileName)
        elif sender == self.orientations_set_outraster:
            self.orientations_outraster_lineEdit.setText(fileName)
        elif sender == self.divergence_set_outraster:
            self.divergence_outraster_lineEdit.setText(fileName)
        elif sender == self.curlmodule_set_outraster:
            self.curlmodule_outraster_lineEdit.setText(fileName)
        elif sender == self.gradient_x_set_outraster:
            self.gradient_x_outraster_lineEdit.setText(fileName)
        elif sender == self.gradient_y_set_outraster:
            self.gradient_y_outraster_lineEdit.setText(fileName)
        elif sender == self.gradient_flowlines_set_outraster:
            self.gradient_flowlines_outraster_lineEdit.setText(fileName)

    def select_output_vectorFile(self):
        
        sender = self.sender()
            
        fileName, _ = QFileDialog.getSaveFileName(self,
                                               "Save shapefile",
                                               lastUsedDir(),
                                               "shp (*.shp *.SHP)")
        if not fileName:
            return
        setLastUsedDir(fileName)
    
        if sender == self.calc_pathlines_set_outshape:
            self.pathlines_outshapefile_input.setText(fileName)

    def try_get_rasters_infos(self):

        field_x_ndx = self.inraster_x_comboBox.currentIndex()
        field_y_ndx = self.inraster_y_comboBox.currentIndex()

        if field_x_ndx == field_y_ndx:
            return False, "X- and Y- layers must be different"

        try:
            field_x_name, field_x_source = self.monobands[field_x_ndx]
        except Exception as err:
            return False, "Exception with getting X-layer: {}".format(err)

        try:
            field_y_name, field_y_source = self.monobands[field_y_ndx]
        except Exception as err:
            return False, "Exception with getting Y-layer: {}".format(err)

        return True, ((field_x_name, field_x_source), (field_y_name, field_y_source))

    def get_vector_operator_parameters(self):
    
        # vector operator parameters

        return (self.magnitude_calc_choice_checkBox.isChecked(), self.magnitude_outraster_lineEdit.text(),
                self.orientations_calc_choice_checkBox.isChecked(), self.orientations_outraster_lineEdit.text(),
                self.divergence_calc_choice_checkBox.isChecked(), self.divergence_outraster_lineEdit.text(),
                self.curlmodule_calc_choice_checkBox.isChecked(), self.curlmodule_outraster_lineEdit.text())

    def get_gradient_parameters(self):
            
        # vector field parameters            
        return (self.gradient_x_calc_choice_checkBox.isChecked(), self.gradient_x_outraster_lineEdit.text(),
                self.gradient_y_calc_choice_checkBox.isChecked(), self.gradient_y_outraster_lineEdit.text(),
                self.gradient_flowlines_calc_choice_checkBox.isChecked(), self.gradient_flowlines_outraster_lineEdit.text())

    def write_and_load_result(self, result_ga: GeoArray, result_fpath: str, load_in_TOC: bool) -> None:

        success, msg = try_write_esrigrid(
            geoarray=result_ga,
            outgrid_flpth=result_fpath)

        if not success:
            QMessageBox.critical(
                self,
                "Vector field processing",
                msg)
            return

        # add required layer to the map canvas - modified after RasterCalc module

        if load_in_TOC:
            newLayer = QgsRasterLayer(result_fpath, QFileInfo(result_fpath).baseName())
            QgsProject.instance().addMapLayer(newLayer)

    def calculate_vectorfieldops(self):

        # input rasters

        success, cnt = self.try_get_rasters_infos()
        if not success:
            QMessageBox.critical(
                self,
                "Vector field processing",
                cnt)
            return
        else:
            (field_x_name, field_x_source), (field_y_name, field_y_source) = cnt

        # vector field parameters

        magnitude_calc_choice, magnitude_outraster_path, \
        orientations_calc_choice, orientations_outraster_path, \
        divergence_calc_choice, divergence_outraster_path, \
        curlmodule_calc_choice, curlmodule_outraster_path = self.get_vector_operator_parameters()

        # load results

        load_output = self.output_vfops_load_choice_checkBox.isChecked()

        ### PRE-PROCESSINGS
        
        # check if any calculation

        if not (magnitude_calc_choice or orientations_calc_choice or divergence_calc_choice or curlmodule_calc_choice):
            QMessageBox.critical(
                self,
                "Vector field processing",
                "No parameter to calculate")
            return

        # get x- and y-axis component data

        success, result = try_read_raster_band(field_x_source)
        if not success:
            QMessageBox.critical(
                self,
                "Input X-field",
                result)
            return   
        else:
            gt_x, prj_x, _, data_x = result

        if gt_x.has_rotation:
            QMessageBox.critical(
                self,
                "Input X-field",
                "The plugin does not support rasters with axis rotations")
            return

        success, result = try_read_raster_band(field_y_source)
        if not success:
            QMessageBox.critical(
                self,
                "Input Y-field",
                result)
            return   
        else:
            gt_y, prj_y, _, data_y = result

        if gt_y.has_rotation:
            QMessageBox.critical(
                self,
                "Input Y-field",
                "The plugin does not support rasters with axis rotations")
            return

        # check geometric and geographic equivalence of the two components rasters

        if not levelsEquival(
            levelCreateParams(gt_x, prj_x, data_x),
            levelCreateParams(gt_y, prj_y, data_y)):
            QMessageBox.critical(
                self,
                "Raster component grids",
                "The two rasters have different geographic parameters (e.g., extent, projection, cell sizes)")
            return 
        
        # pre-processes vector field parameters

        params_choices = (magnitude_calc_choice, orientations_calc_choice, divergence_calc_choice, curlmodule_calc_choice)
        params_names = ('magnitude', 'orientation', 'divergence', 'curl module')
        params_savefiles = (magnitude_outraster_path, orientations_outraster_path, divergence_outraster_path, curlmodule_outraster_path)

        # verify input choices for vector field parameters

        for vfp_name, vfp_choice, vfp_savefile in zip(params_names, params_choices, params_savefiles):
            if vfp_choice and (vfp_savefile is None or vfp_savefile == ''):
                QMessageBox.critical(
                    self,
                    vfp_name + " values",
                    "No output layer defined")
                return 
        
        # PROCESSINGS
        
        # create velocity geoarray

        ga = GeoArray(
            inGeotransform=gt_x,
            inProjection=prj_x,
            inLevels=[data_x, data_y])

        # calculates vector field parameters

        if magnitude_calc_choice:
            magn = ga.magnitude_field()
            self.write_and_load_result(magn, magnitude_outraster_path, load_output)
        if orientations_calc_choice:
            orients = ga.orientations()
            self.write_and_load_result(orients, orientations_outraster_path, load_output)
        if divergence_calc_choice:
            diverg = ga.divergence_2D()
            self.write_and_load_result(diverg, divergence_outraster_path, load_output)
        if curlmodule_calc_choice:
            curl_mod = ga.curl_module()
            self.write_and_load_result(curl_mod, curlmodule_outraster_path, load_output)

        # all done
        QMessageBox.information(self, "Vector operators output", "Processings completed.")

    def calculate_vectorfieldgrads(self):

        # input rasters
        success, cnt = self.try_get_rasters_infos()
        if not success:
            QMessageBox.critical(
                self,
                "Vector field processing",
                cnt)
            return
        else:
            (field_x_name, field_x_source), (field_y_name, field_y_source) = cnt

        # gradients parameters                                           
        gradient_x_calc_choice, gradient_x_outraster_path, \
        gradient_y_calc_choice, gradient_y_outraster_path, \
        gradient_flowlines_calc_choice, gradient_flowlines_outraster_path  = self.get_gradient_parameters() 

        # load results                       
        load_output = self.output_grads_load_choice_checkBox.isChecked()

        ### PRE-PROCESSINGS
        
        # check if any calculation                   
        if not (gradient_x_calc_choice or gradient_y_calc_choice or gradient_flowlines_calc_choice):
            QMessageBox.critical(
                self,
                "Vector field gradient processing",
                "No parameter to calculate")
            return

        # get x- and y-axis component data

        success, result = try_read_raster_band(field_x_source)
        if not success:
            QMessageBox.critical(
                self,
                "Input X-field",
                result)
            return
        else:
            gt_x, prj_x, _, data_x = result

        if gt_x.has_rotation:
            QMessageBox.critical(
                self,
                "Input X-field",
                "The plugin does not support rasters with axis rotations")
            return

        success, result = try_read_raster_band(field_y_source)
        if not success:
            QMessageBox.critical(
                self,
                "Input Y-field",
                result)
            return
        else:
            gt_y, prj_y, _, data_y = result

        if gt_y.has_rotation:
            QMessageBox.critical(
                self,
                "Input Y-field",
                "The plugin does not support rasters with axis rotations")
            return

        # check geometric and geographic equivalence of the two components rasters

        if not levelsEquival(
            levelCreateParams(gt_x, prj_x, data_x),
            levelCreateParams(gt_y, prj_y, data_y)):
            QMessageBox.critical(
                self,
                "Raster component grids",
                "The two rasters have different geographic parameters (e.g., extent, projection, cell sizes)")
            return 
        
        # pre-processes gradients parameters            
        vfgrads_choices = (gradient_x_calc_choice, gradient_y_calc_choice, gradient_flowlines_calc_choice)     
        vfgrads_names = ('gradient along x axis','gradient along y axis','gradient along flow lines')                      
        vfgrads_savefiles = (gradient_x_outraster_path, gradient_y_outraster_path, gradient_flowlines_outraster_path)
                 
        # verify input choices for gradients parameters

        for vfg_name, vfg_choice, vfg_savefile in zip(vfgrads_names, vfgrads_choices, vfgrads_savefiles):
            if vfg_choice and (vfg_savefile is None or vfg_savefile == ''):
                QMessageBox.critical(
                    self,
                    vfg_name + " values",
                    "No output layer defined")
                return 
        
        ### PROCESSINGS
        
        # create velocity geoarray

        ga = GeoArray(
            inGeotransform=gt_x,
            inProjection=prj_x,
            inLevels=[data_x, data_y])

        # calculates gradients parameters

        if gradient_x_calc_choice:
            grad_x_vals = ga.magnitude_grads(axis='x')
            self.write_and_load_result(grad_x_vals, gradient_x_outraster_path, load_output)
        if gradient_y_calc_choice:
            grad_y_vals = ga.magnitude_grads(axis='y')
            self.write_and_load_result(grad_y_vals, gradient_y_outraster_path, load_output)
        if gradient_flowlines_calc_choice:
            grad_flwlns_vals = ga.grad_flowlines()
            self.write_and_load_result(grad_flwlns_vals, gradient_flowlines_outraster_path, load_output)

        # all done
        QMessageBox.information(self, "Gradients output", "Processings completed.")

    def calculate_vectorfieldpathlines(self):

        def interpolate_location(ga: GeoArray, t_step: Number, init_pt: Point):

            interp_point, interp_point_error_estim = interpolate_rkf(
                geoarray=ga,
                delta_time=t_step,
                start_pt=init_pt)

            if interp_point is None or interp_point_error_estim is None:
                return None, None, t_step
            elif interp_point_error_estim <= error_max_tolerance:
                return interp_point, interp_point_error_estim, t_step
            else:
                while interp_point_error_estim > error_max_tolerance:
                    t_step /= 2.0
                    interp_point, interp_point_error_estim = interpolate_rkf(
                        geoarray=ga,
                        delta_time=t_step,
                        start_pt=init_pt)
                    if interp_point is None or interp_point_error_estim is None:
                        return None, None, t_step
                return interp_point, interp_point_error_estim, t_step

        # input rasters
        success, cnt = self.try_get_rasters_infos()
        if not success:
            QMessageBox.critical(
                self,
                "Vector field processing",
                cnt)
            return
        else:
            (field_x_name, field_x_source), (field_y_name, field_y_source) = cnt

        # pathline calculation parameters

        pathlines_input_shapefile = self.pathlines_inshapefile_input.text()
        time_step = self.pathlines_timestep_input.text()
        total_time = self.pathlines_totaltime_input.text()
        error_max_tolerance = self.pathlines_stepmaxerror_input.text()
        pathlines_output_shapefile = self.pathlines_outshapefile_input.text()
        
        # load results

        load_output = self.output_pathl_load_choice_checkBox.isChecked()

        # PRE-PROCESSINGS

        # verify input parameters

        if pathlines_input_shapefile is None or pathlines_input_shapefile == '':
            QMessageBox.critical(
                self,
                "Pathline calculation",
                "No input point layer defined")
            return

        try:
            time_step = float(time_step)
            total_time = float(total_time)
        except:
            QMessageBox.critical(
                self,
                "Pathline calculation",
                "Time step and total time should be both valid decimal numbers")
            return

        if not time_step * total_time > 0.0:
            QMessageBox.critical(
                self,
                "Pathline calculation",
                "Time step and total time must be of the same sign (positive or negative)")
            return

        try:
            error_max_tolerance = float(error_max_tolerance)
        except:
            QMessageBox.critical(
                self,
                "Pathline calculation",
                "Max error should be a valid decimal number")
            return

        if not error_max_tolerance > 0.0:
            QMessageBox.critical(
                self,
                "Pathline calculation",
                "Max error should be a positive number")
            return

        if pathlines_output_shapefile is None or pathlines_output_shapefile == '':
            QMessageBox.critical(
                self,
                "Pathline calculation",
                "No output point layer defined")
            return 
            
        # PROCESSINGS

        # get x- and y-axis component data

        success, result = try_read_raster_band(field_x_source)
        if not success:
            QMessageBox.critical(
                self,
                "Input X-field",
                result)
            return
        else:
            gt_x, prj_x, _, data_x = result

        if gt_x.has_rotation:
            QMessageBox.critical(
                self,
                "Input X-field",
                "The plugin does not support rasters with axis rotations")
            return

        success, result = try_read_raster_band(field_y_source)
        if not success:
            QMessageBox.critical(
                self,
                "Input Y-field",
                result)
            return
        else:
            gt_y, prj_y, _, data_y = result

        if gt_y.has_rotation:
            QMessageBox.critical(
                self,
                "Input Y-field",
                "The plugin does not support rasters with axis rotations")
            return

        # check geometric and geographic equivalence of the two components rasters

        if not levelsEquival(
                levelCreateParams(gt_x, prj_x, data_x),
                levelCreateParams(gt_y, prj_y, data_y)):
            QMessageBox.critical(
                self,
                "Raster component grids",
                "The two rasters have different geographic parameters (e.g., extent, projection, cell sizes)")
            return
        else:
            gt = gt_x
            prj = prj_x

        # create velocity geoarray

        ga = GeoArray(
            inGeotransform=gt,
            inProjection=prj,
            inLevels=[data_x, data_y])

        # get input and output shapefiles

        pathlines_input_shapefile = str(pathlines_input_shapefile)        
        pathlines_output_shapefile = str(pathlines_output_shapefile)

        driver = ogr.GetDriverByName('ESRI Shapefile') 
      
        in_shapefile = driver.Open(pathlines_input_shapefile, 0)                        
        if in_shapefile is None:
            QMessageBox.critical(
                self,
                "Error in pathline calculation",
                "Unable to get input shapefile")
            return
   
        if os.path.exists(pathlines_output_shapefile):
            driver.DeleteDataSource(pathlines_output_shapefile)
    
        out_shape = driver.CreateDataSource(pathlines_output_shapefile)
        if out_shape is None:
            QMessageBox.critical(
                self,
                "Pathline calculation",
                "Unable to create output shapefile: %s" % pathlines_output_shapefile)
            return
        
        out_layer = out_shape.CreateLayer(
            'out_pathlines',
            geom_type=ogr.wkbPoint)

        if out_layer is None:
            QMessageBox.critical(
                self,
                "Pathline calculation",
                "Unable to create output shapefile: %s" % pathlines_output_shapefile)
            return        

        # Output shapefile field names

        path_id_fldnm = "path_id"
        point_id_fldnm = "point_id"
        x_fldnm ="x"
        y_fldnm ="y"
        estim_error_fldnm = "estim_err"
        d_s_fldnm ="delta_s"
        s_fldnm ="tot_s"
        d_time_fldnm ="delta_t"
        t_fldnm ="tot_t"
        vx_fldnm ="vx"
        vy_fldnm ="vy"
        v_magn_fldnm ="inst_v"
        aver_v_fldnm = "aver_v"

        fields = [
            (path_id_fldnm, ogr.OFTInteger),
            (point_id_fldnm, ogr.OFTInteger),
            (x_fldnm, ogr.OFTReal),
            (y_fldnm, ogr.OFTReal),
            (estim_error_fldnm, ogr.OFTReal),
            (d_s_fldnm, ogr.OFTReal),
            (s_fldnm, ogr.OFTReal),
            (d_time_fldnm, ogr.OFTReal),
            (t_fldnm, ogr.OFTReal),
            (vx_fldnm, ogr.OFTReal),
            (vy_fldnm, ogr.OFTReal),
            (v_magn_fldnm, ogr.OFTReal),
            (aver_v_fldnm, ogr.OFTReal)]

        # add fields to the output shapefile

        for fld_nm, fld_type in fields:
            out_layer.CreateField(
                ogr.FieldDefn(
                    fld_nm,
                    fld_type))

        # get the layer definition of the output shapefile

        outshape_featdef = out_layer.GetLayerDefn()
    
        # get info from input layer

        ptLayer = in_shapefile.GetLayer(0) 
    
        # initialization of pathline id

        pathline_id = 0
        
        # get next feature

        pathline_init_pt = ptLayer.GetNextFeature()
    
        while pathline_init_pt:
            
            # initialization of current pathline parameters

            pathline_id += 1

            pathline_cumul_time = 0.0
            pathline_cumul_length = 0.0

            #  initialization of initial point parameters

            curr_pt_id = 0
            interp_pt_err_estim = 0.0
            d_space = 0.0
            
            # new point with coords and path_id from input layer

            init_pt_geom_ref = pathline_init_pt.GetGeometryRef()
            init_pt_x = init_pt_geom_ref.GetX()
            init_pt_y = init_pt_geom_ref.GetY()

            init_pt = Point(
                init_pt_x,
                init_pt_y)

            curr_pt_vx = ga.interpolate_bilinear(init_pt_x, init_pt_y, level_ndx=0)
            curr_pt_vy = ga.interpolate_bilinear(init_pt_x, init_pt_y, level_ndx=1)
            if curr_pt_vx is None or curr_pt_vy is None:
                curr_v_magnitude = None
            else:
                curr_v_magnitude = sqrt(curr_pt_vx*curr_pt_vx + curr_pt_vy*curr_pt_vy)

            if pathline_cumul_length != 0.0:
                aver_v = pathline_cumul_length / pathline_cumul_time
            else:
                aver_v = None

            # pre-processing for new feature in output layer

            curr_pt_geom = ogr.Geometry(ogr.wkbPoint)
            curr_pt_geom.AddPoint(init_pt_x, init_pt_y)

            # create a new feature

            curr_pt_shape = ogr.Feature(outshape_featdef)
            curr_pt_shape.SetGeometry(curr_pt_geom)
            curr_pt_shape.SetField(path_id_fldnm, pathline_id)
            curr_pt_shape.SetField(point_id_fldnm, curr_pt_id)
            curr_pt_shape.SetField(x_fldnm, init_pt_x)
            curr_pt_shape.SetField(y_fldnm, init_pt_y)
            curr_pt_shape.SetField(estim_error_fldnm, interp_pt_err_estim)
            curr_pt_shape.SetField(d_s_fldnm, d_space)
            curr_pt_shape.SetField(s_fldnm, pathline_cumul_length)
            curr_pt_shape.SetField(d_time_fldnm, 0.0)
            curr_pt_shape.SetField(t_fldnm, pathline_cumul_time)
            curr_pt_shape.SetField(vx_fldnm, curr_pt_vx)
            curr_pt_shape.SetField(vy_fldnm, curr_pt_vy)
            curr_pt_shape.SetField(v_magn_fldnm, curr_v_magnitude)
            curr_pt_shape.SetField(aver_v_fldnm, aver_v)

            # add the feature to the output layer

            out_layer.CreateFeature(curr_pt_shape)

            # destroy no longer used objects

            curr_pt_geom.Destroy()
            curr_pt_shape.Destroy()

            # pathline cycle

            src_pt = init_pt
            d_time = time_step

            while abs(pathline_cumul_time) < abs(total_time):

                # interpolate new location

                interp_pt, interp_pt_err_estim, d_time = interpolate_location(
                    ga,
                    d_time,
                    src_pt)

                if interp_pt is None or interp_pt_err_estim is None:
                    break

                # current point parameters

                curr_pt_id += 1
                curr_pt_x = interp_pt.x
                curr_pt_y = interp_pt.y
                d_space = src_pt.dist2DWith(interp_pt)
                pathline_cumul_length += d_space
                pathline_cumul_time += d_time
                curr_pt_vx = ga.interpolate_bilinear(curr_pt_x, curr_pt_y, level_ndx=0)
                curr_pt_vy = ga.interpolate_bilinear(curr_pt_x, curr_pt_y, level_ndx=1)
                if curr_pt_vx is None or curr_pt_vy is None:
                    curr_v_magnitude = None
                else:
                    curr_v_magnitude = sqrt(curr_pt_vx * curr_pt_vx + curr_pt_vy * curr_pt_vy)

                if pathline_cumul_length != 0.0:
                    aver_v = pathline_cumul_length / pathline_cumul_time
                else:
                    aver_v = None

                # pre-processing for new feature in output layer
                curr_pt_geom = ogr.Geometry(ogr.wkbPoint)
                curr_pt_geom.AddPoint(curr_pt_x, curr_pt_y)

                # create a new feature
                curr_pt_shape = ogr.Feature(outshape_featdef)
                curr_pt_shape.SetGeometry(curr_pt_geom)
                curr_pt_shape.SetField(path_id_fldnm, pathline_id)
                curr_pt_shape.SetField(point_id_fldnm, curr_pt_id)
                curr_pt_shape.SetField(x_fldnm, curr_pt_x)
                curr_pt_shape.SetField(y_fldnm, curr_pt_y)
                curr_pt_shape.SetField(estim_error_fldnm, interp_pt_err_estim)
                curr_pt_shape.SetField(d_s_fldnm, d_space)
                curr_pt_shape.SetField(s_fldnm, pathline_cumul_length)
                curr_pt_shape.SetField(d_time_fldnm, d_time)
                curr_pt_shape.SetField(t_fldnm, pathline_cumul_time)
                curr_pt_shape.SetField(vx_fldnm, curr_pt_vx)
                curr_pt_shape.SetField(vy_fldnm, curr_pt_vy)
                curr_pt_shape.SetField(v_magn_fldnm, curr_v_magnitude)
                curr_pt_shape.SetField(aver_v_fldnm, aver_v)

                # add the feature to the output layer

                out_layer.CreateFeature(curr_pt_shape)

                # destroy no longer used objects

                curr_pt_geom.Destroy()
                curr_pt_shape.Destroy()

                src_pt = interp_pt

                # when possible, doubles the delta time value

                if interp_pt_err_estim < error_max_tolerance / 100.0:
                    d_time *= 2.0

            # get next feature

            pathline_init_pt = ptLayer.GetNextFeature()
        
        # destroy output geometry
        out_shape.Destroy()

        # add required layer to the map canvas - modified after RasterCalc module                
        if load_output:
            pathlines_outshape = QgsVectorLayer(
                pathlines_output_shapefile,
                QFileInfo(pathlines_output_shapefile).baseName(),
                "ogr")
            QgsProject.instance().addMapLayer(pathlines_outshape)

        # all done
        QMessageBox.information(self, "Pathline output", "Processings completed.")

    def about(self):
        """
        Visualize an About window.
        """
        
        QMessageBox.about(self, "About VectorFieldCalc", 
        """
            <p>VectorFieldCalc version 1.5.3<br />License: GPL v. 3</p>
            <p>Mauro Alberti</p> 
            <p>This application calculates vector field parameters (e.g., divergence, curl module, gradients)
            and pathlines.            
            </p>
             <p>Please report any bug to <a href="mailto:maualbe@libero.it">maualbe@libero.it</a></p>
        """)              

