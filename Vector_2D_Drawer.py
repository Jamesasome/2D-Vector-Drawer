import pyqtgraph as pg
import numpy as np
from vectors import Vector, matrix_mult
from matmultimage import render_matrix_mult_fixed_size
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton, QLabel, QApplication, QMessageBox, QComboBox
)

####################################################################################
# --- Function Runner ---
class FunctionRunner(QWidget):
    def __init__(self, functions: dict):
        super().__init__()
        self.functions = functions
        self.setWindowTitle("Function Runner")
        self.resize(400, 100)

        self.dropdown = QComboBox()
        self.dropdown.addItems(functions.keys())
        self.dropdown.currentTextChanged.connect(self.switch_input)

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_selected_function)

        self.input_layout = QVBoxLayout()
        self.setLayout(QVBoxLayout())
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.dropdown)
        top_layout.addWidget(self.run_button)
        self.layout().addLayout(top_layout)
        self.layout().addLayout(self.input_layout)

    def switch_input(self, name):
        pass  # Not needed; handled with custom matrix dropdown

    def run_selected_function(self):
        func_name = self.dropdown.currentText()
        func, _ = self.functions[func_name]
        try:
            func()
        except Exception as e:
            print(f"Error running '{func_name}': {e}")

####################################################################################
# --- App ---
app = QApplication([])
window = QWidget()
window.setWindowTitle("2D Vector Drawer")
layout = QHBoxLayout(window)

####################################################################################
# --- Plot ---
plot = pg.PlotWidget()
plot.showGrid(x=True, y=True)
plot.setAspectLocked(True)
layout.addWidget(plot)
right_layout = QVBoxLayout()
layout.addLayout(right_layout)
layout.setStretch(1,1)

####################################################################################
# --- Vector input ---
input_layout = QHBoxLayout()
button_layout = QVBoxLayout()
right_layout.addLayout(input_layout)
right_layout.addLayout(button_layout)

input_layout.addWidget(QLabel("Vector (x,y):"))
vector_input = QLineEdit("3,2")
input_layout.addWidget(vector_input)

draw_btn = QPushButton("Draw Vectors")
clear_btn = QPushButton("Clear Vectors")
button_layout.addWidget(draw_btn)
button_layout.addWidget(clear_btn)

####################################################################################
vectors_to_draw = []

####################################################################################
# --- Dropdowns for selecting two vectors ---
select_layout = QVBoxLayout()
button_layout.addLayout(select_layout)
vec1_dropdown = QComboBox()
vec2_dropdown = QComboBox()
select_layout.addWidget(QLabel("Vector 1:"))
select_layout.addWidget(vec1_dropdown)
select_layout.addWidget(QLabel("Vector 2:"))
select_layout.addWidget(vec2_dropdown)

####################################################################################
# --- Matrix examples ---
matrix_examples = {
    "Identity": [[1,0],[0,1]],
    "Rotation 90° (clockwise)": [[0,-1],[1,0]],
    "Scaling 2x": [[2,0],[0,2]],
    "Shearing in x-direction" : [[1,1],[0,1]],
    "Shearing in y-direction" : [[1,0],[1,1]],
    "Reflect about Origin" : [[-1,0],[0,-1]],
    "Reflect about x-axis" : [[1,0],[0,-1]],
    "Reflect about y-axis" : [[-1,0],[0,1]],
    "Custom": None
}
current_matrix = matrix_examples["Identity"]

matrix_layout = QVBoxLayout()
matrix_dropdown = QComboBox()
matrix_dropdown.addItems(matrix_examples.keys())
matrix_input = QLineEdit()
matrix_input.setPlaceholderText("Enter 2x2 matrix [[a,b],[c,d]]")
matrix_input.hide()  # Only show if Custom selected
matrix_layout.addWidget(QLabel("Matrix:"))
matrix_layout.addWidget(matrix_dropdown)
matrix_layout.addWidget(matrix_input)
right_layout.addLayout(matrix_layout)

def set_current_matrix(text):
    global current_matrix
    if text == "Custom":
        matrix_input.show()
        current_matrix = None
    else:
        matrix_input.hide()
        current_matrix = matrix_examples[text]

matrix_dropdown.currentTextChanged.connect(set_current_matrix)

####################################################################################
# --- Helpers ---
def update_dropdowns():
    vec_strings = [f"({v.vector[0]}, {v.vector[1]})" for v in vectors_to_draw]
    vec1_dropdown.clear()
    vec2_dropdown.clear()
    vec1_dropdown.addItems(vec_strings)
    vec2_dropdown.addItems(vec_strings)

def draw_arrow(vec, color):
    x, y = vec.vector
    plot.plot([0, x], [0, y], pen=pg.mkPen(color, width=2))
    angle = 180 - np.degrees(np.arctan2(y, x))
    arrow = pg.ArrowItem(pos=(x, y), angle=angle, headLen=20, tipAngle=30, brush=color)
    plot.addItem(arrow)

