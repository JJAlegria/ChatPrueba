# app.py
from flask import Flask, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.logic import BestMatch, SpecificResponseAdapter # Importamos SpecificResponseAdapter
from chatterbot.trainers import ChatterBotCorpusTrainer
import spacy
import os 


app = Flask(__name__)

conversaciones_faq = [
    # Tema: Horario de Atención de la Terminal
    "¿Cuál es el horario de atención de la Terminal de Transportes de Popayán?",
    "La Terminal de Transportes de Popayán opera las 24 horas del día.",
    "¿Está abierta la terminal todo el día?",
    "Sí, la Terminal de Transportes de Popayán está abierta las 24 horas.",
    "¿A qué hora cierra la terminal?",
    "La terminal de Popayán no cierra, opera las 24 horas.",
    "¿Funciona la terminal por la noche?",
    "Sí, la Terminal de Transportes de Popayán opera las 24 horas, incluyendo la noche.",
    "¿La terminal de Popayán atiende 24/7?",
    "Sí, la Terminal de Transportes de Popayán opera las 24 horas del día, los 7 días de la semana.",

    # Tema: Empresas de Transporte
    "¿Qué empresas de transporte operan en la terminal de Popayán?",
    "En la Terminal de Popayán operan empresas como **Sotracauca**, **TaxBelalcazar**, **Expreso Palmira**, **Bolivariano**, **Trans Ipiales**, **Trans Puerto Tejada**, **Trans Tambo** y **Trans Timbío**.",
    "Nombra algunas empresas de buses que salgan de Popayán.",
    "Algunas de las empresas de buses que operan desde Popayán son **Sotracauca**, **Expreso Palmira**, **Bolivariano** y **Trans Ipiales**.",
    "¿Puedo encontrar buses de Sotracauca aquí?",
    "Sí, **Sotracauca** es una de las empresas que operan en la Terminal de Transportes de Popayán.",
    "¿Hay servicio de TaxBelalcazar en la terminal?",
    "Sí, **TaxBelalcazar** es una de las empresas de transporte que encontrarás en la Terminal de Popayán.",
    "¿Expreso Palmira tiene rutas desde Popayán?",
    "Sí, **Expreso Palmira** es una de las empresas que operan desde la Terminal de Popayán.",
    "¿Puedo viajar con Bolivariano desde esta terminal?",
    "Sí, **Bolivariano** ofrece servicios desde la Terminal de Transportes de Popayán.",

    # Tema: Destinos desde Popayán (Municipios Aledaños)
    "¿Hay rutas desde Popayán a municipios cercanos?",
    "Sí, desde Popayán puedes encontrar rutas a municipios aledaños como **El Tambo**, **Timbío**, **Rosas**, **Puracé**, **Paispamba**, **Santander de Quilichao**, **Totoró**, **Bolívar**, **Piendamó** y **Paniquita**.",
    "¿Cómo llego a Santander de Quilichao desde aquí?",
    "Puedes encontrar rutas hacia **Santander de Quilichao** desde la Terminal de Transportes de Popayán.",
    "¿Hay buses para Timbío?",
    "Sí, puedes encontrar buses para **Timbío** desde la Terminal de Transportes de Popayán.",
    "¿Se puede viajar a Puracé desde esta terminal?",
    "Sí, **Puracé** es uno de los destinos a los que puedes viajar desde la Terminal de Transportes de Popayán.",
    "¿Qué destinos cubre la terminal?",
    "La Terminal de Popayán cubre destinos a municipios aledaños como **El Tambo**, **Timbío**, **Rosas**, **Puracé**, **Paispamba**, **Santander de Quilichao**, **Totoró**, **Bolívar**, **Piendamó** y **Paniquita**, además de otras ciudades importantes.",
    "Necesito ir a El Tambo, ¿desde dónde sale el bus?",
    "Los buses para **El Tambo** salen desde la Terminal de Transportes de Popayán.",
    "¿Hay buses hacia Rosas?",
    "Sí, puedes encontrar rutas hacia **Rosas** desde la Terminal de Transportes de Popayán.",
    "¿Cómo llego a Piendamó?",
    "Hay buses disponibles hacia **Piendamó** desde la Terminal de Transportes de Popayán.",
    "¿Qué empresas van a Piendamó?",
    "Varias empresas como **Sotracauca** y **Trans Piendamó** ofrecen rutas a Piendamó.",

    # Tema: Servicios Generales de la Terminal
    "¿Hay baños en la terminal?",
    "Sí, la Terminal de Transportes de Popayán cuenta con servicio de **baños públicos** para los viajeros.",
    "¿Dónde puedo encontrar un cajero automático?",
    "Generalmente, los **cajeros automáticos** se ubican cerca de la entrada principal o en la zona de servicios de la terminal.",
    "¿Hay servicio de consigna de equipaje o guarda equipaje?",
    "Sí, la terminal ofrece un servicio de **guarda equipaje** o consigna para que puedas dejar tus pertenencias de forma segura.",
    "¿Se pueden cargar celulares en la terminal?",
    "Sí, la terminal cuenta con **puntos de carga** para dispositivos móviles en varias áreas comunes.",
    "¿Dónde puedo comprar algo de comer o beber?",
    "Dentro de la terminal encontrarás **cafeterías y tiendas de conveniencia** donde puedes comprar alimentos y bebidas.",
    "¿Hay alguna farmacia en la terminal?",
    "La terminal puede contar con una **farmacia o un puesto de primeros auxilios**. Te recomendamos preguntar en el punto de información.",
    "¿Hay taxis disponibles al salir de la terminal?",
    "Sí, al salir de la terminal encontrarás una **zona designada para taxis seguros**.",
    "¿Dónde está el punto de información?",
    "El **punto de información** o servicio al cliente se encuentra usualmente en el hall central o cerca de la entrada principal de la terminal.",
    "¿Se puede acceder a Wi-Fi en la terminal?",
    "Sí, la Terminal de Transportes de Popayán ofrece servicio de **Wi-Fi gratuito** para los usuarios en las zonas comunes.",
    "¿Hay alguna zona de espera cómoda?",
    "Sí, la terminal dispone de varias **zonas de espera con sillas** para la comodidad de los pasajeros.",
    "¿Hay restaurantes en la terminal?",
    "Sí, encontrarás opciones de **restaurantes y locales de comida rápida** dentro de la terminal.",
    "¿Ofrecen servicio de encomiendas?",
    "Sí, la mayoría de las empresas de transporte en la terminal ofrecen servicio de **encomiendas y carga**.",

    # Tema: Horarios de Salida a Pueblos Aledaños (Datos Generados)
    "¿Cuál es el primer bus para El Tambo?",
    "El primer bus para **El Tambo** sale aproximadamente a las **5:30 AM**.",
    "¿Hasta qué hora hay buses para El Tambo?",
    "Los buses para **El Tambo** suelen salir hasta las **10:00 PM**.",
    "¿Con qué frecuencia salen los buses a Timbío?",
    "Los buses para **Timbío** tienen salidas frecuentes, aproximadamente **cada 20-30 minutos**, desde las **4:30 AM** hasta las **10:00 PM**.",
    "¿A qué hora sale el último bus para Timbío?",
    "El último bus hacia **Timbío** sale alrededor de las **10:00 PM**.",
    "¿Hay buses para Rosas por la mañana?",
    "Sí, los primeros buses para **Rosas** inician sus salidas desde las **5:00 AM**.",
    "¿Cuándo sale el último bus para Rosas?",
    "El último bus para **Rosas** suele salir cerca de las **5:45 PM**.",
    "¿A qué hora puedo tomar un bus para Puracé?",
    "Hay buses para **Puracé** con salidas en la mañana, aproximadamente desde las **8:00 AM**.",
    "¿Con qué regularidad salen los buses a Paispamba?",
    "Los buses hacia **Paispamba** suelen tener varias salidas durante el día, desde las **5:30 AM** hasta las **5:00 PM**.",
    "¿Hay buses directos a Santander de Quilichao?",
    "Sí, existen varias rutas directas a **Santander de Quilichao** con salidas frecuentes a lo largo del día, desde temprano en la mañana hasta la tarde noche.",
    "¿A qué hora es el último bus para Santander de Quilichao?",
    "Los buses a **Santander de Quilichao** tienen salidas hasta altas horas de la noche, incluso hasta las **9:00 PM o 10:00 PM**.",
    "¿Puedo viajar a Totoró en bus?",
    "Sí, los buses a **Totoró** tienen salidas desde aproximadamente las **8:00 AM** hasta las **2:00 PM**.",
    "¿Cuáles son los horarios de bus para Bolívar?",
    "Los buses para **Bolívar** tienen salidas a lo largo del día, generalmente desde las **5:30 AM** hasta las **3:30 PM**.",
    "¿Hay buses a Piendamó durante la tarde?",
    "Sí, los buses a **Piendamó** operan con una alta frecuencia durante todo el día, incluyendo la tarde, desde las **5:00 AM** hasta las **9:00 PM**.",
    "¿Cuál es el horario de buses para Paniquita?",
    "Los buses para **Paniquita** tienen salidas limitadas, te recomiendo consultar directamente en taquilla para horarios específicos, pero suelen haber servicios en la mañana y en la tarde.",
    "¿Hay rutas nocturnas a los pueblos aledaños?",
    "Para destinos cercanos como **Timbío** y **El Tambo**, puede haber servicios hasta tarde en la noche. Para otros municipios, los horarios suelen ser diurnos.",

    # Tema: Horarios de Salida y Empresas por Municipio (Datos Generados)
    # El Tambo
    "¿A qué hora sale el primer bus para El Tambo y con qué empresa?",
    "El primer bus para **El Tambo** sale alrededor de las **7:00 AM** con **Trans Tambo**.",
    "¿Cuál es la última salida a El Tambo y qué empresa la opera?",
    "La última salida a **El Tambo** es aproximadamente a las **10:58 PM**, también con **Trans Tambo**.",
    "¿Qué empresas van a El Tambo?",
    "Principalmente **Trans Tambo** ofrece rutas a El Tambo. También podrías encontrar servicios de **Sotracauca**.",
    "¿Qué empresa va hacia Timbío?",
    "Principalmente **Trans Tambo** ofrece rutas a El Tambo. También podrías encontrar servicios de **Sotracauca**.",
    
    # Timbío
    "¿Con qué frecuencia hay buses a Timbío y qué empresas los ofrecen?",
    "Hay buses a **Timbío** cada **20-30 minutos** desde las **4:30 AM** hasta las **10:00 PM**. **Trans Timbío** es la empresa principal, y **Sotracauca** también ofrece servicios.",
    "¿A que hora hay buses a Timbío?",
    "Hay buses a **Timbío** cada **20-30 minutos** desde las **4:30 AM** hasta las **10:00 PM**. **Trans Timbío** es la empresa principal, y **Sotracauca** también ofrece servicios.",
    "¿Cuál es el último horario para viajar a Timbío y con qué empresa?",
    "El último bus a **Timbío** sale a las **10:00 PM** con **Trans Timbío**.",
    "¿Qué empresa cubre la ruta a Timbío?",
    "**Trans Timbío** es la empresa que opera la ruta a Timbío, con apoyo de **Sotracauca**.",
    "¿Qué empresa va hacia Timbío?",
    "**Trans Timbío** es la empresa que opera la ruta a Timbío, con apoyo de **Sotracauca**.",
    "¿Qué empresa viaja a Timbío?",
    "**Trans Timbío** es la empresa que opera la ruta a Timbío, con apoyo de **Sotracauca**.",

    # Rosas
    "¿A qué hora sale el primer bus a Rosas y qué empresa lo cubre?",
    "El primer bus hacia **Rosas** sale a las **5:00 AM** con **Sotracauca**.",
    "¿Cuál es el último bus a Rosas y qué empresa lo ofrece?",
    "El último bus a **Rosas** sale a las **5:45 PM**. **Sotracauca** ofrece este servicio.",
    "¿Qué empresa viaja a Rosas?",
    "**Sotracauca** ofrece rutas a Rosas.",
    "¿Qué empresa van a Rosas?",
    "**Sotracauca** ofrece rutas a Rosas.",

    # Puracé
    "¿Cuándo puedo viajar a Puracé y con qué empresa?",
    "Puedes viajar a **Puracé** desde las **8:30 AM**. **Sotracauca** ofrece este servicio.",
    "¿Hay buses directos a Puracé y quién los opera?",
    "Sí, **Sotracauca** ofrece un servicio directo a Puracé.",
    "¿Qué empresa me lleva a Puracé?",
    "**Sotracauca** es la empresa que viaja a Puracé.",

    # Paispamba
    "¿A qué hora salen los buses a Paispamba y qué empresas van?",
    "Los buses a **Paispamba** salen desde las **5:30 AM** hasta las **5:00 PM**. **Trans Tambo** y **Sotracauca** ofrecen este servicio.",
    "¿Cuál es el horario para viajar a Paispamba?",
    "El horario para viajar a **Paispamba** es desde las **5:30 AM** hasta las **5:00 PM**.",
    "¿Qué empresa cubre la ruta a Paispamba?",
    "**Trans Tambo** y **Sotracauca** son las empresas que operan la ruta a Paispamba.",

    # Santander de Quilichao
    "¿Con qué frecuencia salen buses a Santander de Quilichao y cuáles son las empresas?",
    "Hay salidas frecuentes a **Santander de Quilichao** a lo largo del día, desde las **5:00 AM** hasta las **8:00 PM**. **TaxBelalcazar** y **Expreso Palmira** ofrecen este servicio.",
    "¿Hasta qué hora puedo viajar a Santander de Quilichao y con qué empresa?",
    "Puedes viajar a **Santander de Quilichao** hasta las **8:00 PM** con **TaxBelalcazar** o **Expreso Palmira**.",
    "¿Qué empresa ofrece la ruta a Santander de Quilichao?",
    "**TaxBelalcazar** y **Expreso Palmira** ofrecen la ruta a Santander de Quilichao.",

    # Totoró
    "¿A qué hora hay buses para Totoró y qué empresas van?",
    "Los buses a **Totoró** salen desde las **8:00 AM** hasta las **2:00 PM**. **TaxBelalcazar** y **Sotracauca** ofrecen este servicio.",
    "¿Cuál es el último bus a Totoró?",
    "El último bus a **Totoró** sale a las **2:00 PM**.",
    "¿Qué empresa viaja a Totoró?",
    "**TaxBelalcazar** y **Sotracauca** ofrecen rutas a Totoró.",

    # Bolívar
    "¿Cuáles son los horarios para viajar a Bolívar y con qué empresa?",
    "Los horarios para viajar a **Bolívar** son desde las **7:30 AM** hasta las **3:30 PM**. **Sotracauca** y **Bolivariano** ofrecen este servicio.",
    "¿Hay buses directos a Bolívar?",
    "Sí, **Sotracauca** y **Bolivariano** ofrecen buses directos a Bolívar.",
    "¿Qué empresa me lleva a Bolívar?",
    "**Sotracauca** y **Bolivariano** son las empresas que viajan a Bolívar.",

    # Piendamó
    "¿Con qué frecuencia hay buses a Piendamó y qué empresas los operan?",
    "Hay buses a **Piendamó** con salidas desde las **5:00 AM** hasta las **9:00 PM**, con alta frecuencia. **TaxBelalcazar** y **Trans Timbío** ofrecen rutas a Piendamó.",
    "¿Hasta qué hora puedo viajar a Piendamó?",
    "Puedes viajar a **Piendamó** hasta las **9:00 PM**.",
    "¿Qué empresas van a Piendamó?",
    "**TaxBelalcazar** y **Trans Timbío** ofrecen rutas a Piendamó.",

    # Paniquita
    "¿Cuáles son los horarios para viajar a Paniquita y con qué empresa?",
    "Los horarios para viajar a **Paniquita** son limitados, te recomiendo consultar directamente en taquilla. **Sotracauca** ofrece este servicio con algunas salidas en la mañana y tarde.",
    "¿Hay buses directos a Paniquita?",
    "Sí, **Sotracauca** ofrece buses directos a Paniquita.",
    "¿Qué empresa viaja a Paniquita?",
    "**Sotracauca** es la empresa que viaja a Paniquita."
]


