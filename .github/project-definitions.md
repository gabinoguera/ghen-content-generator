Archivo Final – Definición del Proyecto

Descripción General

Archivo Final es una plataforma editorial que combina tecnología y sensibilidad literaria para acompañar a los autores y autoras en el camino desde su manuscrito hasta la publicación.
Nuestra misión es conectar manuscritos con las editoriales adecuadas, facilitando el acceso a la publicación tradicional y ofreciendo herramientas que aporten claridad, objetividad y confianza a los escritores en su proceso creativo.

El proyecto se compone de dos grandes ejes:
	1.	LEO, la aplicación de lectura técnica.
	2.	Matcher, el sistema de conexión entre manuscritos y editoriales.

⸻

1. LEO – Lector Editorial Online

LEO es una aplicación desarrollada en Django que analiza manuscritos y genera informes de lectura técnica.
El sistema utiliza procesamiento de lenguaje natural para ofrecer un feedback objetivo y estructurado, centrado en métricas que los editores y agentes valoran a la hora de evaluar una obra.

Objetivo

Dar a los autores una primera lectura profesional que les permita comprender en qué punto se encuentra su manuscrito antes de enviarlo a una editorial.

Métricas Actuales

LEO evalúa el manuscrito en torno a seis dimensiones principales:
	•	Sinopsis y claridad narrativa
	•	Definición de personajes
	•	Estilo y fluidez
	•	Coherencia y consistencia narrativa
	•	Adaptabilidad
	•	Originalidad

El sistema genera un feedback textual (no correctivo), con un análisis crítico de fortalezas y debilidades.
La puntuación mínima recomendada para avanzar en el proceso es 7/10 en cada métrica o un promedio general equivalente.

Versión actual (Freemium)
	•	Permite subir manuscritos en PDF.
	•	El informe se genera en minutos.
	•	El usuario puede descargarlo o visualizarlo en su panel.
	•	No ofrece aún sugerencias ni comparativas con otros textos.

⸻

2. Matcher – Sistema de Conexión Editorial

El Matcher es el siguiente paso del proceso.
Su objetivo es poner en contacto a los autores que obtienen buenas métricas en LEO con editoriales que publican obras afines por género, estilo y catálogo.

Cómo funciona
	1.	El autor obtiene su informe de lectura (LEO).
	2.	Si el manuscrito supera las métricas mínimas, el sistema lo marca como “apto para contacto editorial”.
	3.	El equipo de Archivo Final revisa la información y contacta al autor para ofrecerle el servicio de conexión con editoriales.
	4.	En esta fase, el autor recibe:
	•	Un briefing editorial personalizado.
	•	Una carta editorial para presentar su obra.
	•	La posibilidad de acceder al matcher, que sugiere editoriales relevantes.

Modelo de negocio
	•	Freemium: acceso gratuito al primer informe de lectura.
	•	Premium (en desarrollo): acceso al servicio de briefing, carta editorial y conexión con editoriales.

⸻

3. Contexto Tecnológico
	•	Aplicación principal: desarrollada en Django (Python).
	•	Base de datos: PostgreSQL.
	•	Interfaz comercial: WordPress, conectado a Brevo para gestión de leads.
	•	Próximos desarrollos: integración de dashboard avanzado, módulo de sugerencias editoriales y analítica de comportamiento (Clarity, GA4).

⸻

4. Objetivos del Proyecto

Corto plazo (0–6 meses)
	•	Validar el producto con usuarios reales.
	•	Obtener feedback cualitativo sobre la experiencia LEO.
	•	Incrementar el uso del sistema Freemium.
	•	Desarrollar la comunicación aspiracional centrada en la publicación como destino.

Medio plazo (6–12 meses)
	•	Integrar Matcher con un panel de usuario Premium.
	•	Iniciar colaboraciones con editoriales y agentes literarios.
	•	Ampliar las métricas de LEO con más granularidad (voz, ritmo, tono).
	•	Establecer una comunidad de escritores beta testers.

⸻

5. Tono y Comunicación de Marca

Archivo Final se comunica con un tono:
	•	Empático y humano, cercano al escritor que busca orientación.
	•	Inspirador, porque parte de la emoción del proceso creativo.
	•	Profesional, con lenguaje editorial preciso.
	•	No tecnocrático: la IA se menciona como herramienta, no como protagonista.

Ejemplo de claim de marca:

“Todo empieza con un manuscrito.”

⸻

6. Propósito del Blog

El blog de Archivo Final tiene como objetivo:
	•	Educar y acompañar a escritores en temas de escritura, edición y publicación.
	•	Divulgar conocimientos editoriales (estructura, estilo, narrativa).
	•	Visibilizar los aprendizajes del proyecto LEO y Matcher.
	•	Explorar la relación entre creatividad, tecnología y literatura contemporánea.

El enfoque del contenido debe poner en valor la mirada editorial, no la herramienta tecnológica, y reforzar el mensaje de que la tecnología puede abrir puertas, no reemplazar el juicio humano.