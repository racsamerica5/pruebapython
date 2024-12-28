from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly.express as px
import os

# Crear la aplicación Flask
app = Flask(__name__)

# Carpeta para guardar los archivos cargados
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

# Cargar archivo
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and file.filename.endswith(('.csv', '.xlsx','.xls')):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('visualize_data', filename=file.filename))
    return redirect(request.url)

# Visualizar el gráfico y realizar operaciones
@app.route('/visualize/<filename>', methods=['GET', 'POST'])
def visualize_data(filename):
    # Cargar los datos
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if filename.endswith('.csv'):
        data = pd.read_csv(filepath)
    elif filename.endswith('.xlsx'):
        data = pd.read_excel(filepath)

    columns = data.columns.tolist()

    if request.method == 'POST':
        # Obtener las variables seleccionadas por el usuario
        var1 = request.form.get('var1')
        var2 = request.form.get('var2')
        var3 = request.form.get('var3')
        operation = request.form.get('operation')  # Operación seleccionada
        group_by = request.form.get('group_by')  # Si se seleccionó agrupar por la variable 1

        # Definir las funciones de agregación
        operation_map = {
            "suma": "sum",
            "promedio": "mean",
            "desviacion": "std",
            "maximo": "max",
            "minimo": "min"
        }

        # Obtener la función de agregación basada en la operación seleccionada
        agg_func = operation_map.get(operation)

        if group_by == 'yes' and var1:
            # Agrupar por la primera variable y aplicar la operación seleccionada a la tercera variable
            grouped_data = data.groupby(var1).agg({var2: 'sum', var3: agg_func}).reset_index()
        else:
            # Si no se agrupa, tomar todos los valores sin agrupar
            grouped_data = data.copy()

            # Aplicar la operación sobre la tercera variable
            if agg_func:
                grouped_data = data.groupby(var1).agg({var2: 'sum', var3: agg_func}).reset_index()

        # Crear el gráfico
        fig = px.scatter(grouped_data, x=var1, y=var2, size=var3,
                         title=f"Gráfico: {var1} vs {var2} con {operation} sobre {var3}",
                         labels={var1: var1, var2: var2, var3: var3})

        # Convertir el gráfico a HTML
        fig_html = fig.to_html(full_html=False)

        # Resultado de la operación
        result = grouped_data[var3].iloc[0]  # Obtener el valor de la operación aplicada al primer grupo
        return render_template('index.html', fig_html=fig_html, columns=columns, filename=filename, result=result, operation_var=var3)

    return render_template('index.html', columns=columns, filename=filename)

# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True)
