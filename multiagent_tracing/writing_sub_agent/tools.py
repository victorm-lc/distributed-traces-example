from typing import Any, Callable, List, Optional, cast

from langchain_core.tools import tool
from typing import Dict, List, Any
from datetime import datetime

@tool
def report_generation_tool(
    title: str,
    sections: List[Dict[str, Any]],
    summary: str = "",
    recommendations: List[str] = None,
    metadata: Dict[str, Any] = None
) -> str:
    """
    Generate a formatted report with the provided content.
    
    Args:
        title: The main title of the report
        sections: List of dictionaries with 'heading' and 'content' keys
        summary: Executive summary or overview (optional)
        recommendations: List of key recommendations (optional)
        metadata: Additional metadata like author, date, etc. (optional)
    
    Returns:
        Formatted report as a string
    """
    if recommendations is None:
        recommendations = []
    if metadata is None:
        metadata = {}
    
    # Build the report
    report_lines = []
    
    # Header
    report_lines.append("=" * 80)
    report_lines.append(f"REPORT: {title.upper()}")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # Metadata section
    report_lines.append("REPORT METADATA")
    report_lines.append("-" * 20)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    for key, value in metadata.items():
        report_lines.append(f"{key.title()}: {value}")
    report_lines.append("")
    
    # Executive Summary
    if summary:
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 20)
        report_lines.append(summary)
        report_lines.append("")
    
    # Main sections
    for i, section in enumerate(sections, 1):
        heading = section.get('heading', f'Section {i}')
        content = section.get('content', '')
        
        report_lines.append(f"{i}. {heading.upper()}")
        report_lines.append("-" * (len(f"{i}. {heading}") + 5))
        report_lines.append(content)
        report_lines.append("")
    
    # Recommendations
    if recommendations:
        report_lines.append("KEY RECOMMENDATIONS")
        report_lines.append("-" * 20)
        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"{i}. {rec}")
        report_lines.append("")
    
    # Footer
    report_lines.append("=" * 80)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)


@tool
def format_data_for_report(data: Dict[str, Any], data_type: str = "general") -> Dict[str, Any]:
    """
    Format raw data into a structure suitable for report generation.
    
    Args:
        data: Raw data dictionary
        data_type: Type of data being formatted (research, analysis, etc.)
    
    Returns:
        Formatted data structure for use in reports
    """
    formatted_data = {
        "data_type": data_type,
        "timestamp": datetime.now().isoformat(),
        "processed_data": {}
    }
    
    # Process different types of data
    if data_type == "research":
        formatted_data["processed_data"] = {
            "findings": data.get("findings", []),
            "sources": data.get("sources", []),
            "key_points": data.get("key_points", []),
            "methodology": data.get("methodology", "")
        }
    elif data_type == "analysis":
        formatted_data["processed_data"] = {
            "results": data.get("results", {}),
            "insights": data.get("insights", []),
            "metrics": data.get("metrics", {}),
            "conclusions": data.get("conclusions", [])
        }
    else:
        # General formatting
        formatted_data["processed_data"] = data
    
    return formatted_data

TOOLS: List[Callable[..., Any]] = [report_generation_tool, format_data_for_report]