import streamlit as st
from urllib.parse import urlparse, parse_qs

def obtener_parametros_desde_url():
    url = st.experimental_get_query_params()
    return url

def main():
    st.title('Calculadora Interactiva')

    # Obtener los parámetros desde la URL
    parametros = obtener_parametros_desde_url()
    parametro1 = parametros.get('param1', [''])[0]
    parametro2 = parametros.get('param2', [''])[0]

    # Definir los inputs para los parámetros con los valores obtenidos
    parametro1 = st.text_input('Parámetro 1', value=parametro1)
    parametro2 = st.text_input('Parámetro 2', value=parametro2)

    # Botón para realizar el cálculo o recálculo
    if st.button('Calcular'):
        if parametro1 and parametro2:
            try:
                resultado = float(parametro1) + float(parametro2)
                st.write(f'Resultado del cálculo: {resultado}')

                # Actualizar los parámetros en la URL después del cálculo
                st.experimental_set_query_params(param1=parametro1, param2=parametro2)

            except ValueError:
                st.error('¡Ingrese valores numéricos válidos!')

if __name__ == '__main__':
    main()
