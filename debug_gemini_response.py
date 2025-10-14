#!/usr/bin/env python3
"""
Script para diagnosticar el problema con las respuestas de Gemini
"""

from longcontent_generator import model, generation_config

def test_gemini_response():
    """Prueba una respuesta simple de Gemini para diagnosticar el problema"""
    
    print("🧪 DIAGNÓSTICO DE RESPUESTAS GEMINI")
    print("="*50)
    
    try:
        # Prueba simple
        simple_prompt = "Escribe solo: 'Hola mundo'"
        
        print(f"📝 Prompt de prueba: {simple_prompt}")
        
        response = model.generate_content(
            simple_prompt,
            generation_config=generation_config
        )
        
        print(f"\n🔍 Tipo de respuesta: {type(response)}")
        print(f"🔍 Atributos disponibles: {dir(response)}")
        
        if hasattr(response, 'text'):
            print(f"✅ response.text disponible: {response.text}")
        else:
            print("❌ response.text no disponible")
            
        if hasattr(response, 'candidates'):
            print(f"🔍 response.candidates: {response.candidates}")
            
        if hasattr(response, 'parts'):
            print(f"🔍 response.parts: {response.parts}")
            
        print(f"\n📊 Respuesta completa: {response}")
        
        # Probar extracción de texto
        if hasattr(response, 'text'):
            extracted_text = response.text.strip()
            print(f"\n✅ Texto extraído: '{extracted_text}'")
        else:
            # Intentar extraer de otra manera
            response_str = str(response)
            print(f"\n📝 Respuesta como string: {response_str}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_response()
