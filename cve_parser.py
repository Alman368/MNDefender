from textwrap import fill
from typing import Literal

from nvdlib import searchCVE
from nvdlib.classes import CVE


def format_cve(cve_objects: list[CVE]):
    output = ""
    for cve in cve_objects:
        output += f"CVE ID:{cve.id}\n"
        output += f"Estado: {getattr(cve, 'vulnStatus', 'Desconocido')}\n"
        output += f"Publicado: {cve.published}\n"
        output += f"Última modificación: {cve.lastModified}\n"

        # Descripciones (priorizando español)
        en_desc = next((desc.value for desc in cve.descriptions if desc.lang == 'en'), "Sin descripción")
        es_desc = next((desc.value for desc in cve.descriptions if desc.lang == 'es'), None)

        output += "Descripción:\n"
        output += fill(es_desc if es_desc else en_desc, width=80)

        # CVSS v3.1
        if hasattr(cve, 'metrics') and getattr(cve.metrics, 'cvssMetricV31', None):
            cvss = cve.metrics.cvssMetricV31[0].cvssData
            output += "CVSS v3.1:"
            output += f"  Puntuación: {cvss.baseScore} ({cvss.baseSeverity})"
            output += f"  Vector: {cvss.vectorString}"
            output += f"  Impacto: Confidencialidad: {cvss.confidentialityImpact}, Integridad: {cvss.integrityImpact}, Disponibilidad: {cvss.availabilityImpact}"

        # Productos afectados (CPE)
        if hasattr(cve, 'configurations'):
            output += "Sistemas afectados:"
            for node in cve.configurations[0].nodes:
                for match in node.cpeMatch:
                    if match.vulnerable:
                        version_info = f" (Versiones anteriores a {match.versionEndExcluding})" if hasattr(match,
                                                                                                           'versionEndExcluding') else ""
                        output += f"  - {match.criteria}{version_info}"

        # Referencias
        if hasattr(cve, 'references'):
            output += "REFERENCIAS:"
            for ref in cve.references[:3]:  # Mostrar solo 3
                tags = ', '.join(ref.tags) if hasattr(ref, 'tags') else ''
                output += f"  - {ref.url} ({tags})"

        output += "---"


def search_cve(keywords: str, limit: int = 10, severity: Literal['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] = None):
    """
    Busca vulnerabilidades en base a keywords y severity

    Args:
        keywords (str): Palabras clave para buscar
        limit (int): Número de resultados a devolver
        severity (Literal['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']): Nivel de severidad de la vulnerabilidad

    Returns:
        Lista de vulnerabilidades encontradas
    """
    results = searchCVE(keywordSearch=keywords, limit=limit, cvssV3Severity=severity)
    print("calling cve parser")
    return format_cve(results)