def process_input(widget):
    try:
        text = widget.text().strip()
        if ',' not in text:
            raise ValueError("Use comma to separate coordinates")
        coords = [float(val.strip()) for val in text.split(',')]
        if len(coords) != 2:
            raise ValueError(f"Expected 2D vector, got {len(coords)}D")
        return Vector(vector=coords)
    except Exception as e:
        QMessageBox.warning(window, "Input Error", str(e))
        return None

def draw_computed_vectors():
    plot.clear()
    colors = ['r','g','b','y','c','m']
    for i, vec in enumerate(vectors_to_draw):
        draw_arrow(vec, colors[i % len(colors)])
    update_dropdowns()

####################################################################################
# --- Manual math text output ---
latex_label = QLabel()
latex_label.setFixedHeight(150)
latex_label.setStyleSheet("background-color: #f0f0f0;")
right_layout.addWidget(latex_label)

def show_matrix_mult_image(vector, matrix, result):
    # Convert vector to horizontal 1x2 row
    vec_as_matrix = [vector]          # 1 row
    result_as_matrix = [result]       # 1 row
    matrices_to_render = [vec_as_matrix, matrix, result_as_matrix]
    symbols = ["×", "="]

    pixmap = render_matrix_mult_fixed_size(matrices_to_render, symbols, target_size=(latex_label.width(), latex_label.height()))
    latex_label.setPixmap(pixmap)
    
####################################################################################
# --- Button actions ---
def draw_vectors():
    vec = process_input(vector_input)
    if vec:
        vectors_to_draw.append(vec)
        vector_input.clear()
    draw_computed_vectors()

def add_vectors():
    if len(vectors_to_draw)<2:
        QMessageBox.warning(window,"Need Vectors","Choose at least two vectors first")
        return
    idx1 = vec1_dropdown.currentIndex()
    idx2 = vec2_dropdown.currentIndex()
    if idx1<0 or idx2<0:
        QMessageBox.warning(window,"Select Vectors","Select two vectors to add")
        return
    vectors_to_draw.append(vectors_to_draw[idx1] + vectors_to_draw[idx2])
    draw_computed_vectors()

def subtract_vectors():
    if len(vectors_to_draw)<2:
        QMessageBox.warning(window,"Need Vectors","Choose at least two vectors first")
        return
    idx1 = vec1_dropdown.currentIndex()
    idx2 = vec2_dropdown.currentIndex()
    if idx1<0 or idx2<0:
        QMessageBox.warning(window,"Select Vectors","Select two vectors to subtract")
        return
    vectors_to_draw.append(vectors_to_draw[idx1] - vectors_to_draw[idx2])
    draw_computed_vectors()

def multiply_vectors_by_matrix():
    global current_matrix
    if len(vectors_to_draw) < 1:
        QMessageBox.warning(window, "Need Vector", "Choose at least one vector")
        return
    idx1 = vec1_dropdown.currentIndex()
    if idx1 < 0:
        QMessageBox.warning(window, "Select Vector", "Select one vector")
        return
    v_obj = vectors_to_draw[idx1]

    # Evaluate custom matrix if selected
    if matrix_dropdown.currentText() == "Custom":
        text = matrix_input.text().strip()
        if not text:
            QMessageBox.warning(window, "Input Error", "Enter a valid 2x2 matrix")
            return
        try:
            m = eval(text)
        except Exception as e:
            QMessageBox.warning(window, "Input Error", f"Invalid matrix syntax: {e}")
            return
    else:
        m = current_matrix

    # Ensure 2x2
    if not (isinstance(m, list) and len(m) == 2 and all(len(row) == 2 for row in m)):
        QMessageBox.warning(window, "Dimension Error", "Matrix must be 2x2")
        return

    # Multiply safely
    try:
        result = matrix_mult([v_obj.vector], m)[0]
    except Exception as e:
        QMessageBox.warning(window, "Matrix Error", str(e))
        return

    vectors_to_draw.append(Vector(vector=result))
    draw_computed_vectors()
    show_matrix_mult_image(v_obj.vector, m, result)

def clear_vectors():
    plot.clear()
    vectors_to_draw.clear()
    update_dropdowns()
    latex_label.clear()

####################################################################################
functions = {
    "Add Vectors": (add_vectors, False),
    "Subtract Vectors": (subtract_vectors, False),
    "Matrix Multiplication": (multiply_vectors_by_matrix, True)
}

func_runner = FunctionRunner(functions)
button_layout.addWidget(func_runner)

####################################################################################
draw_btn.clicked.connect(draw_vectors)
clear_btn.clicked.connect(clear_vectors)

window.show()
app.exec()