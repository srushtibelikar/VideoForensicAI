import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


def _table(data, widths=None):
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def generate_report(result, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    document = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=15 * mm, leftMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
    )
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("VideoForensic AI - Forensic Analysis Report", styles["Title"]),
        Paragraph("Automated video evidence examination", styles["Heading2"]),
        Spacer(1, 10),
    ]

    metadata = result["metadata"]
    data = [["Property", "Value"],
            ["Filename", metadata["filename"]],
            ["File size", f"{metadata['file_size_mb']} MB"],
            ["Resolution", metadata["resolution"]],
            ["FPS", metadata["fps"]],
            ["Frame count", metadata["frame_count"]],
            ["Duration", f"{metadata['duration_seconds']} sec"],
            ["Container", metadata["container"]],
            ["Video codec", metadata["codec"]],
            ["Pixel format", metadata["pixel_format"]],
            ["Creation time", metadata["creation_time"]],
            ["SHA-256", result["sha256"]],
            ["Risk score", f"{result['risk_score']}/100"],
            ["Classification", result["classification"]]]
    elements.append(_table(data, [55 * mm, 125 * mm]))
    elements.append(Spacer(1, 12))

    frame = result["frame_analysis"]
    elements.append(Paragraph("Frame-Level Analysis", styles["Heading2"]))
    frame_data = [["Metric", "Value"],
                  ["Sampled frames", frame["sample_count"]],
                  ["Average frame difference", frame["average_frame_difference"]],
                  ["Repeated/near-identical transitions", frame["duplicate_frame_count"]],
                  ["Abrupt-change transitions", len(frame["high_change_frames"])],
                  ["Low-blur-score frames", len(frame["blur_frames"])],
                  ["Suspicious segments", len(frame["suspicious_segments"])],
                  ["Evidence frames saved", len(frame["evidence_frames"])]]
    elements.append(_table(frame_data, [90 * mm, 90 * mm]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Suspicious Segments", styles["Heading2"]))
    segments = frame["suspicious_segments"]
    if segments:
        segment_data = [["Start (s)", "End (s)", "Start frame", "End frame", "Reason"]]
        segment_data += [[s["start_seconds"], s["end_seconds"], s["start_frame"], s["end_frame"], s["reason"]] for s in segments[:50]]
        elements.append(_table(segment_data, [25 * mm, 25 * mm, 28 * mm, 28 * mm, 64 * mm]))
    else:
        elements.append(Paragraph("No suspicious segments were identified by the configured heuristics.", styles["BodyText"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Audio Analysis", styles["Heading2"]))
    audio = result["audio_analysis"]
    audio_data = [["Property", "Value"], ["Status", audio.get("status", "Unknown")], ["Stream count", audio.get("stream_count", 0)]]
    for index, stream in enumerate(audio.get("streams", [])[:10], 1):
        audio_data.append([f"Stream {index}", f"{stream.get('codec_name', 'Unknown')}, {stream.get('sample_rate', 'n/a')} Hz, {stream.get('channels', 'n/a')} channel(s)"])
    elements.append(_table(audio_data, [55 * mm, 125 * mm]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Tampering Detection Indicators", styles["Heading2"]))
    tampering = result["tampering_detection"]
    indicator_data = [["Type", "Severity", "Observation"]]
    for indicator in tampering.get("indicators", []):
        indicator_data.append([indicator["type"], indicator["severity"], indicator["message"]])
    if len(indicator_data) == 1:
        indicator_data.append(["None", "Info", "No configured automated indicator was triggered."])
    elements.append(_table(indicator_data, [35 * mm, 25 * mm, 120 * mm]))

    elements.append(PageBreak())
    elements.append(Paragraph("Evidence Frames", styles["Heading2"]))
    evidence = frame["evidence_frames"]
    if evidence:
        evidence_data = [["Frame", "Timestamp", "Reason", "Difference", "File"]]
        evidence_data += [[e["frame_number"], e["timestamp_seconds"], e["reason"], e["difference"], e["filename"]] for e in evidence[:100]]
        elements.append(_table(evidence_data, [22 * mm, 27 * mm, 32 * mm, 25 * mm, 64 * mm]))
    else:
        elements.append(Paragraph("No evidence frames were generated.", styles["BodyText"]))

    elements.append(Spacer(1, 18))
    elements.append(Paragraph(
        "Forensic note: This report records automated indicators generated by the current software. It does not establish authenticity, authorship, intent, or legal conclusions. Findings should be corroborated with the original evidence, chain-of-custody records, validated forensic tools, and expert examination.",
        styles["BodyText"]
    ))
    document.build(elements)
    return output_path