try:
    nlp = spacy.load("es_core_news_sm")
    print("Modelo 'es_core_news_sm' de SpaCy cargado.")
except OSError:
    print("El modelo 'es_core_news_sm' de SpaCy no se encontró. Intentando descarga para uso local...")
    os.system("python -m spacy download es_core_news_sm")
    nlp = spacy.load("es_core_news_sm")

# ChatterBot a menudo requiere el modelo de inglés también, incluso para español.
try:
    nlp_en = spacy.load("en_core_web_sm")
    print("Modelo 'en_core_web_sm' de SpaCy cargado.")
except OSError:
    print("El modelo 'en_core_web_sm' de SpaCy no se encontró. Intentando descarga para uso local...")
    os.system("python -m spacy download en_core_web_sm")
    nlp_en = spacy.load("en_core_web_sm")


DB_FILE = 'db.sqlite3'

chatbot = ChatBot(
    'TerminalFAQsBot', # Nombre del chatbot
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri=f'sqlite:///{DB_FILE}', # Ruta de la base de datos
    logic_adapters=[
        # Adaptador para palabras clave específicas (con mayor peso)
        {
            'import_path': 'chatterbot.logic.SpecificResponseAdapter',
            'input_text': 'Piendamó',
            'output_text': 'Para Piendamó hay buses disponibles con alta frecuencia durante todo el día, desde las 5:00 AM hasta las 9:00 PM. Varias empresas como Sotracauca y Trans Piendamó ofrecen rutas.',
            'threshold': 0.85
        },
        {
            'import_path': 'chatterbot.logic.SpecificResponseAdapter',
            'input_text': 'Santander de Quilichao',
            'output_text': 'Existen varias rutas directas a Santander de Quilichao con salidas frecuentes a lo largo del día, desde temprano en la mañana hasta la tarde noche, incluso hasta las 9:00 PM o 10:00 PM.',
            'threshold': 0.85
        },
        {
            'import_path': 'chatterbot.logic.SpecificResponseAdapter',
            'input_text': 'Timbío',
            'output_text': 'Los buses para Timbío tienen salidas frecuentes, aproximadamente cada 20-30 minutos, desde las 4:30 AM hasta las 10:00 PM.',
            'threshold': 0.85
        },
        {
            'import_path': 'chatterbot.logic.SpecificResponseAdapter',
            'input_text': 'El Tambo',
            'output_text': 'El primer bus para El Tambo sale aproximadamente a las 5:30 AM y los servicios suelen operar hasta las 10:00 PM.',
            'threshold': 0.85
        },
        # Adaptadores para saludos y despedidas específicos (muy alta prioridad)
        {
            'import_path': 'chatterbot.logic.SpecificResponseAdapter',
            'input_text': 'hola',
            'output_text': '¡Hola! Soy el asistente virtual de la Terminal de Popayán. ¿En qué puedo ayudarte hoy?',
            'threshold': 0.95
        },
        {
            'import_path': 'chatterbot.logic.SpecificResponseAdapter',
            'input_text': 'gracias',
            'output_text': 'De nada, estoy aquí para servirte.',
            'threshold': 0.95
        },
        {
            'import_path': 'chatterbot.logic.SpecificResponseAdapter',
            'input_text': 'adios',
            'output_text': '¡Adiós! Que tengas un buen día.',
            'threshold': 0.95
        },
        # El BestMatch Adapter va al final, como fallback
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'Lo siento, no pude entender tu pregunta. Por favor, reformúlala o intenta con algo más específico.',
            'maximum_similarity_threshold': 0.70 # Ajusta este umbral según tus pruebas
        }
    ],
    nlp=nlp, # Pasamos el objeto SpaCy cargado
    read_only=True # Para que el bot no aprenda de las interacciones en línea
)

print(f"[{DB_FILE}] no encontrado. Entrenando al chatbot...")
    # Entrenamiento con tus FAQs
trainer = ListTrainer(chatbot)
print("Entrenando ChatBot con FAQs...")
trainer.train(conversaciones_faq)
print("Entrenamiento de FAQs completado.")

    # Entrenamiento con el corpus general de ChatterBot (para chitchat)
trainer_corpus = ChatterBotCorpusTrainer(chatbot)
print("Entrenando corpus general (chitchat)...")
trainer_corpus.train('chatterbot.corpus.spanish')
print("Entrenamiento de corpus general completado.")



@app.route('/ask', methods=['POST'])
def ask_bot():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No se proporcionó un mensaje en el cuerpo de la solicitud JSON."}), 400

    try:
        response = chatbot.get_response(user_message)
        # Convertimos la respuesta a string para asegurar el formato JSON
        return jsonify({"response": str(response)})
    except Exception as e:
        # Capturamos cualquier error durante la respuesta del bot
        print(f"Error al obtener respuesta del chatbot: {e}")
        return jsonify({"error": "Ocurrió un error interno al procesar tu pregunta."}), 500

@app.route('/')
def index():
    return """
    <h1>Asistente de la Terminal de Transportes de Popayán</h1>
    <p>¡Hola! Soy tu chatbot de FAQs. Estoy listo para responder tus preguntas.</p>
    <p>Para interactuar, envía una solicitud <strong>POST</strong> a la ruta <code>/ask</code> con un cuerpo JSON como este:</p>
    <pre><code>{"message": "Tu pregunta aquí"}</code></pre>
    <p>Ejemplo de pregunta: <em>"¿Cuál es el horario de atención?"</em></p>
    """

# --- 6. Ejecutar la Aplicación Flask ---
if __name__ == '__main__':
    # Usamos 0.0.0.0 para que sea accesible desde cualquier IP (necesario en servidores)
    # El puerto 5000 es el default de Flask. Gunicorn lo gestionará en Render.
    app.run(host='0.0.0.0', port=5000, debug=True)